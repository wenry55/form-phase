from gc import callbacks
import dash
from dash import html, dcc, html, Input, Output, State, callback
from formation import *
import plotly.express as px
from random import randint

dash.register_page(__name__, path='/')

# 6 lanes, 48 stages each.

layout = html.Div(children=[
    html.H1(children='Home'),
    html.Div(children=f'''
        This is home.
        Put you content here.
        {len(stages)}
    '''),
    html.Button('Req', id='pb', n_clicks=0),
    html.Div(id='div1'),
    html.Div(id='heatmap_div', children=[
        dcc.Graph(id='h1'),

    ]),

    dcc.Checklist(
        id='medals',
        options=["gold", "silver", "bronze"],
        value=["gold", "silver"],
    ),    
])

@callback(
    Output('h1', 'figure'), 
    Input('medals', 'value')
    )
def draw_heatmap(cols):

    data = [[randint(0, 18000) for i in range(48)] for j in range(6)]
    df = pd.DataFrame(data)
    fig = px.imshow(df, aspect="auto", text_auto=True,
    x = [str(i) for i in range(1,49)],
    y = ['Lane 1', 'Lane 2', 'Lane 3', 'Lane 4', 'Lane 5', 'Lane 6']
    )
    return fig

@callback(Output('div1', 'children'), Input('pb', 'n_clicks'))
def dotest(n_clicks):
    lane_id = '1'
    stage_id = '1'
    s = stages[lane_id][stage_id]
    s.put(f'hello {lane_id}, {stage_id}')
    return 'Val'
