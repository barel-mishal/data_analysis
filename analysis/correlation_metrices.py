import pandas as pd
import numpy as np
import plotly.express as px
import polars as pl 
import polars.selectors as cs 
from scipy import stats
import streamlit as st

def correlation_matrix(df: pl.DataFrame):
    return df.select(cs.numeric()).drop_nulls().corr()

def correlation_matrix_with_p_values(df: pl.DataFrame):
    corr_matrix = correlation_matrix(df)
        # Compute p-values matrix
    num_matrix = corr_matrix.to_numpy()

    pvals = np.zeros(num_matrix.shape, dtype=np.float64)
    for i in range(num_matrix.shape[0]):
        for j in range(num_matrix.shape[1]):
            if i != j:
                _, pval = stats.pearsonr(num_matrix[:, i], num_matrix[:, j])
                pvals[i, j] = pval
            else:
                pvals[i, j] = np.nan  # NaN for diagonal
    
    # # Convert p-values to DataFrame
    pvals_df = pl.DataFrame(pvals, schema=corr_matrix.schema)
    return corr_matrix, pvals_df

def plot_cohort_correlation_matrix(df: pl.DataFrame, cohort: pl.String, color_scale=px.colors.diverging.RdBu, significance_level=0.05):
    # Filter the DataFrame for the specified cohort and calculate the correlation matrix
    corr_matrix, pvals_df = correlation_matrix_with_p_values(df)
    st.write("### P-Values")
    st.write(pvals_df.to_pandas())
    st.write("### Correlation Matrix")
    st.write(corr_matrix.to_pandas())

    # Apply a mask to the upper triangle of the correlation matrix
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    corr_matrix_masked = corr_matrix.to_pandas().mask(mask)
    pvals_masked = pvals_df.to_pandas().mask(mask)

    significances = pvals_df.select([
        pl.when(cs.numeric().lt(significance_level)).then(pl.lit("*")).otherwise(pl.lit("")).name.prefix("Significance: "),
        
    ]).to_pandas()

    masked_significances = significances.mask(mask)

    # Determine the color scale based on the cohort
    color_scale = px.colors.diverging.RdBu.copy()
    if cohort == 'ISR':
        # Blue at the start, red at the end (original RdBu)
        pass  # No action needed
    elif cohort == 'IND':
        # Red at the start, blue at the end (reverse the color scale)
        color_scale.reverse()

    

    # Create the heatmap
    fig = px.imshow(
        corr_matrix_masked,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale=color_scale,
        title=f"{cohort} Cohort Metrics Correlation",
        labels=dict(color="Correlation Coefficient", pval="P-Value"),
        x=corr_matrix_masked.columns,
        y=corr_matrix_masked.columns,
        template="plotly_white",
    )

    
    for i in range(corr_matrix_masked.shape[0]):
        for j in range(corr_matrix_masked.shape[1]):
            if not mask[i, j] and masked_significances.iloc[i, j] == "*":
                fig.add_annotation(
                    x=corr_matrix_masked.columns[j],
                    y=corr_matrix_masked.columns[i],
                    text="*",
                    xshift=19,
                    showarrow=False,
                    font=dict(color="red", size=20),
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
