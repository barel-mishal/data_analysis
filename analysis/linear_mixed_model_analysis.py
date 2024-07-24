import polars as pl
import numpy as np
import streamlit as st
import plotly.express as px
import statsmodels.api as sm
import plotly.graph_objects as go
from statsmodels.formula.api import mixedlm
from statsmodels.regression.mixed_linear_model import MixedLM
from typing import Optional

# Define the function for analysis
def linear_mixed_model_analysis(df: pl.DataFrame, dependent_var: str, group_var: str, time_var: Optional[str] = 'Record_count') -> None:
    # Convert to pandas DataFrame for statsmodels
    half_max_people_count = (
        pl.col('people_count') >= pl.col('people_count').max().over("All_Cohorts") / 2
    ).alias("half_max_people_count")
    # Ensure Patient_nmb is treated as a categorical variable

    df = df.with_columns([
        df['Patient_nmb'].cast(pl.Categorical),
        df[group_var].cast(pl.Categorical),
        half_max_people_count
    ]).filter([pl.col("half_max_people_count"), pl.col(dependent_var).is_not_null()]).sort([time_var, group_var])

    st.write(df.to_pandas())

    df_pd = df.to_pandas()

    # # Model formula
    formula = f"{dependent_var} ~ {time_var} * {group_var}"

    # # Fit linear mixed model
    model = mixedlm(formula, df_pd, groups=df_pd["Patient_nmb"])
    result = model.fit()

    # st.write(result)

    # # Display results
    # st.write("### Linear Mixed Model Results")
    st.write(result.summary())

    # # Visualize the data
    st.write("### Data Visualization")

    # # Plot the dependent variable over time for each cohort
    # Calculate mean and confidence interval for each group over time
    grouped_data = df_pd.groupby([group_var, time_var], observed=False)[dependent_var].agg(['mean', 'sem']).reset_index()
    grouped_data['lower_ci'] = grouped_data['mean'] - 1.96 * grouped_data['sem']
    grouped_data['upper_ci'] = grouped_data['mean'] + 1.96 * grouped_data['sem']

    # Plot using Plotly
    fig = go.Figure()

    # Add traces for each group
    for group in grouped_data[group_var].unique():
        group_data = grouped_data[grouped_data[group_var] == group]
        fig.add_trace(go.Scatter(
            x=group_data[time_var], y=group_data['mean'], mode='lines', name=f'Group {group}',
            line=dict(width=2), 
            hoverinfo='x+y+name'
        ))
        fig.add_trace(go.Scatter(
            x=group_data[time_var], y=group_data['lower_ci'], mode='lines', name=f'{group} CI Lower',
            line=dict(width=0), 
            hoverinfo='none', showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=group_data[time_var], y=group_data['upper_ci'], mode='lines', name=f'{group} CI Upper',
            fill='tonexty', line=dict(width=0), 
            hoverinfo='none', showlegend=False
        ))

    # Update layout
    fig.update_layout(
        title='Daily Adherence Score Over Time by Group',
        xaxis_title='Days Since Start',
        yaxis_title='Mean Daily Score',
        template='plotly_dark'
    )

    st.plotly_chart(fig)
