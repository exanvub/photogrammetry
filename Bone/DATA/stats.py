import pandas as pd
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import MultiComparison
from statsmodels.formula.api import ols
from scipy.stats import ttest_rel

# Load the data from the Excel file (Adjust the file path)
file_path = "DATA/stats.xlsx"  # Replace with the actual file path
data = pd.read_excel(file_path)

# Create a pandas DataFrame from the data
df = pd.DataFrame(data)

# Define your variables for the repeated measures ANOVA
independent_variable = 'Model'  # The variable to compare (Model)
subject_variable = 'Condition'  # The repeated measures variable (Condition)

# List of mesh quality metrics
mesh_quality_metrics = ['minimum', 'maximum', 'average', 'median', 'stdDev', 'Variance']

# Perform the repeated measures ANOVA and Bonferroni correction for each metric
for metric in mesh_quality_metrics:
    # Perform the repeated measures ANOVA for the current metric
    aov_metric = AnovaRM(df, metric, subject=subject_variable, within=[independent_variable])
    result_metric = aov_metric.fit()

    # Print the ANOVA results for the current metric
    print(f"{metric} Metric ANOVA:")
    print(result_metric)

    # Apply the Bonferroni correction for multiple comparisons for the current metric
    mc_metric = MultiComparison(df[metric], df[independent_variable])
    result_metric_corr = mc_metric.allpairtest(ttest_rel, method='bonferroni')

    # Print the corrected p-values for the current metric
    print(f"{metric} Metric Bonferroni Correction:")
    print(result_metric_corr[0])

# Define your variables for the repeated measures ANOVA for Surface Area
dependent_variable_surface_area = 'Surface Area'  # The primary outcome measure

# Perform the repeated measures ANOVA for Surface Area
aov_surface_area = AnovaRM(df, dependent_variable_surface_area, subject=subject_variable, within=[independent_variable])
result_surface_area = aov_surface_area.fit()

# Print the ANOVA results for Surface Area
print("Surface Area ANOVA:")
print(result_surface_area)

# Apply the Bonferroni correction for multiple comparisons for Surface Area
mc_surface_area = MultiComparison(df[dependent_variable_surface_area], df[independent_variable])
result_surface_area_corr = mc_surface_area.allpairtest(ttest_rel, method='bonferroni')

# Print the corrected p-values for Surface Area
print("Surface Area Bonferroni Correction:")
print(result_surface_area_corr[0])

# Define your variables for the repeated measures ANOVA for Mesh Volume
dependent_variable_mesh_volume = 'Mesh Volume'  # The additional outcome measure

# Perform the repeated measures ANOVA for Mesh Volume
aov_mesh_volume = AnovaRM(df, dependent_variable_mesh_volume, subject=subject_variable, within=[independent_variable])
result_mesh_volume = aov_mesh_volume.fit()

# Print the ANOVA results for Mesh Volume
print("Mesh Volume ANOVA:")
print(result_mesh_volume)

# Apply the Bonferroni correction for multiple comparisons for Mesh Volume
mc_mesh_volume = MultiComparison(df[dependent_variable_mesh_volume], df[independent_variable])
result_mesh_volume_corr = mc_mesh_volume.allpairtest(ttest_rel, method='bonferroni')

# Print the corrected p-values for Mesh Volume
print("Mesh Volume Bonferroni Correction:")
print(result_mesh_volume_corr[0])
