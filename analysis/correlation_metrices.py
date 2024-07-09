import pandas as pd
import numpy as np
import plotly.express as px
import polars as pl 
import polars.selectors as cs 
import streamlit as st


def correlation_matrix(df: pl.DataFrame):
    return df.select(cs.numeric()).drop_nulls().corr()

def plot_cohort_correlation_matrix(df: pl.DataFrame, cohort: pl.String, color_scale = px.colors.diverging.PiYG):
    # Filter the DataFrame for the specified cohort and calculate the correlation matrix
    corr_matrix = correlation_matrix(df)

    # Apply a mask to the upper triangle of the correlation matrix
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    corr_matrix_masked = corr_matrix.to_pandas().mask(mask)

    # Customize the color scale
    
    # Create the heatmap
    fig = px.imshow(
        corr_matrix_masked,
        text_auto=True,
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
        margin=dict(t=50, l=50, b=50, r=50),
        coloraxis_colorbar=dict(
            title="Correlation",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1", "-0.5", "0 - No correlation", "0.5", "1 - Very strong correlation"],
        )
    )

    # Update axes titles
    fig.update_xaxes(title="Metrics")
    fig.update_yaxes(title="Metrics")

    # Increase the font size for better readability
    fig.update_annotations(font_size=12)

    # Show the figure
    st.plotly_chart(fig)



# Example usage
# plot_cohort_correlation_matrix(df, "ISR")
