from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
import os
import pandas as pd

dfi = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')


def add_features(df):
    df['hour'] = df['ds'].apply(lambda x: int(x.split(':')[0]))
    df['min'] = df['ds'].apply(lambda x: int(x.split(':')[1]))
    df['series'] = np.arange(1, len(df) + 1)
    # q_diff는 필요하지 않아보임. 현재까지의 누적량이 영향을 미침.
    # df['q_diff'] = df['q_val'] - df['q_val'].shift(1)
    df.drop(['ds'], axis=1, inplace=True)
    return df

df_list = []
file_list = os.listdir('./data')
for file in file_list:
    df = pd.read_csv(f'./data/{file}', encoding='euc-kr')
    stage = file.split('_')[0]
    for i in range(1, 57):
        # _sc => stage_channel
        df_sc = df[['시간', f'ch{i} 전압', f'ch{i} 전류', f'ch{i} 용량', f'ch{i} PV']]
        df_sc = df_sc.rename(columns={'시간':'ds', f'ch{i} 전압': 'vol', f'ch{i} 전류': 'curr', f'ch{i} 용량': 'q_val',  f'ch{i} PV': 'pv'})
        df_sc.drop(['pv'], axis=1, inplace=True)
        df_sc = add_features(df_sc)
        df_list.append({'stage': stage, 'ch': i, 'data': df_sc})
    print(f'Stage : {stage} loaded.')
    break
dfi = df_list[0]['data']

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        0,
        len(df_list[0]['data']),
        step=None,
        value=0,
        id='year-slider'
    ),
    dcc.Interval(
        id='interval-component',
        interval=500
    )
])




@app.callback(
    Output('year-slider', 'value'),
    Input('interval-component', 'n_intervals')
    )
def update_metrics(n):
    return n


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('interval-component', 'n_intervals')
    #Input('year-slider', 'value'))
)
def update_figure(n):

    dfa = dfi[['vol']].copy()
    dfa['record'] = dfi['vol'][:n*10]

    fig = px.line(dfa)
    fig.add_vline(x=n*10, line_dash='dash')
    fig.update_layout(transition_duration=500)
    # fig.update_layout()

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)