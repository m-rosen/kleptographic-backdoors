'''
    Written by Miriam Rosén in 2023
'''
from sts_parse import *

import matplotlib.pyplot as plt
import sys

# Adjust font sizes ----------------------------------------------------------
plt.rcParams.update({'figure.autolayout': True})
SMALL_SIZE = 14
MEDIUM_SIZE = 16
BIGGER_SIZE = 18

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
# --------------------------------------------------------------------------

file = sys.argv[1]
data = sts_parse(file)

props = [ item.proportion[0]/item.proportion[1] for item in data]

props_per_test = []
spread_upper = []
spread_lower = []

tests = ['Frequency', 'BlockFrequency','CumulativeSums', 'Runs', 'LongestRun',
         'Rank', 'FFT', 'NonOverlappingTemplate', 'OverlappingTemplate', 'Universal',
         'ApproximateEntropy','RandomExcursions','RandomExcursionsVariant','Serial', 'LinearComplexity']

for name in tests:
    p = [item.proportion[0]/item.proportion[1] for item in filter(lambda x: x.name == name, data)]
    mean = sum(p)/len(p)
    spread_upper.append(max(p) - mean)
    spread_lower.append(mean - min(p))
    props_per_test.append(mean)

ps  = [item.p for item in data ]


# Scatter of proportion of passing sequences per test type (15)
# ---------------------------------------------------------------------------
# Limits for alpha = 0.01
mid = 0.99
diff = 0.0094392

plt.axhline(y=mid, color='gray', linestyle=':', label="y = 0.99")
plt.axhline(y=mid+diff, color='r', linestyle='--')
plt.axhline(y=mid-diff, color='r', linestyle='--')

x = [i for i in range(1, 15 + 1)]
plt.scatter(x, props_per_test)
plt.errorbar(x, props_per_test, yerr=[spread_lower, spread_upper], fmt="o")

plt.xlabel("Test nr")
plt.ylabel("Proportion")

plt.xticks([i for i in range(0, 16)], labels=['']+ [i for i in range(1, 16)])
plt.yticks([0.98 + i*0.01 for i in range(3)])

plt.savefig(f"{file}_prop_scatter.pdf")
plt.close()
# ---------------------------------------------------------------------------


# Histogram of p-values
# ---------------------------------------------------------------------------
bins = [i*0.1 for i in range(0, 10 + 1)]
plt.hist(ps, bins)
plt.ylabel("Frequency")
plt.xlabel("p-value")
plt.savefig(f"{file}_p-values.pdf")
plt.close()
# ---------------------------------------------------------------------------


# Scatter of p-values
# ---------------------------------------------------------------------------
x = [i for i in range(0, len(ps))]
plt.scatter(x, ps)
plt.axhline(y=0.0001, color='r', linestyle='--', label="y = 0.0001")
plt.xlabel("Test nr")
plt.ylabel("p-value")
plt.legend()
plt.savefig(f"{file}_p-values_scatter.pdf")
plt.close()
# ---------------------------------------------------------------------------

