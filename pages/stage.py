from enum import auto
import dash
from dash import html, dcc, Output, Input, State, callback
from idna import check_nfc
from numpy import show_config
from formation import *
import plotly.express as px
import plotly.graph_objects as go
import xgboost as xgb
from plotly.subplots import make_subplots
from flask import request

dash.register_page(__name__)

selected_channels = []

@callback(
    Output('chks', 'value'),
    Input('location', 'search')
)
def change_selected(search):
    print('search=>', f"xx{search}yy")
    if search != '':
        lane_id = search.split('&')[0].split('=')[1]
        stage_id = search.split('&')[1].split('=')[1]
        print('searching lane, stage', lane_id, stage_id)
        if lane_id == '6' and stage_id == '48':
            return ['29']
        else:
            return []

def layout(stage_id=None, channel_id=None, **others):
    
    channels = [str(i) for i in range(1, 57)]

    return html.Div(

        style={'height':'100vh'},
        children=[
            html.Div(children=[
            html.Label('Channels'),
            dcc.Checklist(channels, [], inline=True, id='chks')
            ]),
        html.Button('start', id='start', n_clicks=0),
        html.Button('Play', id='play', n_clicks=0),
        dcc.Input(id='my_input', value='initial value', type='text'),
        # dcc.Graph(id='c-1',config={'displayModeBar': False}),

        dcc.Graph(id='t-1'),

        html.Div(id='div_start'),
        html.Div(id='div_start2'),
        dcc.Interval(id='update_interval', interval=5000),
        dcc.Location(id='location'),

        html.Div(id='none', style={'display':'none'})
    ])

# @callback(
#     Output('div_start', 'children'),
#     Input('start', 'n_clicks'),
# )
# def funx(n_clicks):
#     if n_clicks == 0:
#         print('init =-> ', n_clicks)
#         return
#     print('funx', n_clicks)
#     stage = stages['1']['1']
#     stage.start(1000)

# @callback(
#     Output('c-1', 'figure'),
#     Input('start', 'n_clicks')
# )
# def draw_he(v):
#     go_heatmap =go.Heatmap(
#         z = [[i for i in range(1,57)]],
#         x = [str(i) for i in range(1,57)],
#         y = [f'Lane {i} ' for i in range(1, 0, -1)],
#         # aspect="auto",
#         # text_auto=True,
#         ygap=10,
#         xgap=1,
#         showlegend=False,
        
        
#     )
#     # fs = make_subplots()
#     # fs.add_traces([go_line, go_heatmap])
#     fs = go.Figure([go_heatmap])
#     fs.update_traces(showscale=False)
#     fs.update_layout(autosize=False, height=200, width=1200)
#     # fs.show(config=dict(displayModeBar=False))


#     return fs

@callback(
    # Output('stage-1', 'figure'), 
    Output('t-1', 'figure'),
    # Output('p-1', 'figure'), 
    Input('play', 'n_clicks'),
    Input('chks', 'value'),
    Input('update_interval', 'n_intervals'),
    Input('location', 'search')

    
    )
def dotest(n_clicks, value, interval, search):
    print(value, search)
    lane_id = search.split('&')[0].split('=')[1]
    stage_id = search.split('&')[1].split('=')[1]
    s = stages[lane_id][stage_id]
    s.put(f'hello {lane_id}, {stage_id}')
    # print(s.data)
    # print(n_clicks)
    # d = s.data[s.data['channel'] == 1]

    # d = s.data

    # dfa = d[['vol']].copy()

    # for i in range(1, 49):
    #     d = s.data[s.data['channel'] == i]
    #     fig = px.add_scatter(x='series', y='vol')

    # d = s.data.query('channel < 3')
    
    # c for predicted line
    c = s.data
    d = stages['1']['1'].data

    # fig = px.line(d, x='series', y='vol', color='channel')
    # fig.update_layout(transition_duration=500,
    #                   xaxis=dict(
    #                       rangeslider=dict(visible=True)
    #                   )
    #                   )

    df_t = df_tempers.query('stage == "T75979"')
    # df_t = df_tempers
    vol_x = list(d[['series']].groupby('series').groups.keys())
    vol_x_rev = vol_x[::-1]
    vol_max_y = d[['series', 'vol']].groupby('series').max()['vol'].tolist()
    vol_min_y = d[['series', 'vol']].groupby('series').min()['vol'].tolist()
    curr_max_y = d[['series', 'curr']].groupby('series').max()['curr'].tolist()
    curr_min_y = d[['series', 'curr']].groupby('series').min()['curr'].tolist()


    x_steps = c['series'].tolist()
    y_vol = c['vol'].tolist()
    y_curr = c['curr'].tolist()



   # f2 = px.line(df_t, x='series', y='temperature', color='index')
    f2 = make_subplots(specs=[[{"secondary_y": True}]])

    f2.add_trace(go.Scatter(
        x = vol_x + vol_x_rev,
        y = vol_max_y + vol_min_y[::-1],
        fill='toself',
        fillcolor='rgba(231,107,243,0.2)',
        line_color='rgba(255,255,255,0)',
        showlegend=True,
        name='Voltage Range'
    ), secondary_y=False)

    f2.add_trace(go.Scatter(
        x = vol_x,
        y = vol_max_y,
        line_color='rgba(231,107,243,0.5)',
        showlegend=True,
        name='Voltage Max'
    ), secondary_y=False)

    f2.add_trace(go.Scatter(
        x = vol_x,
        y = vol_min_y,
        line_color='rgba(231,107,243,0.5)',
        showlegend=True,
        name='Voltage Min'
    ), secondary_y=False)

    f2.add_trace(go.Scatter(
        x = vol_x + vol_x_rev,
        y = curr_max_y + curr_min_y[::-1],
        fill='toself',
        fillcolor='rgba(170,176,200,0.7)',
        line_color='rgba(255,255,255,0)',
        showlegend=True,
        name='Current Range'
    ), secondary_y=True)

    f2.add_trace(go.Scatter(
        x = vol_x,
        y = curr_max_y,
        line_color='rgba(170,176,200,0.5)',
        showlegend=True,
        name='Current Max'
    ), secondary_y=True)

    f2.add_trace(go.Scatter(
        x = vol_x,
        y = curr_min_y,
        line_color='rgba(170,176,200,0.5)',
        showlegend=True,
        name='Current Min'
    ), secondary_y=True)

    for channel_num in value:
        channel_data = c.query(f'channel == {int(channel_num)}')
        channel_vol = channel_data['vol'].tolist()
        channel_curr = channel_data['curr'].tolist()
        channel_series = channel_data['series'].tolist()
    
        f2.add_trace(go.Scatter(
            x = channel_series[:s.current_step],
            y = channel_vol[:s.current_step],
            # line_color='rgba(170,176,200,0.5)',
            showlegend=True,
            name=f'Voltage {channel_num}'
        ), secondary_y=False)

        f2.add_trace(go.Scatter(
            x = channel_series[:s.current_step],
            y = channel_vol[:s.current_step],
            # line_color='rgba(170,176,200,0.5)',
            showlegend=True,
            name=f'Voltage(now) {channel_num}',
        ), secondary_y=False)

        f2.add_trace(go.Scatter(
            x = channel_series[s.current_step:s.current_step+1],
            y = channel_vol[s.current_step:s.current_step+1],
            # line_color='rgba(170,176,200,0.5)',
            showlegend=True,
            name=f'Voltage(now) {channel_num}',
            mode='markers',
            marker=dict(size=7)
        ), secondary_y=False)



        f2.add_trace(go.Scatter(
            x = channel_series[:s.current_step],
            y = channel_curr[:s.current_step],
            # line_color='rgba(170,176,200,0.5)',
            showlegend=True,
            name=f'Current {channel_num} '
        ), secondary_y=True)

        f2.add_trace(go.Scatter(
            x = channel_series[:s.current_step],
            y = channel_curr[:s.current_step],
            # line_color='rgba(170,176,200,0.5)',
            showlegend=True,
            name=f'Current(now) {channel_num}',
        ), secondary_y=True)


        f2.add_trace(go.Scatter(
            x = channel_series[s.current_step:s.current_step+1],
            y = channel_curr[s.current_step:s.current_step+1],
            # line_color='rgba(170,176,200,0.5)',
            showlegend=True,
            name=f'Current(now) {channel_num}',
            mode='markers',
            marker=dict(size=7)
        ), secondary_y=True)



    

    # f2.add_vline(x=s.current_step, line_dash='dash', line_color='green', line_width=3)


    f2.update_layout(height=600)
    # go_heatmap =go.Heatmap(
    #     z = [[i for i in range(1,49)]],
    #     x = [str(i) for i in range(1,49)],
    #     y = [f'Lane {i} ' for i in range(1, 0, -1)],
    #     # aspect="auto",
    #     # text_auto=True,
    #     ygap=10,
    #     xgap=1,
    #     showlegend=False,
    # )

    # df_st = df_tempers.query('stage == "T75979" and index == "10"')

    # reg = xgb.XGBRegressor()
    # reg.load_model(fname='./models/temperature_10.json')
    # pred = reg.predict(df_st[['series']])


    # f3 = go.Figure()
    # f3.add_trace(go.Scatter(x=df_st['series'], y=pred))
    # f3.add_trace(go.Scatter(x=df_st['series'], y=df_st['temperature']))

    # ff = go.Figure([go_heatmap, f2])

    
    return f2 # fig, f2 #, f3

@callback(
    Output('div_start2', 'children'),
    Input('chks', 'value'),
    State('chks', 'value')
)
def ff1(value, vstate):
    print(value)
    print(vstate)