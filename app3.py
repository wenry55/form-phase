from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

import plotly.express as px
import numpy as np
import os
import pandas as pd
import json
from dash.dash_table import DataTable 

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
    html.Div(id='my-output')
])

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


if __name__ == '__main__':
    app.run_server(debug=True)

    print('next run.')