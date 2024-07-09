import polars as pl
import plotly.express as px


def match_graph_type_comparison(df: pl.DataFrame, value_x: str, value_y: str, value_color: str, graph_type: str):
    match graph_type:
        case "Histogram":
            fig = px.histogram(df.to_pandas(), color=value_x, x=value_y, marginal="box", barmode="overlay", nbins=20, histnorm="percent")
        case _:
            fig = px.box(df.to_pandas(), x=value_x, y=value_y, color=value_color)
    return fig