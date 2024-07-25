import pandas as pd
import numpy as np
import plotly.express as px
import polars as pl 
import polars.selectors as cs 
import streamlit as st

def correlation_matrix(df: pl.DataFrame):
    return df.select(cs.numeric()).drop_nulls().corr()

def plot_cohort_correlation_matrix(df: pl.DataFrame, cohort: pl.String, color_scale=px.colors.sequential.Viridis):
    # Filter the DataFrame for the specified cohort and calculate the correlation matrix
    corr_matrix = correlation_matrix(df)

    # Apply a mask to the upper triangle of the correlation matrix
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    corr_matrix_masked = corr_matrix.to_pandas().mask(mask)

    # Create the heatmap
    fig = px.imshow(
        corr_matrix_masked,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale=color_scale,
        title=f"{cohort} Cohort Metrics Correlation",
        labels=dict(color="Correlation Coefficient"),
        x=corr_matrix_masked.columns,
        y=corr_matrix_masked.columns,
        template="plotly_white",
    )

    # Improve layout and styling
    fig.update_layout(
        margin=dict(t=60, l=60, b=60, r=60),
        coloraxis_colorbar=dict(
            title="Correlation",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1 (Strong Negative)", "-0.5", "0 (No Correlation)", "0.5", "1 (Strong Positive)"],
            len=0.8,
            thickness=20,
            xpad=10  # Increase the padding from the heatmap
        )
    )

    # Update axes titles and increase font size
    fig.update_xaxes(title="Metrics", showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(title="Metrics", showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_annotations(font_size=14)

    # Show the figure
    st.plotly_chart(fig)
