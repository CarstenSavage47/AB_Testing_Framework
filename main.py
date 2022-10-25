# AB Testing Framework

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, chi2
import numpy as np

AB_DF = pandas.read_csv('/Users/carstenjuliansavage/Desktop/R Working Directory/Useful Datasets/ab_data.csv')

# We can see that there are some mistakes in the DF. The control should have the old_page, not new_page.

(AB_DF
 .query('group in ["control"] & landing_page in ["new_page"]')
 )

NONSENSICAL_1 = (AB_DF["group"] == "control") & (AB_DF["landing_page"] == "new_page")
INDEX_TO_DROP_1 = AB_DF[NONSENSICAL_1].index
AB_DF = AB_DF.drop(INDEX_TO_DROP_1)

NONSENSICAL_2 = (AB_DF["group"] == "treatment") & (AB_DF["landing_page"] == "old_page")
INDEX_TO_DROP_2 = AB_DF[NONSENSICAL_2].index
AB_DF = AB_DF.drop(INDEX_TO_DROP_2)

