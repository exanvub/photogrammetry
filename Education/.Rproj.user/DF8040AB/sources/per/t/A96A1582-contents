# Load required libraries
library(readxl)
library(likert)
library(ggplot2)
library(dplyr)
library(tidyr)
library(purrr)
library(FSA)
library(knitr)

# Load the data
file_path <- "Data/Use of Real Life 3D Models in Education.xlsx"
sheets <- excel_sheets(file_path)
data_list <- lapply(sheets, function(sheet) read_excel(file_path, sheet = sheet))
data <- data_list[[1]]

print("Column names in data:")
print(colnames(data))

# specify which columns to use for the Likert scale plot
overall_experience <- c(7, 8, 9, 10, 11, 12, 13, 14)
ease_of_use_columns <- c(27, 28, 29, 30, 31, 32)
annot_quiz_columns <- c(21, 22, 23, 24, 25)
lighting_columns <- c(15, 16, 17, 18, 19, 20)

#------------- Overall Experience:

overall_experience_likert_data <- data[, overall_experience]
overall_experience_likert_data$Group <- data[["I am a"]]

# Convert selected columns to factors with ordered levels (5-point Likert scale)
overall_experience_likert_data <- data.frame(lapply(overall_experience_likert_data[, -ncol(overall_experience_likert_data)], factor, 
                                                    levels = c("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"), 
                                                    ordered = TRUE))

# Add the grouping column back to the data frame
overall_experience_likert_data$Group <- data[["I am a"]]

# Create more readable column names for the plot
colnames(overall_experience_likert_data) <- c("Sufficient detail", 
                                              "Enhances understanding vs books", 
                                              "Enhances understanding vs other 3D software", 
                                              "Contributes to learning experience", 
                                              "Valuable during dissection courses",
                                              "Valuable during exam studies",
                                              "Would recommend",
                                              "Worthwhile the investment",
                                              "Group")

# Create the Likert object with grouping
overall_experience_likert_object <- likert(overall_experience_likert_data[, -ncol(overall_experience_likert_data)], grouping = overall_experience_likert_data$Group)

# Plot Likert data
plot(overall_experience_likert_object) +
  ggtitle("Overall Experience by Group") +
  theme_minimal()

# Kruskal-Wallis test for Overall Experience
data_long <- overall_experience_likert_data %>%
  pivot_longer(cols = -Group, names_to = "Item", values_to = "Response")

kruskal_test <- function(item_data) {
  kruskal.test(Response ~ Group, data = item_data)
}

# Apply the Kruskal-Wallis test to each Likert item
test_results <- data_long %>%
  group_by(Item) %>%
  nest() %>%
  mutate(test = map(data, kruskal_test)) %>%
  mutate(p_value = map_dbl(test, ~.x$p.value)) %>%
  select(-data, -test)

# Print Kruskal-Wallis test results
kable(test_results, digits = 3, caption = "Kruskal-Wallis Test Results for Likert Scale Items (Overall Experience)")

# Dunn's test:
dunn_test <- function(item_data) {
  dunnTest(Response ~ Group, data = item_data, method = "bonferroni")
}

# Apply Dunn's test to each Likert item where Kruskal-Wallis was significant
posthoc_results <- data_long %>%
  group_by(Item) %>%
  nest() %>%
  mutate(test = map(data, kruskal_test)) %>%
  filter(map_dbl(test, ~.x$p.value) < 0.05) %>%
  mutate(posthoc = map(data, dunn_test)) %>%
  select(-data, -test)

# Extract and print post-hoc results
posthoc_results_summary <- posthoc_results %>%
  mutate(posthoc_summary = map(posthoc, ~ .x$comparisons)) %>%
  select(Item, posthoc_summary) %>%
  unnest(posthoc_summary)

kable(posthoc_results_summary, digits = 3, caption = "Dunn's Test Pairwise Comparisons (Overall Experience)")

#--------------- Ease of Use:
ease_of_use_likert_data <- data[, ease_of_use_columns]
ease_of_use_likert_data$Group <- data[["I am a"]]

# Convert selected columns to factors with ordered levels (5-point Likert scale)
ease_of_use_likert_data <- data.frame(lapply(ease_of_use_likert_data[, -ncol(ease_of_use_likert_data)], factor, 
                                             levels = c("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"), 
                                             ordered = TRUE))

# Add the grouping column back to the data frame
ease_of_use_likert_data$Group <- data[["I am a"]]

# readable column names for the plot
colnames(ease_of_use_likert_data) <- c("The website is easily accessible", 
                                       "The website is structured and clearly arranged", 
                                       "The 3D models loaded successfully on my device", 
                                       "It took too long to load the models", 
                                       "It was easy to navigate the 3D models", 
                                       "I prefer the use of a tablet or smartphone over a laptop for this type of tool",
                                       "Group")

# Create the Likert object with grouping
ease_of_use_likert_object <- likert(ease_of_use_likert_data[, -ncol(ease_of_use_likert_data)], grouping = ease_of_use_likert_data$Group)

# Plot the Likert data
plot(ease_of_use_likert_object) +
  ggtitle("Ease of Use by Group") +
  theme_minimal()

# Kruskal-Wallis test for Ease of Use:
data_long_ease <- ease_of_use_likert_data %>%
  pivot_longer(cols = -Group, names_to = "Item", values_to = "Response")

# Apply the Kruskal-Wallis test to each Likert item
test_results_ease <- data_long_ease %>%
  group_by(Item) %>%
  nest() %>%
  mutate(test = map(data, kruskal_test)) %>%
  mutate(p_value = map_dbl(test, ~.x$p.value)) %>%
  select(-data, -test)

# Print Kruskal-Wallis test results
kable(test_results_ease, digits = 3, caption = "Kruskal-Wallis Test Results for Likert Scale Items (Ease of Use)")

# Apply Dunn's test to each Likert item where Kruskal-Wallis was significant
posthoc_results_ease <- data_long_ease %>%
  group_by(Item) %>%
  nest() %>%
  mutate(test = map(data, kruskal_test)) %>%
  filter(map_dbl(test, ~.x$p.value) < 0.05) %>%
  mutate(posthoc = map(data, dunn_test)) %>%
  select(-data, -test)

# Extract and print post-hoc results
posthoc_results_summary_ease <- posthoc_results_ease %>%
  mutate(posthoc_summary = map(posthoc, ~ .x$comparisons)) %>%
  select(Item, posthoc_summary) %>%
  unnest(posthoc_summary)

kable(posthoc_results_summary_ease, digits = 3, caption = "Dunn's Test Pairwise Comparisons (Ease of Use)")

#----------------- Annotations and Quiz:
annot_quiz_likert_data <- data[, annot_quiz_columns]
annot_quiz_likert_data$Group <- data[["I am a"]]

# Convert the selected columns to factors with ordered levels (5-point Likert scale)
annot_quiz_likert_data <- data.frame(lapply(annot_quiz_likert_data[, -ncol(annot_quiz_likert_data)], factor, 
                                            levels = c("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"), 
                                            ordered = TRUE))

# Add the grouping column back to the data frame
annot_quiz_likert_data$Group <- data[["I am a"]]

# readable column names for the plot
colnames(annot_quiz_likert_data) <- c("Importance of Annotations",
                                      "3D models are useless without annotations",                                                                                                   
                                      "Coloured dots are an appropriate method",                                                            
                                      "Value of Quizzes",                                                                                                                           
                                      "Relevance of Quiz Questions",
                                      "Group")

# Create the Likert object with grouping
annot_quiz_likert_object <- likert(annot_quiz_likert_data[, -ncol(annot_quiz_likert_data)], grouping = annot_quiz_likert_data$Group)

# Plot the Likert data
plot(annot_quiz_likert_object) +
  ggtitle("Annotations and Quiz by Group") +
  theme_minimal()

# Prepare the data for Kruskal-Wallis test for Annotations and Quiz
data_long_annot_quiz <- annot_quiz_likert_data %>%
  pivot_longer(cols = -Group, names_to = "Item", values_to = "Response")

# Apply the Kruskal-Wallis test to each Likert item
test_results_annot_quiz <- data_long_annot_quiz %>%
  group_by(Item) %>%
  nest() %>%
  mutate(test = map(data, kruskal_test)) %>%
  mutate(p_value = map_dbl(test, ~.x$p.value)) %>%
  select(-data, -test)

# Print Kruskal-Wallis test results
kable(test_results_annot_quiz, digits = 3, caption = "Kruskal-Wallis Test Results for Likert Scale Items (Annotations and Quiz)")

# Apply Dunn's test to each Likert item where Kruskal-Wallis was significant
posthoc_results_annot_quiz <- data_long_annot_quiz %>%
  group_by(Item) %>%
  nest() %>%
  mutate(test = map(data, kruskal_test)) %>%
  filter(map_dbl(test, ~.x$p.value) < 0.05) %>%
  mutate(posthoc = map(data, dunn_test)) %>%
  select(-data, -test)

# Extract and print post-hoc results
posthoc_results_summary_annot_quiz <- posthoc_results_annot_quiz %>%
  mutate(posthoc_summary = map(posthoc, ~ .x$comparisons)) %>%
  select(Item, posthoc_summary) %>%
  unnest(posthoc_summary)

kable(posthoc_results_summary_annot_quiz, digits = 3, caption = "Dunn's Test Pairwise Comparisons (Annotations and Quiz)")

#---------------- Lighting:
lighting_likert_data <- data[, lighting_columns]
lighting_likert_data$Group <- data[["I am a"]]

# Convert the selected columns to factors with ordered levels
lighting_likert_data <- data.frame(lapply(lighting_likert_data[, -ncol(lighting_likert_data)], factor, 
                                          levels = c("Diffuse lighting", "Rather Diffuse lighting", "Equal on both", "Rather Polarized Filter", "Polarized Filter"), 
                                          ordered = TRUE))

# Add the grouping column back to the data frame
lighting_likert_data$Group <- data[["I am a"]]

# Create more readable column names for the plot
colnames(lighting_likert_data) <- c("Muscles are easier to recognise", 
                                    "Muscles are more defined", 
                                    "Arteries and nerves are easier to recognise", 
                                    "Has the most detail", 
                                    "Is most photorealistic", 
                                    "My general preference goes to",
                                    "Group")

# Create the Likert object with grouping
lighting_likert_object <- likert(lighting_likert_data[, -ncol(lighting_likert_data)], grouping = lighting_likert_data$Group)

# Plot the Likert data
plot(lighting_likert_object) +
  ggtitle("Polarized filter vs Diffuse lighting by Group") +
  theme_minimal()

# Prepare the data for Kruskal-Wallis test for Lighting
data_long_lighting <- lighting_likert_data %>%
  pivot_longer(cols = -Group, names_to = "Item", values_to = "Response")

# Apply the Kruskal-Wallis test to each Likert item
test_results_lighting <- data_long_lighting %>%
  group_by(Item) %>%
  nest() %>%
  mutate(test = map(data, kruskal_test)) %>%
  mutate(p_value = map_dbl(test, ~.x$p.value)) %>%
  select(-data, -test)

# Print Kruskal-Wallis test results
kable(test_results_lighting, digits = 3, caption = "Kruskal-Wallis Test Results for Likert Scale Items (Lighting)")

# Apply Dunn's test to each Likert item where Kruskal-Wallis was significant
posthoc_results_lighting <- data_long_lighting %>%
  group_by(Item) %>%
  nest() %>%
  mutate(test = map(data, kruskal_test)) %>%
  filter(map_dbl(test, ~.x$p.value) < 0.05) %>%
  mutate(posthoc = map(data, dunn_test)) %>%
  select(-data, -test)

# Extract and print post-hoc results
posthoc_results_summary_lighting <- posthoc_results_lighting %>%
  mutate(posthoc_summary = map(posthoc, ~ .x$comparisons)) %>%
  select(Item, posthoc_summary) %>%
  unnest(posthoc_summary)

kable(posthoc_results_summary_lighting, digits = 3, caption = "Dunn's Test Pairwise Comparisons (Lighting)")

