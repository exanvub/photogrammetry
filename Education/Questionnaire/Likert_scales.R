# Load necessary libraries
library(readxl)
library(likert)
library(ggplot2)
library(tidyverse)

# Define the file path
file_path <- "Data/Use of Real Life 3D Models in Education.xlsx"

# Read the sheet names
sheets <- excel_sheets(file_path)

# Read all sheets into a list of data frames
data_list <- lapply(sheets, function(sheet) read_excel(file_path, sheet = sheet))

# Assume we are working with the first sheet for this example
data <- data_list[[1]]

# Preview the column names
print("column names in data:")
print(colnames(data))

# Manually specify which columns to use for the Likert scale plot
overall_experience <- c(7, 8, 9, 10, 11, 12, 13, 14)  # Update this based on the correct column numbers

# Extract the selected columns for the Likert data
overall_experience_likert_data <- data[, overall_experience]

# Convert the columns to factors with ordered levels (assuming a 5-point Likert scale)
overall_experience_likert_data <- data.frame(lapply(overall_experience_likert_data, factor, 
                                 levels = c("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"), 
                                 ordered = TRUE))

# Create more readable column names for the plot
colnames(overall_experience_likert_data) <- c("Sufficient detail", 
                           "Enhances understanding of spatial relationship vs books", 
                           "Enhances understanding of spatial relationship vs other 3D software", 
                           "Contributes to learning experience", 
                           "Valuable during dissection courses",
                           "Valuable during exam studies",
                           "Would recommend",
                           "Worthwhile the investment"
                           )

# Create the Likert object
overall_experience_likert_object <- likert(overall_experience_likert_data)

# Reorder items manually
overall_experience_order_of_items <- colnames(overall_experience_likert_data)

# Adjust plot to respect the order of items
plot(overall_experience_likert_object, text.size = 5) +
  ggtitle("Overall Experience") +
  theme_minimal() +
  scale_x_discrete(limits = rev(overall_experience_order_of_items))

# Adjust plot to respect the order of items and tweak theme for readability
plot(overall_experience_likert_object,text.size = 4) +
  ggtitle("Overall Experience") +
  theme_minimal(base_size = 12) +   # Adjust base text size for readability
  scale_x_discrete(limits = rev(overall_experience_order_of_items)) +  # Reversing item order for display
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),  # Center the title and make it bold
    axis.text.y = element_text(size = 14),  # Adjust axis text size
    legend.position = "bottom"  # Move legend to the bottom
  )


#---------

# Define the columns for "Ease of Use" questions
ease_of_use_columns <- c(27, 28, 29, 30, 31, 32)  # Update as needed

# Extract the selected columns for the Likert data
ease_of_use_data <- data[, ease_of_use_columns]

# Convert the columns to factors with ordered levels (assuming a 5-point Likert scale)
ease_of_use_data <- data.frame(lapply(ease_of_use_data, factor, 
                                      levels = c("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"), 
                                      ordered = TRUE))

# Create more readable column names for the plot
colnames(ease_of_use_data) <- c("The website is easily accessible", 
                                "The website is structured and clearly arranged", 
                                "The 3D models loaded successfully on my device", 
                                "It took too long to load the models", 
                                "It was easy to navigate the 3D models", 
                                "Prefer use of a tablet or smartphone over a laptop for this type of tool")

# Create the Likert object
ease_of_use_likert <- likert(ease_of_use_data)

# Reorder items manually
ease_of_use_order_of_items <- colnames(ease_of_use_data)

# Plot the Likert scale responses
plot(ease_of_use_likert) +
  ggtitle("Ease of Use") +
  theme_minimal() +
  scale_x_discrete(limits = rev(ease_of_use_order_of_items))

# Adjust plot to respect the order of items and tweak theme for readability
plot(ease_of_use_likert,text.size = 4) +
  ggtitle("Ease of Use") +
  theme_minimal(base_size = 12) +   # Adjust base text size for readability
  scale_x_discrete(limits = rev(ease_of_use_order_of_items)) +  # Reversing item order for display
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),  # Center the title and make it bold
    axis.text.y = element_text(size = 14),  # Adjust axis text size
    legend.position = "bottom"  # Move legend to the bottom
  )

#------------------

# Manually specify which columns to use for the second Likert scale plot
lighting_columns <- c(15, 16, 17, 18, 19, 20)

# Extract the selected columns for the Likert data
lighting_likert_data <- data[, lighting_columns]

# Convert the selected columns to factors with ordered levels (specified options)
lighting_likert_data <- data.frame(lapply(lighting_likert_data, factor, 
                                   levels = c("Diffuse lighting", "Rather Diffuse lighting", "Equal on both", "Rather Polarized Filter", "Polarized Filter"), 
                                   ordered = TRUE))

# Create more readable column names for the plot
colnames(lighting_likert_data) <- c("Muscles are easier to recognise", 
                             "Muscles are more defined", 
                             "Arteries and nerves are easier to recognise", 
                             "Has the most detail", 
                             "Is most photorealistic", 
                             "My general preference goes to"
                             )

# Create the Likert object with grouping
lighting_likert_object <- likert(lighting_likert_data)

# Reorder items manually
lighting_order_of_items <- colnames(lighting_likert_data)

# Adjust plot to respect the order of items
plot(lighting_likert_object) +
  ggtitle("Polarized filter vs Diffuse lighting") +
  theme_minimal() +
  scale_x_discrete(limits = rev(lighting_order_of_items))

plot(lighting_likert_object,text.size = 4) +
  ggtitle("Polarized filter vs Diffuse lighting") +
  theme_minimal(base_size = 12) +   # Adjust base text size for readability
  scale_x_discrete(limits = rev(lighting_order_of_items)) +  # Reversing item order for display
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),  # Center the title and make it bold
    axis.text.y = element_text(size = 14),  # Adjust axis text size
    legend.position = "bottom"  # Move legend to the bottom
  )


#-----------------
# Define the columns for annotations and quiz questions
annot_quiz_columns <- c(21, 22, 23, 24, 25)  # Update as needed

# Extract the selected columns for the Likert data
annot_quiz_data <- data[, annot_quiz_columns]

# Convert the columns to factors with ordered levels (assuming a 5-point Likert scale)
annot_quiz_data <- data.frame(lapply(annot_quiz_data, factor, 
                                      levels = c("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"), 
                                      ordered = TRUE))

# Create more readable column names for the plot
colnames(annot_quiz_data) <- c("Importance of Annotations",
                               "3D models are useless without annotations",                                                                                                   
                               "Coloured dots are an appropriate method",                                                            
                               "Value of Quizzes",                                                                                                                           
                               "Relevance of Quiz Questions")

# Create the Likert object
annot_quiz_likert <- likert(annot_quiz_data)

# Reorder items manually
annot_quiz_order_of_items <- colnames(annot_quiz_data)

# Plot the Likert scale responses
plot(annot_quiz_likert) +
  ggtitle("Annotations and Quiz") +
  theme_minimal() +
  scale_x_discrete(limits = rev(annot_quiz_order_of_items))

plot(annot_quiz_likert,text.size = 4) +
  ggtitle("Annotations and Quiz") +
  theme_minimal(base_size = 12) +   # Adjust base text size for readability
  scale_x_discrete(limits = rev(annot_quiz_order_of_items)) +  # Reversing item order for display
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),  # Center the title and make it bold
    axis.text.y = element_text(size = 14),  # Adjust axis text size
    legend.position = "bottom"  # Move legend to the bottom
  )
#-----------
