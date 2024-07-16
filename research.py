import streamlit as st
import polars as pl
from urllib.error import URLError
from analysis.correlation_metrices import plot_cohort_correlation_matrix
from analysis.match_graph_type_comparison import match_graph_type_comparison
from analysis.old import analyze_health_data, perform_graph_analysis, perform_t_tests_two_sample, text_analysis_T_test_example, use_parquet_file_by_upload
from analysis.over_time_analysis_comparssion import figure_line_grouped, filter_and_group_by


# TODO: Add template 
# TODO: Add group by graph and table
# TODO: Add t-test
# TODO: Deploy to streamlit share
# TODO: Buy a streamlit share subscription
blue_to_green = [
    '#3C9BED', 
    '#349AC7',
    '#2D9BA1',
    '#26A37B', 
    '#1FAB55',
]
orange_to_green = [
    '#FF9933', 
    '#E6A233', 
    '#CCAB34',
    '#B2B434',
    '#99BD35',
]

col_all_cohorts = "All_Cohorts"
def main():
    try:

        df = use_parquet_file_by_upload()
        if df is None:
            st.write("Please upload a file to continue.")
            return
        df = df.with_columns([pl.col("Date").cast(pl.Datetime)])
        df = df.sort("Date")
        columns = [col_all_cohorts, *filter(lambda x: x != col_all_cohorts, df.columns)]
        cohorts = sorted(df.select(col_all_cohorts).unique().to_pandas().values.flatten())

        st.write("## Schema")
        st.write(df.schema)
        st.write("## Data")
        st.write('TODO: sticky header for the selected cohorts')
        cols = st.multiselect("Filter Cohorts", cohorts)

        df = df.filter(pl.col(col_all_cohorts).is_in(cols))
        st.write(df.to_pandas())

        value_columns = [x for x in columns if x not in ["Patient_nmb", "Date", "Record_count", "Cohort"]]

        col1, col2 = st.columns([2, 1])
        with col1:
            value_x = col_all_cohorts
            st.write("## Cohorts Analysis")
        with col2:
            value_columns = [x for x in columns if x not in ["Patient_nmb", "Date", "Record_count", "Cohort"]]
            value_y = st.selectbox("Y Axis", value_columns, index=4)

        rander_line_graph(df, value_y)
        
        st.write('''
        ### Improvements

        - Add an option to fill or filter out missing values.
        - Implement a date range filter.
        - Display additional information when hovering over data points.
        - use color persistent to represent different cohorts.
        ''')

        graph_type = st.selectbox("Graph Type", ["Histogram", "Box"])

        rander_histogram(df, value_x, value_y, value_x, graph_type)

        rander_metrics(df, cols)

        st.write('''
                 # t-test
        ''')

        match len(cols):
            case 2:
                rander_t_test(df, value_columns)
            case 3:
                st.write("TODO: Implement anova test")
            case _:
                st.write("Please select two cohorts to perform a t-test.")

        st.write('''
        ### TODOs

        - Make - Paired t-test (dependent t-test): Compares the means of the same group at different times (e.g., before and after a treatment).

        ''')


        if False:

            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                value_x = st.selectbox(
                    "Value Of X", columns
                )
            with col2:
                value_y = st.selectbox(
                    "Value Of Y", columns, index=1
                )
            with col3:
                value_color = st.selectbox(
                    "Value Of Color", set([None, *df.columns]), index=0
                )
            with col4:
                graph_type = st.selectbox(
                    "Graph Type",
                    ["Bar", "Line", "Scatter", "Pie", "Histogram"],
                )
            if not value_x:
                st.error(f"Please select a value for X axis. {df.columns}")
            elif not value_y:
                st.error(f"Please select a value for Y axis. {df.columns}")
            elif value_x == value_y:
                st.error(f"Please select different values for X and Y axes. {df.columns}")
            else:
                perform_graph_analysis(df, value_x, value_y, value_color, graph_type)
            
            correlation_matrix, fig = analyze_health_data(df)
            st.header("Correlation Matrix")
            st.write(correlation_matrix)

            st.header("daily Trends")
            st.plotly_chart(fig)

    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
            """
            % e.reason
        )

def rander_line_graph(df, value_y):
        proccess = filter_and_group_by(df, ["Record_count", col_all_cohorts], value_y)
        
        fig = figure_line_grouped(
            proccess, 
            "Record_count", 
            value_y,
            f"{value_y} Over Time", 
            "Days Since Start", 
            "Mean Daily Score", 
            ['#FF9933','#3C9BED', '#349AC7', '#1FAB55'], 
            col_all_cohorts,
            True
        )

        st.plotly_chart(fig) 
    
def rander_histogram(df, value_x, value_y, value_color, graph_type="Histogram"):
    fig = match_graph_type_comparison(df, value_x, value_y, value_color, graph_type)
    st.plotly_chart(fig)

def rander_metrics(df: pl.DataFrame, cohors: list):
        for cohort in cohors:
            plot_cohort_correlation_matrix(df.filter(pl.col(col_all_cohorts) == cohort), cohort, blue_to_green)

def rander_t_test(df: pl.DataFrame, columns: list):
    col1, col2 = st.columns(2)
    with col1: 
        value_x = st.selectbox(
            "Independent 1", columns
        )
    with col2:
        value_y = st.selectbox(
            "Independent 2", columns, index=3
        )
    st.write("## Perform t-tests")
    if value_x and value_y:
        perform_t_tests_two_sample(df, value_x, value_y)
        text_analysis_T_test_example()

    



if __name__ == "__main__":
    main()