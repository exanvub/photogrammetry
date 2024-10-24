# Load necessary libraries
library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(reshape2)
library(ggpubr)
library(tidyverse)
library(emmeans)


# Read the data from the Excel file
file_path <- "Data/Use of Real Life 3D Models in Education.xlsx"

data <- read_excel(file_path)

data_orig <- data

# Add ResponderType column to orig data
data <- data %>%
  mutate(ResponderType = `I am a`)

# Process ranking data
data_long <- data %>%
  # Separate rankings into individual rows
  separate_rows(`Rank the following possible future features in order of importance:`, sep = ";") %>%
  # unique identifier for each response and its rank
  group_by(ID) %>%
  mutate(Rank = row_number()) %>%
  ungroup() %>%
  # Select relevant columns and pivot to a long format
  select(ID, ResponderType, Rank, `Rank the following possible future features in order of importance:`) %>%
  rename(Feature = `Rank the following possible future features in order of importance:`)

print(head(data_long))

# Heatmap
ggplot(data_long, aes(x = Rank, y = Feature, fill = ResponderType)) +
  geom_tile(color = "white") +
  scale_fill_brewer(palette = "Set3") +
  labs(title = "Rankings per Type of Responder",
       x = "Rank",
       y = "Feature") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Jitter Plot
ggplot(data_long, aes(x = Rank, y = Feature, color = ResponderType)) +
  geom_point(position = position_jitter(width = 0.2, height = 0.2), alpha = 0.7, size = 3) +
  scale_color_brewer(palette = "Set1") +
  labs(title = "Rankings per Type of Responder",
       x = "Rank",
       y = "Feature") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Find significant differences between type of responders

agg_data <- data_long %>%
  group_by(ResponderType, Feature) %>%
  summarise(Mean_Rank = mean(Rank, na.rm = TRUE), .groups = 'drop')

# ANOVA to test
anova_results <- aov(Rank ~ Feature * ResponderType, data = data_long)
summary(anova_results)

# if there's a significant interaction or main effect
# pairwise comparisons
if (summary(anova_results)[[1]]$`Pr(>F)`[3] < 0.05) {
  pairwise_results <- TukeyHSD(anova_results, "Feature:ResponderType")
  #print(pairwise_results)
} else {
  cat("No significant differences found between responder types.\n")
}

# Convert Tukey HSD results to data frame 
# Feature:ResponderType:
tukey_df <- as.data.frame(pairwise_results$`Feature:ResponderType`)
tukey_df$Comparison <- rownames(tukey_df)

if (summary(anova_results)[[1]]$`Pr(>F)`[3] < 0.05) {
  pairwise_results <- TukeyHSD(anova_results, "ResponderType")
  print(pairwise_results)
} else {
  cat("No significant differences found between responder types.\n")
}

# Convert Tukey HSD results to data frame for plotting
# ResponderType:
tukey_df <- as.data.frame(pairwise_results$ResponderType)
tukey_df$Comparison <- rownames(tukey_df)

# Plot Tukey HSD results
ggplot(tukey_df, aes(x = Comparison, y = diff, color = `p adj` < 0.05)) +
  geom_point(size = 4) +
  geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
  labs(title = "Tukey HSD Results for Responder Types",
       x = "Comparison",
       y = "Difference in Mean Rank",
       color = "Significant") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Kruskal-Wallis test to find significant differences between type of responders
kruskal_results <- data_long %>%
  group_by(Feature) %>%
  summarise(p_value = kruskal.test(Rank ~ ResponderType, data = .)$p.value)

print(kruskal_results)

# perform pairwise comparisons using Dunn's test
if (any(kruskal_results$p_value < 0.05)) {
  pairwise_results <- data_long %>%
    group_by(Feature) %>%
    do(pairwise = dunnTest(Rank ~ ResponderType, data = ., method = "bonferroni"))

  print(pairwise_results)
}

# Perform simple effects analysis for each feature
emmeans_results <- emmeans(anova_results, pairwise ~ Feature | ResponderType)
emmeans_results
# Print the results
print(emmeans_results)

# Extract the emmeans and contrasts from the emmeans_results
emmeans_data <- as.data.frame(emmeans_results$emmeans)
contrasts_data <- as.data.frame(emmeans_results$contrasts)

# Plot the Estimated Marginal Means (emmeans)
ggplot(emmeans_data, aes(x = Feature, y = emmean, color = ResponderType)) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = lower.CL, ymax = upper.CL), width = 0.2) +
  labs(title = "Estimated Marginal Means by Feature and Responder Type",
       x = "Feature",
       y = "Estimated Mean") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  facet_wrap(~ ResponderType, scales = "free_x")

# Prepare data for the contrasts plot
contrasts_data <- contrasts_data %>%
  mutate(Feature1 = sub(" - .*", "", contrast),
         Feature2 = sub(".* - ", "", contrast))

# Plot Contrasts
ggplot(contrasts_data, aes(x = Feature1, y = estimate, color = p.value < 0.05)) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = estimate - SE, ymax = estimate + SE), width = 0.2) +
  labs(title = "Contrasts of Features within Responder Type",
       x = "Feature Comparison",
       y = "Estimated Difference",
       color = "Significant") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  facet_wrap(~ ResponderType, scales = "free_x")

#---------- Ranking Barplot:

ranking_column <- "Rank the following possible future features in order of importance:"
rankings <- data_orig[[ranking_column]]

# Split the data into list of character vectors
rankings <- str_split(rankings, ";") %>% map(~ .x[.x != ""])
print(rankings)

rankings_df <- tibble(rankings = rankings) %>%
  unnest_wider(rankings, names_sep = "_") %>%
  pivot_longer(everything(), names_to = "position", values_to = "feature") %>%
  mutate(position = parse_number(position))
print(rankings_df)

# Calculate the average rank for each feature
average_ranks <- rankings_df %>%
  group_by(feature) %>%
  summarise(average_rank = mean(position))

# Subtract average ranks from 6 (to reverse order)
average_ranks <- average_ranks %>%
  mutate(adjusted_rank = 6 - average_rank)
print(average_ranks)

# Plot the adjusted ranks
ggplot(average_ranks, aes(x = reorder(feature, adjusted_rank), y = adjusted_rank)) +
  geom_col(fill = "skyblue") +
  coord_flip() +
  labs(title = "Ranking of Future Features",
       x = "Feature",
       y = "Average Rank)") +
  theme_minimal()

#---------------

# By Group

ranking_column <- "Rank the following possible future features in order of importance:"
group_column <- "I am a"

# Extract rankings and group information
rankings <- data_orig[[ranking_column]]
groups <- data_orig[[group_column]]

# Combine rankings and groups into a single data frame
ranking_data <- tibble(
  group = groups,
  rankings = str_split(rankings, ";") %>% map(~ .x[.x != ""])
)

# Process the ranking data
ranking_data_df <- ranking_data %>%
  unnest_wider(rankings, names_sep = "_") %>%
  pivot_longer(-group, names_to = "position", values_to = "feature") %>%
  mutate(position = parse_number(position))

# Calculate the average rank for each feature within each group
average_ranks <- ranking_data_df %>%
  group_by(group, feature) %>%
  summarise(average_rank = mean(position), .groups = 'drop') %>%
  mutate(adjusted_rank = 6 - average_rank)

print(average_ranks)

# Plot the adjusted ranks grouped by feature
ggplot(average_ranks, aes(x = reorder(feature, adjusted_rank), y = adjusted_rank, fill = group)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(title = "Ranking of Future Features by Group",
       x = "Feature",
       y = "Average Rank") +
  theme_minimal()


# Create the plot
ggplot(average_ranks, aes(x = reorder(feature, adjusted_rank), y = adjusted_rank, fill = group)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(title = "Ranking of Future Features by Group",
       x = "Feature",
       y = "Average Rank") +
  theme_minimal() +
  theme(axis.text.y = element_text(size = 14),  # Adjust font size if necessary
        legend.title = element_blank(),
        legend.position = "bottom"  # Move legend to the bottom
        
        )  # Optionally remove legend title
