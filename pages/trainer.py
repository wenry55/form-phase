import dash
from dash import html, dcc, Output, Input, callback
from formation import *
import plotly.express as px

# dash.register_page(__name__)


def layout(stage_id=None, channel_id=None, **others):

    return html.Div(children=[
        html.H1(children='This is trainer'),
        html.Div(children=f'''
            Params : Stage: {stage_id}, Channel: {channel_id}
        '''),
        html.Button('Train Channel', id='train_channel', n_clicks=0),
        html.Button('Train Temperature', id='train_termperature', n_clicks=0),
        html.Div(id='train_result')
    ])


FEATURES = ['curr', 'q_val', 'hour', 'min', 'series']
TARGET = 'vol'


@callback(
    Output('train_result', 'children'),
    Input('train_channel', 'n_clicks'),
)
def train_channel(tn):

    for i in range(1, 57):
        df_channel = df_all.query("channel == @i")
        print(df_channel)

    return ''
