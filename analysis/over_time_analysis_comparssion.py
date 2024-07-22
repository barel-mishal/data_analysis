import polars as pl
import plotly.express as px

def figure_line_grouped(
        df: pl.DataFrame, 
        x: str, 
        y: str, 
        title: str, 
        x_label: str, 
        y_label: str, 
        color_discrete_sequence: list, 
        color: str,
        markers: bool): 
    # Convert Polars DataFrame to Pandas for Plotly
    df = df.to_pandas()

    # Define the labels dictionary
    labels = {x: x_label, y: y_label}

    # Create the line plot with Plotly Express
    fig = px.line(
        df, 
        x=x, 
        y=y, 
        color=color,  # This column will be used for coloring and will create the legend entries
        title=title, 
        labels=labels,
        color_discrete_sequence=color_discrete_sequence,  # Ensure this is a list of color strings
        markers=markers,  # Add markers to the line if True
        hover_data={"people_count": True}
    )

    # Improve the aesthetics
    fig.update_layout(
        title_font_size=24,
        font=dict(size=18),
        title_x=0.5,  # Center the title
        plot_bgcolor='white',  # Background color
        showlegend=True  # Show the legend
    )

    fig.update_traces(
        line=dict(width=3),  # Make the line thicker
        marker=dict(size=8)  # Enlarge the markers if they are enabled
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

    return fig

def filter_and_group_by(df: pl.DataFrame, group_by: list, agg_by: str = "Daily_score"):
    return df.filter(
            pl.col("Daily_score").is_not_null(),
        )\
        .group_by(group_by)\
        .agg([
            pl.col(agg_by).mean().alias(agg_by),
            pl.count().alias("people_count")
        ])\
        .sort(group_by)