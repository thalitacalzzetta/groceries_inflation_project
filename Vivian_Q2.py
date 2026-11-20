# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 13:31:51 2026

@author: Vi Pham
"""

import pandas as pd

# Groceries items
df_groceries = pd.read_csv("us_average_prices_monthly (1.csv", sep=None, engine="python")

# Convert dates to datetime for consistent monthly alignment across datasets.

df_groceries["date"] = pd.to_datetime(df_groceries["date"])

# Focus on January 2015 through December 2025 (11 calendar years).

# Filtering data.

df_groceries = df_groceries[df_groceries["date"] < "2026-01-01"]

# Creating pivot table.

df_groceries__items = pd.pivot_table(df_groceries, values="price", index='date' , columns="item")

# Checking null values.

df_groceries__items.isna().sum().sort_values(ascending=False)

# Calculate the proportion of missing monthly prices for each item.

df_groceries__items.isna().mean().sort_values(ascending=False)

# Retain items with at most 9% missing observations (up to 11 of 132 months).
# This is a project-specific threshold, not a universal rule; 50 of 74 items remain.
# Note that overall completeness does not guarantee complete coverage at both endpoints.

df_groceries__items = df_groceries__items.loc[:, df_groceries__items.isna().mean() <= 0.09]

# Recheck missingness after filtering items:

df_groceries__items.isna().mean().sort_values(ascending=False)

# Examine missingness by month; many items are missing exactly one observation.

df_groceries__items.isna().sum(axis=1).sort_values(ascending=False)

# October 2025 is missing 47 of the 50 retained item prices.
# Fill internal gaps by linear interpolation; do not extrapolate at series endpoints.
# October 2025 estimates are especially uncertain and should be flagged in our presenation.

df_groceries__items = df_groceries__items.interpolate(method="linear", limit_area="inside")

# Verify missing values after interpolation. Preserve the original long-form

df_groceries__items.isna().sum()

#------

# Pivot Table
df_categories = pd.pivot_table(df_groceries, values="price", index='date' , columns="category")

# Checking null values.

df_categories.isna().sum().sort_values(ascending=False)

# Calculate the proportion of missing monthly prices for each item.

df_categories.isna().mean().sort_values(ascending=False)

# Retain items with at most 9% missing observations.
# Note that overall completeness does not guarantee complete coverage at both endpoints.

df_categories = df_categories.loc[:, df_categories.isna().mean() <= 0.09]

# Recheck missingness after filtering items:

df_categories.isna().mean().sort_values(ascending=False)

# Same case from the items dataset. 
# Fill internal gaps by linear interpolation; do not extrapolate at series endpoints.
# October 2025 estimates are especially uncertain and should be flagged in our presentation.

df_categories = df_categories.interpolate(method="linear", limit_area="inside")

# Verify missing values after interpolation. Preserve the original long-form

df_categories.isna().sum()

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.width',None)

print(df_categories)
#------

# CPI
df_index = pd.read_csv("Consumer_Price_Index.csv", sep=None, engine="python")

# Checking data type.

df_index.info()

# Transforming "observation_date" into date type.

df_index["observation_date"] = pd.to_datetime(df_index["observation_date"])
df_index.info()

# Setting new columns names.

columns = {
    "observation_date": "date",
    "CPIULFSL": "Consumer_Price_Index"}

df_index.rename(columns=columns, inplace=True)

# Filtering Data (2015-2025)

df_index = df_index[(df_index['date'] > "2014-12-01") & (df_index['date'] < "2026-01-01")]
df_index

# Checking missing values.

df_index.isna().sum()

# Checking which month is null.

df_index[df_index["Consumer_Price_Index"].isna()]

# October 2025 is missing in the CPI-excluding-food series (CPIULFSL).
# Estimate the missing index observation by linear interpolation. Highlight this situation in our presentation. 

df_index = df_index.interpolate(method="linear", limit_area="inside")
df_index.isna().sum()

# Setting "date" as the index of the dataset.

df_index = df_index.set_index("date")


# -----

# Average Wage
df_wage = pd.read_csv("Average_Hourly_Wages.csv", sep=None, engine="python")

# Checking Data type

df_wage.info()

# Transforming "date" into date time. 

df_wage["observation_date"] = pd.to_datetime(df_wage["observation_date"])
df_wage.info()

# Setting new column names.

columns_wage = {
    "observation_date": "date",
    "CES0500000003": "Average_Hourly_Wage"
}

df_wage.rename(columns=columns_wage, inplace=True)

# Filtering Data (2015 - 2025).

df_wage = df_wage[(df_wage["date"] > "2014-12-01") & (df_wage["date"] < "2026-01-01")]
df_wage

# Checking missing values.

df_wage.isna().sum()

# Setting "date" as the index for the dataset.

df_wage = df_wage.set_index("date")
df_wage


# Join all three datasets on their monthly date indexes (inner join).
# Confirm the result has the expected 132 months and 52 columns, and check missing values.

df_join = [df_index, df_wage]

df_project_items = df_groceries__items.join(df_join, how="inner")
df_project_items.isna().sum()

# Join all three datasets for categories.
# Confirm the result has the expected 132 months and 52 columns, and check missing values.

df_join_cat = [df_index, df_wage]
df_project_categories = df_categories.join(df_join_cat, how="inner")
df_project_categories.isna().sum()

print(df_project_categories)
# Both datasets were created from the same original grocery dataset.
# The 9% missing-value threshold was applied independently to items
# and categories, followed by linear interpolation.
# Category averages may include items excluded from the item-level dataset.


#--------------------------------------------------------


# 1. Category basket cost: sum of item prices within each category (one unit of each item)
item_to_cat = (df_groceries[["item", "category"]]
               .drop_duplicates()
               .set_index("item")["category"]
               .reindex(df_groceries__items.columns))

basket = df_groceries__items.T.groupby(item_to_cat).sum().T
n_items = item_to_cat.value_counts()

# 2. High-inflation months (same CPI flag as before) -- 
# 4% given the inflation rates have been generally steady at 2-3% historically / allows us to see impact of COVID

THRESHOLD = 4.0
cpi_yoy = df_index["Consumer_Price_Index"].pct_change(12) * 100
high_months = cpi_yoy[cpi_yoy >= THRESHOLD].index

print(cpi_yoy)

# 3. Baseline period
# justification for 2019: it is the most recent year before COVID-19 that we believe is most appropriate for baseline
# also shows the impact of COVID-19

BASE_START, BASE_END = "2019-01-01", "2019-12-01"
baseline = basket.loc[BASE_START:BASE_END].mean()

# 4. Compare against baseline: high-inflation average, peak, and latest month
high_avg = basket.loc[high_months].mean()
peak     = basket.loc[high_months].max()
latest   = basket.iloc[-1]

results = pd.DataFrame({
    "n_items": n_items,
    "baseline": baseline,
    "usd_change_high": high_avg - baseline,
    "pct_change_high": (high_avg / baseline - 1) * 100,
    "usd_change_peak": peak - baseline,
    "pct_change_peak": (peak / baseline - 1) * 100,
    "usd_change_latest": latest - baseline,
    "pct_change_latest": (latest / baseline - 1) * 100,
})

# Dollar change per item, since categories have different numbers of items
results["usd_change_high_per_item"] = results["usd_change_high"] / results["n_items"]

print(results.sort_values("pct_change_high", ascending=False).round(2))
print(results.sort_values("pct_change_peak", ascending = False))
print(peak)


# ______________________________________________________________________________

# Visualization
import matplotlib.pyplot as plt

# Chart 1: Which categories rose the most during high inflation?
order = results.sort_values("pct_change_high", ascending=True)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(order.index, order["pct_change_high"])
for bar, val in zip(bars, order["pct_change_high"]):
    ax.text(val + 1, bar.get_y() + bar.get_height() / 2, f"{val:.0f}%", va="center")
ax.set_xlabel("Avg high-inflation period prices vs. baseline (%)")
ax.set_ylabel("Grocery categories")
ax.set_title("Average % change during high-inflation months")
plt.tight_layout()
plt.show()

# Chart 2: High-inflation average vs. peak vs. latest month
# high-inflation average -- take the months of high inflation CPI and average the costs
cmp = (results.sort_values("pct_change_high", ascending=False)
       [["pct_change_high", "pct_change_peak", "pct_change_latest"]])
cmp.columns = ["High-inflation avg", "Peak", "Latest month"]

ax = cmp.plot(kind="bar", figsize=(12, 6))
ax.set_ylabel("% change vs. baseline")
ax.set_title("High-inflation average vs. peak vs. latest")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# Chart 3: Price paths over time (baseline = 100) with CPI inflation above
basket_idx = basket / basket.loc[BASE_START:BASE_END].mean() * 100

# Eggs (peak ~446) would squash the other lines, so plot it separately
outliers = ["Eggs"]
fig, axes = plt.subplots(2, 1, figsize=(12, 9), sharex=True,
                         gridspec_kw={"height_ratios": [1, 2.5]})

axes[0].plot(cpi_yoy.index, cpi_yoy, color="black")
axes[0].axhline(THRESHOLD, linestyle="--", color="red")
axes[0].set_ylabel("CPI YoY %")
axes[0].set_title("Inflation (top) and price change over time: 2015 - 2025 (bottom)")

for col in basket_idx.columns.drop(outliers):
    axes[1].plot(basket_idx.index, basket_idx[col], label=col)
axes[1].axhline(100, color="gray", linewidth=0.8)
axes[1].set_ylabel("Price change")
axes[1].legend(ncol=2, fontsize=8)

for a in axes:
    a.axvspan(high_months.min(), high_months.max(), alpha=0.15, color="red")
plt.tight_layout()
plt.show()
