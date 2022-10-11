import dash
from dash import html, dcc, Output, Input, callback
from formation import *
import plotly.express as px
import plotly.graph_objects as go
import xgboost as xgb
from plotly.subplots import make_subplots

dash.register_page(__name__)


def layout(stage_id=None, channel_id=None, **others):

    return html.Div(children=[
        html.H1(children='This is stage'),
        html.Div(children=f'''
            Params : Stage: {stage_id}
        '''),
        html.Div(id='div2'),
        html.Button('start', id='start', n_clicks=0),
        html.Button('Play', id='play', n_clicks=0),
        dcc.Input(id='my_input', value='initial value', type='text'),
        dcc.Dropdown(options=['11', '22', '33'], value='33'),
        dcc.Graph(id='stage-1'),
        dcc.Graph(id='t-1'),
        dcc.Graph(id='p-1'),

        html.Div(id='div_start'),
    ])

@callback(
    Output('div_start', 'children'),
    Input('start', 'n_clicks')
)
def funx(n_clicks):
    if n_clicks == 0:
        print('init =-> ', n_clicks)
        return
    print('funx', n_clicks)
    stage = stages['1']['1']
    stage.start(1000)


@callback(
Output('stage-1', 'figure'), 
Output('t-1', 'figure'),
Output('p-1', 'figure'), 
          # Input('my_input', component_property='value'))
          Input('play', 'n_clicks'))
def dotest(n_clicks):
    lane_id = '1'
    stage_id = '1'
    s = stages[lane_id][stage_id]
    s.put(f'hello {lane_id}, {stage_id}')
    print(s.data)
    print(n_clicks)
    # d = s.data[s.data['channel'] == 1]

    # d = s.data

    # dfa = d[['vol']].copy()

    # for i in range(1, 49):
    #     d = s.data[s.data['channel'] == i]
    #     fig = px.add_scatter(x='series', y='vol')

    # d = s.data.query('channel < 3')
    d = s.data
    fig = px.line(d, x='series', y='vol', color='channel')

    fig.update_layout(transition_duration=500,
                      # xaxis=dict(
                      #     rangeslider=dict(visible=True)
                      # )
                      )

    df_t = df_tempers.query('stage == "T75979"')
    # df_t = df_tempers
    f2 = px.line(df_t, x='series', y='temperature', color='index')

    df_st = df_tempers.query('stage == "T75979" and index == "10"')
    print(df_st)
    reg = xgb.XGBRegressor()
    reg.load_model(fname='./models/temperature_10.json')
    pred = reg.predict(df_st[['series']])

    print('============================================')
    print(pred)

    # f3 = px.line(x=df_st['series'], y=pred)

    # fig = make_subplots(specs=[[{"secondary_y": True}]])
    f3 = go.Figure()
    f3.add_trace(go.Scatter(x=df_st['series'], y=pred))
    f3.add_trace(go.Scatter(x=df_st['series'], y=df_st['temperature']))

    return fig, f2, f3