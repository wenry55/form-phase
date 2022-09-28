from ast import arg
from re import S
from time import sleep
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

import plotly.express as px
import numpy as np
import os
import pandas as pd
import json
from dash.dash_table import DataTable 
from queue import Queue
from flask_caching import Cache

dfi = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')


def add_features(df):
    df['hour'] = df['ds'].apply(lambda x: int(x.split(':')[0]))
    df['min'] = df['ds'].apply(lambda x: int(x.split(':')[1]))
    df['series'] = np.arange(1, len(df) + 1)
    # q_diff는 필요하지 않아보임. 현재까지의 누적량이 영향을 미침.
    # df['q_diff'] = df['q_val'] - df['q_val'].shift(1)
    df.drop(['ds'], axis=1, inplace=True)
    return df


df_all = pd.read_csv('all_st_ch.csv')
print('data loaded')
dfi = df_all[(df_all['stage'] == 'T01730') & (df_all['channel'] == 1)]
dfa = dfi[['vol']].copy()
dfa['record'] = dfi['vol'][:1]

fig = px.line(dfa)
fig.add_vline(x=0, line_dash='dash')
fig.update_layout(transition_duration=500, 
# xaxis=dict(
#     rangeslider=dict(visible=True) 
# )
) 

def generate_table(dataframe, index, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(index, index+max_rows)
        ])
    ])

df_per_stage = df_all[(df_all['stage'] == 'T01730') & (df_all['channel'] == 1)]


fig2 = px.line(x=df_per_stage['series'], y=df_per_stage['vol'])



target_columns = ['series', 'q_val', 'curr', 'vol']
app = Dash(__name__)

cache = Cache(app.server, config={
    # 'CACHE_TYPE': 'redis',
    # Note that filesystem cache doesn't work on systems with ephemeral
    # filesystems like Heroku.
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',

    # should be equal to maximum number of users on the app at a single time
    # higher numbers will store more data in the filesystem / redis cache
    'CACHE_THRESHOLD': 200
})


app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(id='graph-with-slider', figure=fig),
        ], style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
            DataTable(
            id='table',
            data=dfi.iloc[0:10][['series', 'q_val', 'curr', 'vol']].to_dict('records'), columns=[{"name": i, "id": i} for i in target_columns]

        )

           
        ], style={'width': '49%', 'display': 'inline-block', 'float':'right'}),
    ]),
    html.Div([
    ]),
    # dcc.Graph(id='graph-with-slider'),
    # dcc.Graph(id='graph-with-slider', figure=fig),
    # dcc.Slider(
    #     0,
    #     len(df_list[0]['data']),
    #     step=None,
    #     value=0,
    #     id='year-slider'
    # ),
    dcc.Interval(
        id='interval-component',
        interval=500
    ),

    html.Div([
        dcc.Graph(id='x1', figure=fig2)
    ]),
    html.Div(id='my-output'),
    html.Div(id='my-output2'),
    html.Div([
        html.Button('Request', id='req', n_clicks=0),
    ]),
    html.Div([
        html.Button('Request #2', id='req2', n_clicks=0),
    ]),
    html.Div(id='c1'),
    html.Div(id='c2'),
    html.Div(id='c3'),
    dcc.Store(id='signal')

])

@app.callback(
    Output('signal', 'data'),
    Input('req2', 'n_clicks')
)
def put_and_alarm(value):
    return value

@app.callback(
    Output('c1', 'children'),
    Input('signal', 'data')
)
def notified_and_render(value):
    return value

@app.callback(
    Output('c2', 'children'),
    Input('signal', 'data')
)
def notified_and_render2(value):
    return value

@app.callback(
    Output('my-output2', 'children'),
    Input('req', 'n_clicks')
)
def request_load(n_clicks):
    print(n_clicks)
    stages['1']['1'].put('data from button')
    pass

rg = None
@app.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='graph-with-slider', component_property='relayoutData')
)
def displayx(layoutData):
    rg = layoutData
    return json.dumps(layoutData, indent=2)

@app.callback(
    # Output(component_id='my-output', component_property='children'),
    Output(component_id='graph-with-slider', component_property='figure'),
    Output(component_id='table', component_property='data'),
    Input(component_id='my-output', component_property='children'),
    Input(component_id='graph-with-slider', component_property='clickData')
)
def display_click_data(range, clickData):
    print(clickData)
    rg = json.loads(range)

    if clickData is None:
        val = 1
    else:
        val = clickData['points'][0]['x']
    
    dfa = dfi[['vol']].copy()
    dfa['record'] = dfi['vol'][:val]

    fig = px.line(dfa)
    fig.add_vline(x=val, line_dash='dash')
    if rg is None or "xaxis.autorange" in rg or "autosize" in rg:
        fig.update_layout(transition_duration=500, 
                #xaxis=dict(rangeslider=dict(visible=True)),
    ) 
        pass
    else:
        fig.update_layout(transition_duration=500, 
                # xaxis=dict(rangeslider=dict(visible=True)),
                xaxis_range=[rg['xaxis.range[0]'],rg['xaxis.range[1]']]) 

    data = dfi.iloc[val:val+10][target_columns].to_dict('records')
    return fig, data
    # return json.dumps(clickData, indent=2)

# @app.callback(
#     Output('graph-with-slider', 'figure'),
#     Input('year-slider', 'value'),
# )
# def update_on_slider(val):
#     dfa = dfi[['vol']].copy()
#     dfa['record'] = dfi['vol'][:val]

#     fig = px.line(dfa)
#     fig.add_vline(x=val, line_dash='dash')
#     fig.update_layout(transition_duration=500, 
#     xaxis=dict(
#         rangeslider=dict(visible=True) 

#     )) 

#     return fig

# @app.callback(
#     Output('year-slider', 'value'),
#     Input('interval-component', 'n_intervals')
#     )
# def update_metrics(n):
#     return n


# @app.callback(
#     Output('graph-with-slider', 'figure'),
#     Input('interval-component', 'n_intervals')
#     #Input('year-slider', 'value'))
# )
# def update_figure(n):

#     dfa = dfi[['vol']].copy()
#     dfa['record'] = dfi['vol'][:n*10]

#     fig = px.line(dfa)
#     fig.add_vline(x=n*10, line_dash='dash')
#     fig.update_layout(transition_duration=500)
#     # fig.update_layout()

#     return fig

from threading import Thread

_sentinel = object()

def producer(out_q):
    print('thread started')
    while True:
        sleep(1)
        out_q.put('xx')

def comsumer(in_q):
    while True:
        data = in_q.get()
        print(data)
        sleep(3)
        in_q.task_done()


# stage states
IN_CHARGE = 1
NOOP = 2
class Channel(object):
    voltage = 0
    current = 0
    state = []
    def __init__(self, channel_id) -> None:
        self.channel_id = channel_id
        self.vol = 0
        self.curr = 0
        self.pv = 0
        self.elapsed = '0000:00:00'
        self.q_val = 0

    def put(self):
        pass

    def get_vol(self):
        pass

    def get_expected(self):
        pass

   
class Stage(object):

    num_thermal = 12
    num_channels = 56
    num_lanes = 6

    def __init__(self, parent_lane, stage_id) -> None:
        self.lane_id = parent_lane
        self.stage_id = stage_id
        self.state = NOOP
        self.channels = [Channel(i) for i in range(1, 57)] # 1~56
        self.temperatures = [np.nan for i in range(13)] # 1~12

        self.queue = Queue()

    def get_state(self):
        return self.state
    
    def task(self):
        while True:
            data = self.queue.get()
            print(f'Reporting {self.lane_id},{self.stage_id} : {self.state}, {data}')
        
    def put(self, data):
        self.queue.put(data)





stages = {}

if __name__ == '__main__':

    # q = Queue()
    # t1 = Thread(target=producer, args=(q,))
    # t2 = Thread(target=comsumer, args=(q,))
    # t1.start()
    # t2.start()

    for lane_id in range(1, 7):
        stages[str(lane_id)] = {}
        for stage_id in range(1, 49):
            s = Stage(lane_id, stage_id)
            stages[str(lane_id)][str(stage_id)] = s
            t = Thread(target=s.task)
            t.start()
            
    for lane_id in stages.keys():
        for stage_id in stages[lane_id].keys():
            s = stages[lane_id][stage_id]
            s.put(f'hello {lane_id}, {stage_id}')



 
    app.run_server(debug=True)

