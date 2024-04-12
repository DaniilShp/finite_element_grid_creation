import json
from flask import Flask, render_template, request, current_app
import os
from work_with_db import select_dict
from sql_provider import SQLProvider
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
with open('src\dbconfig.json') as f:
    app.config['db_config'] = json.load(f)

app.secret_key = 'you will never guess'
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

def build_grid(element_lists, nodes_coordinates):
    for i in range(len(element_lists)):
        triangle_points_x = [nodes_coordinates[element_lists[i]['n1'] - 1]['x'],
                             nodes_coordinates[element_lists[i]['n2'] - 1]['x'],
                             nodes_coordinates[element_lists[i]['n3'] - 1]['x'],
                             nodes_coordinates[element_lists[i]['n1'] - 1]['x']
                             ]
        triangle_points_y = [nodes_coordinates[element_lists[i]['n1'] - 1]['y'],
                             nodes_coordinates[element_lists[i]['n2'] - 1]['y'],
                             nodes_coordinates[element_lists[i]['n3'] - 1]['y'],
                             nodes_coordinates[element_lists[i]['n1'] - 1]['y']
                             ]
        plt.plot(triangle_points_x, triangle_points_y, 'b-')
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url
@app.route('/', methods=['GET', 'POST'])
def draw_finite_element_grid():
    if request.method == 'GET':
        return render_template("draw_finite_element_grid.html", method_GET = 1)
    else:
        _sql = provider.get('get_nodes_coordinates.sql')
        nodes_coordinates_dict = select_dict(current_app.config['db_config'], _sql)
        _sql = provider.get('get_element_lists.sql')
        element_lists = select_dict(current_app.config['db_config'], _sql)
        img = build_grid(element_lists, nodes_coordinates_dict)
        return render_template("draw_finite_element_grid.html", method_GET = 0, plot = img)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)