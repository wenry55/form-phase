from cProfile import label
import dash
from dash import html, dcc, callback, Input, Output
from formation import *
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xgboost as xgb

# dash.register_page(__name__)


def layout(stage_id=None, channel_id=None, **others):

    return html.Div(children=[
        html.H1(children='This is channel'),
        html.Div(children=f'''
            Params : Stage: {stage_id}, Channel: {channel_id}
        '''),
        html.Button('Channel', id='reqChannel', n_clicks=0),
        html.Div(id='out_channel', children=[
            dcc.Graph(id='channel_vol'),
        ])
    ])


FEATURES = ['curr', 'q_val', 'hour', 'min', 'series']


@callback(Output('channel_vol', 'figure'), Input('reqChannel', 'n_clicks'))
def show_channel(n_clicks):
    stage = stages['1']['1']
    stage_df = stage.data
    channel_df = stage_df.query("channel == 3")
    stage.current_step = 1000
    current_df = channel_df.iloc[0:stage.current_step]
    print('step', stage.current_step, current_df)
    # fig = go.Figure()
    reg = xgb.XGBRegressor()
    reg.load_model(fname=f'./models/channel_3.json')
    pred = reg.predict(channel_df[FEATURES])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=channel_df['series'], y=channel_df['vol'], name='Previous' ),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=channel_df['series'], y=pred, name='Expected'))
    fig.add_trace(go.Scatter(x=channel_df['series'], y=channel_df['curr'], name='Current'),
                  secondary_y=True)

    fig.add_trace(go.Scatter(x=current_df['series'], y=current_df['vol'], 
        mode='lines',
        line=dict(color='firebrick', width=3),
        name='In progress'), secondary_y=False )
    fig.add_trace(go.Scatter(x=[stage.current_step], y=[current_df.iloc[-1]['vol']], mode='markers', 
        name='Last step',
        marker=dict(
            color='red',
            size=7

    )), secondary_y=False)
    fig.update_layout(transition_duration=500)

    # fig_curr = px.line(channel_df, x='series', y='curr')
    # fig_curr.update_layout(transition_duration=500)

    return fig  # , fig_curr


# @callback(Output('channel_vol', 'figure'), Output('channel_curr', 'figure'),
#           Input('reqChannel', 'n_clicks'))
# def show_channel(n_clicks):
#     stage_df = stages['1']['1'].data
#     channel_df = stage_df.query("channel == 1")
#     print(channel_df)
#     fig = px.line(channel_df, x='series', y='vol')
#     fig.add_trace(channel_df, x='series', y='curr')
#     fig.update_layout(transition_duration=500)

#     fig_curr = px.line(channel_df, x='series', y='curr')
#     fig_curr.update_layout(transition_duration=500)

#     return fig, fig_curr
