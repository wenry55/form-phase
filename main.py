from distutils.log import debug
from dash import Dash, html, dcc

import dash

app = Dash(__name__, use_pages=True)
app.layout = html.Div([
    html.H1('multi home'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}",
                     href=page['relative_path'] + "?stage_id=2&channel_id=3"))
        for page in dash.page_registry.values()
    ]),
    dash.page_container,
])

NODATA = 3

if __name__ == '__main__':
    app.run_server(debug=False)