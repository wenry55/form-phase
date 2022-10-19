from gc import callbacks
import dash
from dash import html, dcc, html, Input, Output, State, callback
from formation import *
import plotly.express as px
import plotly.graph_objects as go
from random import randint
import json

dash.register_page(__name__, path='/')

# 6 lanes, 48 stages each.

layout = html.Div(children=[
    html.H1(children='Home'),
    html.Div(children=f'''
        This is home.
        Put you content here.
        {len(stages)}
    '''),
    html.Div(id='div1'),
    html.Div(id='div2'),
    html.Div(id='heatmap_div', children=[
        dcc.Graph(id='h1'),
    ]),

    dcc.Location(id='location'),
    dcc.Interval(id='stage_interval', interval=5000),
    html.Div(id='none')
])

def discrete_colorscale(bvals, colors):
    """
    bvals - list of values bounding intervals/ranges of interest
    colors - list of rgb or hex colorcodes for values in [bvals[k], bvals[k+1]],0<=k < len(bvals)-1
    returns the plotly  discrete colorscale
    """
    if len(bvals) != len(colors)+1:
        raise ValueError('len(boundary values) should be equal to  len(colors)+1')
    bvals = sorted(bvals)     
    nvals = [(v-bvals[0])/(bvals[-1]-bvals[0]) for v in bvals]  #normalized values
    
    dcolorscale = [] #discrete colorscale
    for k in range(len(colors)):
        dcolorscale.extend([[nvals[k], colors[k]], [nvals[k+1], colors[k]]])
    return dcolorscale    

bvals = [0,1000, 8000, 13000, 15000, 18000,18001]
colors = ['#777777', '#09ffff', '#19d3f3', '#e763fa' , '#ab63fa', '#ff0000']
dcolorsc = discrete_colorscale(bvals, colors)
tickvals = [np.mean(bvals[k:k+2]) for k in range(len(bvals)-1)] #position with respect to bvals where ticktext is displayed
ticktext = [f'<{bvals[1]}'] + [f'{bvals[k]}-{bvals[k+1]}' for k in range(1, len(bvals)-2)]+[f'>{bvals[-2]}']


@callback(
    Output('h1', 'figure'), 
    # Input('div1', 'children')
    Input('stage_interval', 'n_intervals')
    )
def draw_heatmap(n_interval):

    data = [[randint(0, 18000) for i in range(48)] for j in range(6)]
    df = pd.DataFrame(data)

    #z = [[randint(1,20000) for i in range(1, 49)] for j in range(6)]
    # z[-2][10] = 20001
    z = []
    for lane_id in range(6, 0, -1):
        stage_list = []
        for stage_id in range(1, 49):
            s = stages[str(lane_id)][str(stage_id)] 
            step = s.current_step
            if lane_id == 6 and stage_id == 48:
                step = 20001
            stage_list.append(step)

        z.append(stage_list)

    go_heatmap =go.Heatmap(
        z = z,
        x = [str(i) for i in range(1,49)],
        y = [f'Lane {i} ' for i in range(6, 0, -1)],
        # aspect="auto",
        # text_auto=True,
        ygap=10,
        xgap=1,
        colorscale = dcolorsc, 
        colorbar = dict(thickness=25, tickvals=tickvals, ticktext=ticktext)
    )

    # fig = px.imshow(df, aspect="auto", text_auto=True, ygap=10,
    # x = [str(i) for i in range(1,49)],
    # y = ['Lane 1', 'Lane 2', 'Lane 3', 'Lane 4', 'Lane 5', 'Lane 6']
    # )
    # go_heatmap.on_click(update_point)

    fig = go.FigureWidget([go_heatmap])
    return fig

@callback(
    Output('location', 'href'), 
    Input('h1', 'clickData')
    )
def display_click(clickData):
    # stage_index = clickData.points[0].x
    # lane_index = clickData.points[0].y

    if clickData is not None:
        # print('click=>', clickData, clickData['points'][0]['x'], clickData['points'][0]['y'])
        stage_id = clickData['points'][0]['x']
        lane_id = clickData['points'][0]['y'].replace('Lane', '').strip()
        print(int(stage_id), int(lane_id.replace('Lane', '').strip()))
        return f'/stage?lane_id={lane_id}&stage_id={stage_id}'



# @callback(
#     Output('location', 'pathname'),
#     Input('div2', 'children')
# )
# def change_url(params):

#     # print(params)
#     if params != 'null':
#         return '/stage'
#     pass
    
# @callback(
#     Output('none', 'children'),
#     Input('stage_interval', 'n_intervals')
# )
# def update_map(n_intervals):
#     print('up', n_intervals)
#     return 'none!'