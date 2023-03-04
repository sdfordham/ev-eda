from dash import Dash, dcc, html, Input, Output, no_update
import plotly.express as px
import pandas as pd
from pandas.api.types import is_numeric_dtype

from methods import get_webpage, process_webpage, make_dataframe


res = get_webpage()
cars = process_webpage(res)
df = make_dataframe(cars).fillna(0)
numeric_cols = [col for col in df.columns if is_numeric_dtype(df[col])]

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children="EV viz"),
    dcc.Dropdown(id="x-val", options=numeric_cols),
    dcc.Dropdown(id="y-val", options=numeric_cols),
    dcc.Dropdown(id="size", options=numeric_cols),
    dcc.Graph(id="graph")
])

@app.callback(
    Output("graph", "figure"),
    Input("x-val", "value"),
    Input("y-val", "value"),
    Input("size", "value")
)
def graph_data_callback(x_val, y_val, size):
    if not x_val or not y_val or not size:
        return no_update
    return px.scatter(
        data_frame=df,
        x=x_val,
        y=y_val,
        size=size,
        color="maker",
        hover_data={"model": True}
    )

if __name__ == '__main__':
    print(df.columns)
    app.run_server(debug=True)
