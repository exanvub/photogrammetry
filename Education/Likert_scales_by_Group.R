library(readxl)
library(likert)
library(ggplot2)

file_path <- "Data/Use of Real Life 3D Models in Education.xlsx"

sheets <- excel_sheets(file_path)

data_list <- lapply(sheets, function(sheet) read_excel(file_path, sheet = sheet))

data <- data_list[[1]]

print("column names in data:")
print(colnames(data))

#------------------ overall_experience:
# specify which columns to use for the Likert scale plot
overall_experience <- c(7, 8, 9, 10, 11, 12, 13, 14)

overall_experience_likert_data <- data[, overall_experience]

# Include the "I am a" column for grouping
overall_experience_likert_data$Group <- data[["I am a"]]

# Convert the selected columns to factors with ordered levels (assuming a 5-point Likert scale)
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

# Plot the Likert data
plot(overall_experience_likert_object) +
  ggtitle("Overall Experience by Group") +
  theme_minimal() 

#--------------------- ease_of_use:

# specify which columns to use for the Likert scale plot
ease_of_use_columns <- c(27, 28, 29, 30, 31, 32)

ease_of_use_likert_data <- data[, ease_of_use_columns]

# Include the "I am a" column for grouping
ease_of_use_likert_data$Group <- data[["I am a"]]

# Convert the selected columns to factors with ordered levels (assuming a 5-point Likert scale)
ease_of_use_likert_data <- data.frame(lapply(ease_of_use_likert_data[, -ncol(ease_of_use_likert_data)], factor, 
                                                    levels = c("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"), 
                                                    ordered = TRUE))

# Add the grouping column back to the data frame
ease_of_use_likert_data$Group <- data[["I am a"]]

# Create more readable column names for the plot
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

#------------------------- annot_quiz:

# specify which columns to use for the Likert scale plot
annot_quiz_columns <- c(21, 22, 23, 24, 25)

annot_quiz_likert_data <- data[, annot_quiz_columns]

# Include the "I am a" column for grouping
annot_quiz_likert_data$Group <- data[["I am a"]]

# Convert the selected columns to factors with ordered levels (assuming a 5-point Likert scale)
annot_quiz_likert_data <- data.frame(lapply(annot_quiz_likert_data[, -ncol(annot_quiz_likert_data)], factor, 
                                             levels = c("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly agree"), 
                                             ordered = TRUE))

# Add the grouping column back to the data frame
annot_quiz_likert_data$Group <- data[["I am a"]]

# Create more readable column names for the plot
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

#------------------------- lighting:

# specify which columns to use for the second Likert scale plot
lighting_columns <- c(15, 16, 17, 18, 19, 20)

# Extract the selected columns for the Likert data
lighting_likert_data <- data[, lighting_columns]

# Include the "I am a" column for grouping
lighting_likert_data$Group <- data[["I am a"]]

# Convert the selected columns to factors with ordered levels (specified options)
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

#-----------------------

