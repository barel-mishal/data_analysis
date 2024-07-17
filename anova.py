
import polars as pl
from scipy import stats

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
                scores.append(filtered_data.select(param).to_numpy())
        
        # Ensure we have at least two groups with data for ANOVA
        if len(scores) >= 2 and all(len(group) > 0 for group in scores):
            # Perform ANOVA
            f_val, p_val = stats.f_oneway(*scores)
        else:
            f_val, p_val = float('nan'), float('nan')
        
        # Store the Results
        results[param] = {'F-value': f_val, 'p-value': p_val}
    
    return results
