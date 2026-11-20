"""
Created on Thu Nov 14 14:36:21 2026

@author: 922995473
"""

#Import libraries and load data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

grocery = pd.read_csv("us_average_prices_monthly (1.csv")
cpi = pd.read_csv("Consumer_Price_Index.csv")
wages = pd.read_csv("Average_Hourly_Wages.csv")

grocery["date"] = pd.to_datetime(grocery["date"])
cpi["observation_date"] = pd.to_datetime(cpi["observation_date"])
wages["observation_date"] = pd.to_datetime(wages["observation_date"])

print("Grocery:", grocery.shape)
print("CPI:", cpi.shape)
print("Wages:", wages.shape)

#Calculate category price changes
# Select the two comparison years
grocery["year"] = grocery["date"].dt.year

selected = grocery[grocery["year"].isin([2019, 2025])].copy()

# Average price for each item in each year
item_prices = (
    selected.groupby(
        ["category", "series_id", "year"]
    )["price"]
    .mean()
    .unstack()
)

# Keep items with prices in both years
item_prices = item_prices.dropna(subset=[2019, 2025])

# Calculate percentage change for each item
item_prices["change_pct"] = (
    (item_prices[2025] / item_prices[2019] - 1) * 100
)

# Average item percentage changes by category
category_changes = (
    item_prices.groupby(level="category")["change_pct"]
    .mean()
    .sort_values(ascending=False)
)

print(category_changes.round(2))

#Question 4: Compare grocery inflation with CPI
# Calculate annual average CPI
cpi["year"] = cpi["observation_date"].dt.year

cpi_annual = cpi.groupby("year")["CPIULFSL"].mean()

cpi_change = (
    (cpi_annual.loc[2025] / cpi_annual.loc[2019] - 1) * 100
)

print(f"CPI growth (2019-2025): {cpi_change:.2f}%")

# Identify categories above overall inflation
q4_results = pd.DataFrame({
    "Category Growth (%)": category_changes
})

q4_results["CPI Growth (%)"] = cpi_change
q4_results["Difference (pp)"] = (
    q4_results["Category Growth (%)"] - cpi_change
)

print(q4_results.round(2))

# Visualization
ax = category_changes.sort_values().plot(
    kind="barh",
    figsize=(11, 7),
    color="steelblue"
)

ax.axvline(
    cpi_change,
    color="red",
    linestyle="--",
    linewidth=2,
    label=f"CPI Growth: {cpi_change:.1f}%"
)

plt.title("Grocery Category Price Growth vs. CPI (2019–2025)")
plt.xlabel("Percentage Change (%)")
plt.ylabel("Grocery Category")
plt.legend()
plt.tight_layout()
plt.savefig("Ari_Q4_CPI_Comparison.png", dpi=300)
plt.show()

#Question 5: Compare grocery inflation with wages
# Calculate annual average hourly wages
wages["year"] = wages["observation_date"].dt.year

wage_annual = wages.groupby("year")["CES0500000003"].mean()

wage_change = (
    (wage_annual.loc[2025] / wage_annual.loc[2019] - 1) * 100
)

print(f"Hourly wage growth (2019-2025): {wage_change:.2f}%")

# Compare category growth with wage growth
q5_results = pd.DataFrame({
    "Category Growth (%)": category_changes
})

q5_results["Wage Growth (%)"] = wage_change
q5_results["Difference (pp)"] = (
    q5_results["Category Growth (%)"] - wage_change
)

q5_results["Faster Than Wages"] = (
    q5_results["Difference (pp)"] > 0
)

print(q5_results.round(2))

# Visualization
ax = category_changes.sort_values().plot(
    kind="barh",
    figsize=(11, 7),
    color="darkorange"
)

ax.axvline(
    wage_change,
    color="green",
    linestyle="--",
    linewidth=2,
    label=f"Wage Growth: {wage_change:.1f}%"
)

plt.title("Grocery Category Price Growth vs. Hourly Wages (2019–2025)")
plt.xlabel("Percentage Change (%)")
plt.ylabel("Grocery Category")
plt.legend()
plt.tight_layout()
plt.savefig("Ari_Q5_Wage_Comparison.png", dpi=300)
plt.show()
# Question 5: Final summary

print("\nQUESTION 5: FINAL RESULTS")
print("-" * 50)

print(f"Average hourly wage growth: {wage_change:.2f}%")

# Select categories that increased faster than wages
faster_categories = q5_results[
    q5_results["Faster Than Wages"] == True
]

print("\nGrocery categories that increased faster than wages:")
print(faster_categories[["Category Growth (%)", "Difference (pp)"]].round(2))

print(
    f"\nTotal: {len(faster_categories)} out of "
    f"{len(q5_results)} categories increased faster than wages."
)

# Save results
q5_results.to_csv("Ari_Q5_Results.csv")

print("\nQuestion 5 results saved successfully!")
