import json
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from matplotlib import cm


def create_rgb(score: float):
    """0: red (255, 0, 0), 0.5: yellow (255, 255, 0), 1.0: green (0, 255, 0)"""
    color_map = cm.get_cmap('YlGnBu', 8)
    r, g, b, _ = [c*255 for c in color_map(1 - score)]
    # print(score, abs(score - 0.5))
    # if score < 0.5:
    #     r = 255
    #     g = 255 * (2 * score)
    # else:
    #     r = 255 * (2 - 2 * score)
    #     g = 255
    return 'rgb(' + str(r) + ', ' + str(g) + ', ' + str(b) + ', 0.8)'


with open('./matyasj_newB.json', 'r') as file:
    tree = json.load(file)

id_map = {}
fen_map = {}
for idx, node in enumerate(tree['nodes']):
    id_map[idx] = node[4]
    fen_map[node[4]] = idx


# NODES
labels = [node[0] for node in tree['nodes']]
colors = [create_rgb(node[3]) for node in tree['nodes']]


# EDGES
source = [fen_map[edge[0]] for edge in tree['edges']]
target = [fen_map[edge[1]] for edge in tree['edges']]
value = [edge[2] for edge in tree['edges']]
edge_color = [create_rgb(tree['nodes'][fen_map[edge[1]]][3]) for edge in tree['edges']]
edge_label = ['' for edge in tree['edges']]


app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id="graph", style={'width': '200vh', 'height': '300vh'}),
    html.P("Opacity"),
    dcc.Slider(id='opacity', min=0, max=1,
               value=0.5, step=0.1)
])


@app.callback(
    Output("graph", "figure"),
    [Input("opacity", "value")])
def display_sankey(opacity):
    opacity = str(opacity)
    # override gray link colors with 'source' colors
    node = {
        "pad": 15,
        "thickness": 15,
        "line": {
            "color": "black",
            "width": 0.5
        },
        "label": labels,
        "color": colors,
    }
    link = {
        "source": source,
        "target": target,
        "value": value,
        "color": edge_color,
        "label": edge_label
    }
    # Change opacity
    node['color'] = [
        'rgba(255,0,255,{})'.format(opacity)
        if c == "magenta" else c.replace('0.8', opacity)
        for c in node['color']]
    link['color'] = [
        node['color'][src] for src in link['source']]
    fig = go.Figure(go.Sankey(link=link, node=node))
    fig.update_layout(font_size=10)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
