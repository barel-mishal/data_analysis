import numpy as np
import streamlit as st
import polars as pl
import plotly.express as px
from scipy.stats import ttest_ind
from urllib.error import URLError
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import glob

def use_parquet_file_by_upload():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        try:
            df = pl.read_parquet(uploaded_file)
            if df.is_empty():
                st.error("The uploaded file is empty.")
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")

def get_UN_data():
    # result_file = "/Users/barel/projects/lihi_research/research_data/IBDMED_after_cleaning.parquet"
    # file = "/Users/barel/projects/lihi_research/research_data/IBDMED_without_cleaning.parquet"

    root_folder = "lihi_research"
    result_file_pattern = "IBDMED_after_cleaning.parquet"
    file_pattern = "IBDMED_without_cleaning.parquet"
    
    # Use glob to search for the files starting from the root folder
    result_file = glob.glob(f"**/{root_folder}/**/{result_file_pattern}", recursive=True)
    file = glob.glob(f"**/{root_folder}/**/{file_pattern}", recursive=True)
    
    if not result_file or not file:
        raise FileNotFoundError("One or both of the specified files were not found.")
    df = pl.read_parquet(result_file)    
    return df

def match_graph_type(graph_type, data, x, y, color=None):
    if graph_type == "Bar":
        ccolor = color or x
        chart = px.bar(data, x=x, y=y, color=ccolor)
    elif graph_type == "Line":
        ccolor = color or x
        chart = px.line(data, x=x, y=y, color=ccolor)
    elif graph_type == "Scatter":
        ccolor = color or x
        chart = px.scatter(data, x=x, y=y, color=ccolor)
    elif graph_type == "Pie":
        ccolor = color or x
        chart = px.pie(data, names=x, values=y, color=ccolor)
    elif graph_type == "Histogram":
        ccolor = color or x
        chart = px.histogram(data, x=x, y=y, color=ccolor)
    return chart

def filter_none(x):
    return x is not None

def text_analysis_example():
    st.write("""
Example 1: Line Graph

    •    Value Of X: Date
    •    Value Of Y: Actual_Steps
    •    Value Of Color: Patient_nmb
    •    Graph Type: Line

Analysis:
This line graph would show the trend of actual steps taken by different patients over time. Each line represents a different patient, allowing you to compare their activity levels across different dates.

Example 2: Bar Graph

    •    Value Of X: Patient_nmb
    •    Value Of Y: Daily_score
    •    Value Of Color: Cohort
    •    Graph Type: Bar

Analysis:
This bar graph would illustrate the daily scores for different patients, grouped by their cohorts. It helps in comparing the performance of patients within the same cohort as well as between different cohorts.

Example 3: Scatter Plot

    •    Value Of X: Resting_Heart_Rate
    •    Value Of Y: Stress
    •    Value Of Color: Cohort
    •    Graph Type: Scatter

Analysis:
The scatter plot would show the relationship between Resting_Heart_Rate and stress levels, with different colors representing different cohorts. This can help identify if there is a correlation between heart rate and stress levels across different groups.

Example 4: Pie Chart

    •    Value Of X: Cohort
    •    Value Of Y: Record_count
    •    Value Of Color: Cohort
    •    Graph Type: Pie

Analysis:
A pie chart would represent the distribution of record counts across different cohorts. Each slice of the pie would show the proportion of records that belong to each cohort, giving a quick visual summary of the data distribution.

Example 5: Histogram

    •    Value Of X: Sleep
    •    Value Of Y: Record_count
    •    Value Of Color: Cohort
    •    Graph Type: Histogram

Analysis:
This histogram would display the distribution of sleep hours recorded across different cohorts. It would show how frequently different sleep durations are observed in the dataset, providing insights into the sleep patterns of patients.
""")

def text_analysis_T_test_example():
    st.write("""xample 1: Comparing Actual_Steps between Two Cohorts

	•	Purpose: To determine if there is a significant difference in the average number of steps taken between patients in different cohorts (ISR vs IND).
	•	Value Of 1: Cohort
	•	Value Of 2: Actual_Steps
	•	Groups: ISR and IND

Example 2: Comparing Resting_Heart_Rate between Two Cohorts

	•	Purpose: To see if there is a significant difference in the average Resting_Heart_Rate between patients from different cohorts (ISR vs IND).
	•	Value Of 1: Cohort
	•	Value Of 2: Resting_Heart_Rate
	•	Groups: ISR and IND

Example 3: Comparing Stress Levels between Two Cohorts

	•	Purpose: To assess whether the stress levels differ significantly between patients in different cohorts (ISR vs IND).
	•	Value Of 1: Cohort
	•	Value Of 2: Stress
	•	Groups: ISR and IND

Example 4: Comparing Daily_score between Two Cohorts

	•	Purpose: To investigate if the daily scores are significantly different between patients from different cohorts (ISR vs IND).
	•	Value Of 1: Cohort
	•	Value Of 2: Daily_score
	•	Groups: ISR and IND

Example 5: Comparing Sleep Duration between Two Cohorts

	•	Purpose: To determine if there is a significant difference in the average sleep duration between patients from different cohorts (ISR vs IND).
	•	Value Of 1: Cohort
	•	Value Of 2: Sleep
	•	Groups: ISR and IND

Procedure for Each Example:

	1.	Select Cohort as Value Of X.
	2.	Select the respective metric (e.g., Actual_Steps, Resting_Heart_Rate, Stress, Daily_score, Sleep) as Value Of Y.
	3.	Perform a t-test to compare the means of the selected metric between the two groups (ISR and IND).
	4.	Interpret the t-test results:
	•	t-statistic: Indicates the magnitude of difference between the groups.
	•	p-value: Indicates the significance of the results. A p-value < 0.05 typically suggests a significant difference between the groups.
             
""")

def perform_t_tests_two_sample(df: pl.DataFrame, value_x: str, value_y: str):
    # Step 1: Input Validation
    if value_x not in df.columns or value_y not in df.columns:
        st.write("Error: Invalid columns for t-test.")
        return 

    unique_values = df.select(value_x).unique().to_numpy()
    if len(unique_values) != 2:
        st.write("Error: t-test requires exactly two groups.")
        return 

    # Step 2: Data Preprocessing
    group_1 = df.filter(pl.col(value_x) == unique_values[0]).drop_nulls(value_y)
    group_2 = df.filter(pl.col(value_x) == unique_values[1]).drop_nulls(value_y)

    if len(group_1) < 2 or len(group_2) < 2:
        st.write("Error: Not enough data for t-test after dropping NaN values.")
        return 

    # Step 3: Variance Check
    var_group_1 = np.var(group_1.select(value_y).to_numpy())
    var_group_2 = np.var(group_2.select(value_y).to_numpy())

    if var_group_1 == 0 or var_group_2 == 0:
        st.write("Error: One of the groups has no variance.")
        return 

    # Step 4: T-test Execution
    t_stat, p_value = ttest_ind(group_1.select(value_y).to_numpy(), group_2.select(value_y).to_numpy(), equal_var=False)

    # Step 5: Result Interpretation
    alpha = 0.05
    conclusion = "reject" if p_value < alpha else "fail to reject"
    result = (
        f"T-test results: t-statistic = {t_stat[0]:.4f}, p-value = {p_value[0]:.4f}\n"
        f"Conclusion: Based on the p-value, we {conclusion} the null hypothesis at the {alpha} significance level."
    )

    # Step 6: Visualization
    fig = px.box(df.to_pandas(), x=value_x, y=value_y, title=f'Box Plot of {value_y} by {value_x}')
    
    # Display the results and the plot
    st.write(result)
    st.plotly_chart(fig)
    
    

def perform_graph_analysis(
        df: pl.DataFrame, 
        value_x: str, 
        value_y: str, 
        value_color: str, 
        graph_type: str,
    ):
    values = filter_nones_and_uniqe([value_x, value_y, value_color])
    data = df.select(values)
    st.write(
        "### Comparison of Dietary Adherence and Health Metrics in Hospitalized Patients from India and Israel", 
        data.sort(value_x).to_pandas()
    )
    chart = match_graph_type(graph_type, df.to_pandas(), value_x, value_y, color=value_color)
    st.write("### Graphical Representation of Data")
    st.write(f"#### {graph_type}")
    st.plotly_chart(chart)
    st.write(text_analysis_example())

def plan_group_by(
    df: pl.DataFrame, 
    col_name: str = None,
    group_by_y: str = None, 
    group_by_color: str = None,
    ):
    if not col_name or not group_by_color or not group_by_y:
        return df
    v1, v2 = filter_nones_and_uniqe([group_by_color, group_by_y])
    return df.group_by(v1, v2)\
        .agg(pl.col(col_name).mean().alias(col_name))\
        .sort([v1, v2])

def filter_nones_and_uniqe(array: list):
    return list(set(filter(filter_none, array)))

def analyze_health_data(df: pl.DataFrame):
    # Load the dataset using polars

    # Convert 'Date' to datetime and sort by date
    data = df
    data = data.sort('Record_count')

    data = data.with_columns([
        pl.col('Record_count').cut([7, 14, 21], labels=["1", "2", "3", "4"]).alias('Group')
    ])
    
    grouped_data = data.group_by('Group', maintain_order=True).agg([
        pl.mean('Actual_Steps').alias('Actual_Steps'),
        pl.mean('Stress').alias('Stress'),
        pl.mean('Sleep').alias('Sleep'),
        pl.mean('Daily_score').alias('Daily_score')
    ])

    # Fill missing values
    data = data.with_columns([
        pl.col('Resting_Heart_Rate').fill_nan(pl.median('Resting_Heart_Rate')),
        pl.col('Stress').fill_nan(pl.median('Stress')),
        pl.col('Sleep').fill_nan(pl.median('Sleep')),
        pl.col('Daily_score').fill_nan(pl.median('Daily_score'))
    ])

    grouped_data = grouped_data.with_columns(
        pl.col('Actual_Steps').shift(1).alias('Lagged_Steps_1')
    )

    # Resample data by week
    correlation_matrix = grouped_data.select([
        pl.corr('Lagged_Steps_1', 'Stress').alias('Lagged_Steps_1_Stress'),
        pl.corr('Lagged_Steps_1', 'Sleep').alias('Lagged_Steps_1_Sleep'),
        pl.corr('Lagged_Steps_1', 'Daily_score').alias('Lagged_Steps_1_Daily_score'),
        pl.corr('Stress', 'Sleep').alias('Stress_Sleep'),
        pl.corr('Stress', 'Daily_score').alias('Stress_Daily_score'),
        pl.corr('Sleep', 'Daily_score').alias('Sleep_Daily_score')
    ])

    # Create lagged variables
    daily_data = grouped_data.with_columns([
        pl.col('Actual_Steps').shift(1).alias('Lagged_Steps_1')
    ])
  
    correlation_matrix = correlation_matrix.to_pandas()

    # Convert grouped_data to pandas for visualization
    grouped_data = grouped_data.to_pandas()

    # Plot time series using plotly
    fig = make_subplots(rows=2, cols=2, subplot_titles=('Daily Actual Steps', 'Daily Stress Levels', 'Daily Sleep Duration', 'Daily Daily Score'))

    fig.add_trace(go.Scatter(x=daily_data['Group'], y=daily_data['Actual_Steps'], mode='lines+markers', name='Actual Steps'), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily_data['Group'], y=daily_data['Stress'], mode='lines+markers', name='Stress Levels', marker=dict(color='red')), row=1, col=2)
    fig.add_trace(go.Scatter(x=daily_data['Group'], y=daily_data['Sleep'], mode='lines+markers', name='Sleep Duration', marker=dict(color='purple')), row=2, col=1)
    fig.add_trace(go.Scatter(x=daily_data['Group'], y=daily_data['Daily_score'], mode='lines+markers', name='Daily Score', marker=dict(color='orange')), row=2, col=2)

    fig.update_layout(height=800, width=1200, title_text="Daily Trends")

    return correlation_matrix, fig
