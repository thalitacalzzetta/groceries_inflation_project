# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 11:17:00 2026

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



# ________________________________________
# item prices


# Step 1: first and last price of every item
first_price = df_groceries__items.iloc[0]
last_price  = df_groceries__items.iloc[-1]

print(first_price, last_price)

# Step 2: build a results table with both dollar and percent change
item_results = pd.DataFrame({"first_price": first_price, "last_price": last_price})
item_results["usd_change"] = item_results["last_price"] - item_results["first_price"]
item_results["pct_increase"] = (item_results["last_price"] / item_results["first_price"] - 1) * 100

print(item_results)

# Step 3: add category and unit so each number has context
item_info = (df_groceries[["item", "category", "unit"]]
             .drop_duplicates()
             .set_index("item"))
item_results = item_results.join(item_info)

print(item_results)

# Step 4: rank by percent increase and keep the top 10
item_results = item_results.sort_values("pct_increase", ascending=False)
top5 = item_results.head(5)
print(top5.round(2))


# Step 5: rebase the top 10 to Jan 2015 = 100 for the line chart
top5_names = top5.index
rebased = df_groceries__items[top5_names] / df_groceries__items[top5_names].iloc[0] * 100

# Step 6: draw both charts side by side
import matplotlib.pyplot as plt
fig, axes = plt.subplots(figsize=(12, 6))

top5_sorted = top5.sort_values("pct_increase")
axes.barh(top5_sorted.index, top5_sorted["pct_increase"])
for i, v in enumerate(top5_sorted["pct_increase"]):
    axes.text(v + 0.5, i, f"{v:.0f}%", va="center")
axes.set_xlabel("% price increase, Jan 2015 to Dec 2025")
axes.set_title("Top 5 items by % increase")

plt.tight_layout()
plt.show()