# tool vs. exam scores

library(tidyverse)
library(readxl)


ToolUseExamScore <- read_excel(
  "Data/Sharepoint_Usage_and_score_data.xlsx", 
  range = "A1:M88"
) %>% select(-Name)


# 4 studenten met lagere score in 2e zit: misschien sensitivity analyse doen
# waarbij we de hoogste van de 2 scores nemen als uitkomst
ToolUseExamScore %>% filter(Exam_score > incl_2e_zit)


# some additional variables
ToolUseExamScore <- ToolUseExamScore %>%
  mutate(
    Used_3D = factor(Used_3D, c(0, 1), c("no","yes")),
    number_features = Lowerlimb_Blanc + Lowerlimb_Annotations + 
      Lowerlimb_Quiz + Upperlimb_Blanc + Upperlimb_Annotations + Upperlimb_Quiz
  ) 


# visual explorations of data
ToolUseExamScore %>%
  ggplot(aes(Time_minutes, incl_2e_zit)) +
  geom_jitter(height = 0, width = 3) +
  geom_smooth(method = "loess") +
  geom_smooth(method = "lm", color = "black", se = F, lty = 2) +
  scale_y_continuous(limits = c(0, 100)) +
  geom_hline(yintercept = 50, lty = 3) +
  labs(x = "Time spent with tool (min)", 
       y = "Exam score (incl. 2nd chance)",
       color = "Tool used") +
  theme_classic()

ToolUseExamScore %>%
  ggplot(aes(Time_minutes, incl_2e_zit, group = Used_3D, color = Used_3D,
             fill = Used_3D)) +
  geom_jitter(width = 3, height = 0) +
  geom_smooth(method = "loess") +
  geom_smooth(method = "lm", color = "black", se = F, lty = 2) +
  scale_y_continuous(limits = c(0, 100)) +
  geom_hline(yintercept = 50, lty = 3) +
  labs(x = "Time spent with tool (min)", 
       y = "Exam score (incl. 2nd chance)",
       color = "Tool used", fill = "Tool used") +
  theme_classic()

ToolUseExamScore %>%
  ggplot(aes(Time_minutes, incl_2e_zit, color = factor(number_features))) +
  geom_jitter(height = 0, width = 3) +
  geom_smooth(method = "lm", se = F) +
  scale_y_continuous(limits = c(0, 100)) +
  geom_hline(yintercept = 50, lty = 3) +
  labs(x = "Time spent with tool (min)", 
       y = "Exam score (incl. 2nd chance)",
       color = "Nr. of features used") +
  theme_classic()

ToolUseExamScore %>%
  ggplot(aes(Time_minutes, incl_2e_zit, color = factor(Study))) +
  geom_jitter(height = 0, width = 3) +
  geom_smooth(method = "lm", se = F) +
  scale_y_continuous(limits = c(0, 100)) +
  geom_hline(yintercept = 50, lty = 3) +
  labs(x = "Time spent with tool (min)", 
       y = "Exam score (incl. 2nd chance)",
       color = "Study") +
  theme_classic()



# Pearson correlation (all)
# r = 0.33, p = 0.002
with(ToolUseExamScore,
     cor.test(Time_minutes, incl_2e_zit))

# Pearson correlation (within students who used the tool)
# r = 0.47, p < 0.001
with(ToolUseExamScore %>% filter(Used_3D == "yes"),
     cor.test(Time_minutes, incl_2e_zit))



### Welch 2-sample t-test: comparison of time spent on the website between LO/Kine
#   mean difference = 9.7 (95% CI [-45.4; 64.8]), p = 0.73
with(ToolUseExamScore,
     t.test(Time_minutes ~ Study))
# LO LO LO
#     Kiné Kiné Kiné
# LO LO LO 
#     Kiné Kiné Kiné
# :-) 



### Welch 2-sample t-test: comparison of score between users and non-users
#   mean difference = 3.2 (95% CI [-9.8; 3.4]), p = 0.34
with(ToolUseExamScore,
     t.test(incl_2e_zit ~ Used_3D))



### linear model (within students who used the tool)

m0 <- lm(
  incl_2e_zit ~ I(Time_minutes/60),
  data = ToolUseExamScore %>% filter(Used_3D == "yes")
)
summary(m0)

m1 <- lm(
  incl_2e_zit ~ I(Time_minutes/60) + Study,
  data = ToolUseExamScore %>% filter(Used_3D == "yes")
)
summary(m1)

m2 <- lm(
  incl_2e_zit ~ I(Time_minutes/60) + number_features,
  data = ToolUseExamScore %>% filter(Used_3D == "yes")
)
summary(m2)



### nested linear model (all students)

m3 <- lm(
  incl_2e_zit ~ Used_3D / I(Time_minutes/60),
  data = ToolUseExamScore %>%
    mutate(
      Time_minutes = case_when(Used_3D == "yes" ~ Time_minutes - 300,
                               TRUE ~ Time_minutes)
    )
)
summary(m3)
confint(m3)
sqrt(var(m3$residuals))




