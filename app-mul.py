# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import os
import numpy as np
from random import randint
import matplotlib.pyplot as plt

import xgboost as xgb
from sklearn.metrics import mean_squared_error

import seaborn as sns

color_pal = sns.color_palette()
plt.style.use('fivethirtyeight')


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
        df_sc = df_sc.rename(
            columns={
                '시간': 'ds',
                f'ch{i} 전압': 'vol',
                f'ch{i} 전류': 'curr',
                f'ch{i} 용량': 'q_val',
                f'ch{i} PV': 'pv'
            })
        df_sc.drop(['pv'], axis=1, inplace=True)
        df_sc = add_features(df_sc)
        df_list.append({'stage': stage, 'ch': i, 'data': df_sc})
    print(f'Stage : {stage} loaded.')

FEATURES = ['curr', 'q_val', 'hour', 'min', 'series']
TARGET = 'vol'

from random import randint

draw_list = [randint(0, len(df_list)) for i in range(8)]
print(f'Following data will be used for train and validation, {draw_list}')

df_train = pd.concat([df_list[i]['data'] for i in draw_list[:-1]])
df_test = pd.concat([df_list[i]['data'] for i in draw_list[-1:]])

X_train = df_train[FEATURES]
y_train = df_train[TARGET]
X_test = df_test[FEATURES]
y_test = df_test[TARGET]

reg = xgb.XGBRegressor(booster='gbtree',
                       n_estimators=3000,
                       tree_method='gpu_hist',
                       gpu_id=0)
reg.fit(X_train,
        y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=100)

test = []
score = []
for df in df_list:
    pred = reg.predict(df['data'][FEATURES])
    test.append(pred)
    sc = np.sqrt(mean_squared_error(df['data'][TARGET], pred))
    score.append(sc)

# plt.figure(figsize=(18, 5))
# for i in range(4):
#    fig = px.bar(np.arange(i * 56, (i + 1) * 56), score[i * 56:(i + 1) * 56])
for i in range(4):
    fig = px.bar(score[i * 56:(i + 1) * 56])

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
        Dash: A web application framework for your data.
    '''),
    dcc.Graph(id='example-graph', figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)
