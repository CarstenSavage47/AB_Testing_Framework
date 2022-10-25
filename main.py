# A/B Testing Framework
# Thank you to Bondi Crypto for providing this framework:
# https://bondicrypto.medium.com/implementing-a-b-tests-in-python-514e9eb5b3a1

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, chi2
import numpy as np
import math
import statsmodels.stats.api as sms
import scipy.stats as st

AB_DF = pandas.read_csv('/Users/carstenjuliansavage/Desktop/R Working Directory/Useful Datasets/ab_data.csv')

# We can see that there are some mistakes in the DF. The control should have the old_page, not new_page.

(AB_DF
 .query('group in ["control"] & landing_page in ["new_page"]')
 )

# Drop instances in which group = control and landing page = new page,
# And drop instances in which group = treatment and landing page = old page

NONSENSICAL_1 = (AB_DF["group"] == "control") & (AB_DF["landing_page"] == "new_page")
INDEX_TO_DROP_1 = AB_DF[NONSENSICAL_1].index
AB_DF = AB_DF.drop(INDEX_TO_DROP_1)

NONSENSICAL_2 = (AB_DF["group"] == "treatment") & (AB_DF["landing_page"] == "old_page")
INDEX_TO_DROP_2 = AB_DF[NONSENSICAL_2].index
AB_DF = AB_DF.drop(INDEX_TO_DROP_2)

# Total users
(AB_DF
 .agg({'user_id':pandas.Series.count})
 )

# Unique users
(AB_DF
 .groupby(['user_id'])['user_id']
 .count()
 .to_frame('Count_of_User_ID')
 .query('Count_of_User_ID > 1')
 )

# Drop the duplicate user_id value (773192)
AB_DF.drop_duplicates(subset ='user_id',keep ='first',inplace = True)


# Masking uses booleans, when applied to original array return the elements of interest.

# Show the % split between users who saw new vs old page
# Calculate pooled probability
mask_control = (AB_DF["group"] == "control")
conversions_control = AB_DF["converted"][mask_control].sum()
total_users_control = AB_DF["converted"][mask_control].count()

mask_treatment = (AB_DF["group"] == "treatment")
conversions_treatment = AB_DF["converted"][mask_treatment].sum()
total_users_treatment = AB_DF["converted"][mask_treatment].count()

print("Split of control users who saw old page vs treatment users who saw new page: ",
          round(total_users_control / AB_DF["converted"].count() * 100, 2), "% ",
          round((total_users_treatment / AB_DF["converted"].count()) * 100, 2), "%")

# count number of users who converted in each group
print("Number of control users who converted on old page: ", conversions_control)
print("Percentage of control users who converted: ",
      round((conversions_control / total_users_control) * 100, 2), "%")

mask = (AB_DF["group"] == "treatment")
print("Number of treatment users who converted on new page: ", conversions_treatment)
print("Percentage of treatment users who converted: ",
      round((conversions_treatment/ total_users_treatment) * 100, 2), "%")


#   Baseline rate — an estimate of the metric being analyzed before making any changes
#   Practical significance level — the minimum change to the baseline rate
#   ...that is useful to the business, for example an increase in the conversion
#   ...rate of 0.001% may not be worth the effort required to make the change whereas a 2% change will be
#   Confidence level — also called significance level is the probability that the null hypothesis
#   ...(experiment and control are the same) is rejected when it shouldn’t be
#   Sensitivity — the probability that the null hypothesis is not rejected when it should be

# Check what sample size is required
baseline_rate = conversions_control / total_users_control
practical_significance = 0.01 # user defined
confidence_level = 0.05 # user defined, for a 95% confidence interval
sensitivity = 0.8 # user defined

effect_size = sms.proportion_effectsize(baseline_rate, baseline_rate + practical_significance)
sample_size = sms.NormalIndPower().solve_power(effect_size = effect_size, power = sensitivity,
                                               alpha = confidence_level, ratio=1)
print("Required sample size: ", round(sample_size), " per group")

#Calculate pooled probability
mask = (AB_DF["group"] == "control")
conversions_control = AB_DF["converted"][mask].sum()
total_users_control = AB_DF["converted"][mask].count()

mask = (AB_DF["group"] == "treatment")
conversions_treatment = AB_DF["converted"][mask].sum()
total_users_treatment = AB_DF["converted"][mask].count()

prob_pooled = (conversions_control + conversions_treatment) / (total_users_control + total_users_treatment)

# Calculate pooled standard error and margin of error
se_pooled = math.sqrt(prob_pooled * (1 - prob_pooled) * (1 / total_users_control + 1 / total_users_treatment))
z_score = st.norm.ppf(1 - confidence_level / 2)
margin_of_error = se_pooled * z_score

# Calculate dhat, the estimated difference between probability of conversions in the experiment and control groups
d_hat = (conversions_treatment / total_users_treatment) - (conversions_control / total_users_control)

# Test if we can reject the null hypothesis
lower_bound = d_hat - margin_of_error
upper_bound = d_hat + margin_of_error

if practical_significance < lower_bound:
    print("Reject null hypothesis")
else:
    print("Do not reject the null hypothesis")

print("The lower bound of the confidence interval is ", round(lower_bound * 100, 2), "%")
print("The upper bound of the confidence interval is ", round(upper_bound * 100, 2), "%")

