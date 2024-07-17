import polars as pl
from scipy import stats
from scipy.stats import shapiro, levene, tukey_hsd

def perform_anova(df: pl.DataFrame, cohorts, parameters):
    # Filter Data by Cohorts
    cohort_data = {cohort: df.filter(pl.col('All_Cohorts') == cohort) for cohort in cohorts}
    
    results = {}
    
    for param in parameters:
        # Filter out null values for each cohort
        scores = []
        for cohort in cohorts:
            filtered_data = cohort_data[cohort].filter(pl.col(param).is_not_null())
            if len(filtered_data) > 0:
                scores.append(filtered_data.select(param).to_numpy().flatten())
        
        # Ensure we have at least two groups with data for ANOVA
        if len(scores) >= 2 and all(len(group) > 0 for group in scores):
            # Perform ANOVA
            f_val, p_val = stats.f_oneway(*scores)
            
            # Check Assumptions
            normality_results = [shapiro(group).pvalue for group in scores if len(group) > 3]
            homogeneity_p_val = levene(*scores).pvalue if len(scores) > 1 else float('nan')
            
            # Store the Results
            results[param] = {
                'F-value': f_val,
                'p-value': p_val,
                'normality': normality_results,
                'homogeneity': homogeneity_p_val
            }
        else:
            results[param] = {
                'F-value': float('nan'),
                'p-value': float('nan'),
                'normality': [],
                'homogeneity': float('nan')
            }

    return results


def check_assumptions(df, cohorts, parameters):
    assumption_results = {}
    for param in parameters:
        data = [df.filter(pl.col('All_Cohorts') == cohort).select(param).to_numpy() for cohort in cohorts]
        # Normality
        normality_results = [shapiro(group).pvalue for group in data if len(group) > 3]
        # Homogeneity of Variance
        homogeneity_result = levene(*data).pvalue if len(data) > 1 else None
        assumption_results[param] = {
            'normality': normality_results,
            'homogeneity': homogeneity_result
        }
    return assumption_results

def perform_posthoc(df, cohorts, parameters):
    posthoc_results = {}
    for param in parameters:
        data = [df.filter(pl.col('All_Cohorts') == cohort).select(param).to_numpy() for cohort in cohorts]
        if len(data) > 1:
            posthoc_results[param] = tukey_hsd(*data)
    return posthoc_results

def anova_results_to_dataframe(anova_results):
    # Initialize lists to hold data
    parameters = []
    f_values = []
    p_values = []
    normality_p_values = []
    homogeneity_p_values = []
    assumptions_met = []

    # Populate lists with data from anova_results
    for param, result in anova_results.items():
        parameters.append(param)
        f_values.append(result['F-value'])
        p_values.append(result['p-value'])
        normality_p_values.append(result['normality'])
        homogeneity_p_values.append(result['homogeneity'])
        assumptions_met.append(all(p >= 0.05 for p in result['normality']) and result['homogeneity'] >= 0.05)
    
    # Create DataFrame
    df = pl.DataFrame({
        'Parameter': parameters,
        'F-value': f_values,
        'p-value': p_values,
        'Normality p-values': normality_p_values,
        'Levene\'s Test p-value': homogeneity_p_values,
        'Assumptions Met': assumptions_met
    })

    return df
