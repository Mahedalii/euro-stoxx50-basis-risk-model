import pandas as pd
from statsmodels.api import OLS, add_constant
from functools import reduce
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data
file_path = "Data.xlsx"
xls = pd.ExcelFile(file_path)

def convert_quarter_to_date(qtr_str):
    q, y = qtr_str.split()
    year = int(y)
    return {
        'Q1': f"{year}-03-31",
        'Q2': f"{year}-06-30",
        'Q3': f"{year}-09-30",
        'Q4': f"{year}-12-31"
    }[q]

# Load sheets
basis = pd.read_excel(xls, sheet_name="Basis")[['Date', 'Basis']]
futures = pd.read_excel(xls, sheet_name="Futures")[['Date', 'Open Interest', 'Bid-Ask Spread', 'TTM (days)']].rename(columns={"TTM (days)": "TTM"})
vstoxx = pd.read_excel(xls, sheet_name="Volatility Index")[['Date', 'VSTOXX Price']].rename(columns={'VSTOXX Price': 'VSTOXX'})
euribor = pd.read_excel(xls, sheet_name="Interest Rates")[['Date', 'EURIBOR 3M (%)', 'EURIBOR 6M (%)']].rename(columns={
    'EURIBOR 3M (%)': 'EURIBOR3M', 'EURIBOR 6M (%)': 'EURIBOR6M'
    })
inflation = pd.read_excel(xls, sheet_name="Inflation Rate")[['Date', 'YoY Inflation Rate (%, monthly)']].rename(columns={
    'YoY Inflation Rate (%, monthly)': 'Inflation'
    })
gdp = pd.read_excel(xls, sheet_name="GDP Growth Rate").rename(columns={'Time': 'Date',
    'Real GDP Growth (%, quarterly, calculated YoY by same quarter of previous year)': 'GDP Growth'
    })
fx = pd.read_excel(xls, sheet_name="Exchange Rate")[['Date', 'EUR/USD - FX']].rename(columns={'EUR/USD - FX': 'FX'})
country_spread_data = pd.read_excel(xls, sheet_name="Country Spread")

# Transform macro data 
gdp['Date'] = gdp['Date'].apply(convert_quarter_to_date)
gdp['Date'] = pd.to_datetime(gdp['Date'])
gdp = gdp.set_index('Date').resample('D').ffill().reset_index()

inflation['Date'] = pd.to_datetime(inflation['Date'])
inflation = inflation.set_index('Date').resample('D').ffill().reset_index()

# Country Spread (EU average row)
eu_default_spread = country_spread_data.loc[country_spread_data['Country'] == 'European Union', 'Default Spread (%)'].values[0]
country_spread_df = basis[['Date']].copy()
country_spread_df['Country Spread'] = eu_default_spread

# Merge all sheets
dfs = {
    'Basis': basis,
    'VSTOXX': vstoxx,
    'EURIBOR': euribor,
    'Inflation': inflation,
    'GDP': gdp,
    'FX': fx,
    'Liquidity': futures,
    'Country Spread': country_spread_df
}
merged_df = reduce(lambda left, right: pd.merge(left, right, on='Date', how='inner'), dfs.values())

# Cleaning
merged_df['EURIBOR3M'] /= 100
merged_df['EURIBOR6M'] /= 100
merged_df['Inflation'] /= 100
merged_df['GDP Growth'] /= 100
merged_df['Country Spread'] /= 100
model_df = merged_df.dropna()

# OLS Model
X = model_df[['TTM', 'VSTOXX', 'EURIBOR3M', 'EURIBOR6M', 'Inflation', 'GDP Growth', 'FX',
              'Open Interest', 'Bid-Ask Spread', 'Country Spread']]
y = model_df['Basis']
X = add_constant(X)
model = OLS(y, X).fit()

# Export
summary_df = pd.DataFrame({
    "Variable": model.params.index,
    "Coefficient": model.params.values,
    "Std. Error": model.bse.values,
    "t-Statistic": model.tvalues.values,
    "P-Value": model.pvalues.values,
    "CI Lower (95%)": model.conf_int().iloc[:, 0],
    "CI Upper (95%)": model.conf_int().iloc[:, 1]
}).round(6)

summary_df.to_excel("regression_summary.xlsx", index=False)

# Add Residuals and Predictions 
model_df['Fitted'] = model.fittedvalues
model_df['Residuals'] = model.resid

# Plots
sns.set_theme(style="whitegrid", palette="muted")

# Actual vs Fitted
plt.figure(figsize=(10, 4))
plt.plot(model_df['Date'], model_df['Basis'], label='Actual Basis', color='blue', linewidth=1)
plt.plot(model_df['Date'], model_df['Fitted'], label='Fitted Basis', color='red', linestyle='--', linewidth=1.2)
plt.xlabel('Date')
plt.ylabel('Basis')
plt.title('Actual vs. Fitted Basis Over Time')
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
plt.tight_layout()
plt.savefig("actual_vs_fitted_basis.png", dpi=300)
plt.close()

# Correlation Heatmap
plt.figure(figsize=(10, 8))
corr_data = model_df[['TTM', 'VSTOXX', 'EURIBOR3M', 'EURIBOR6M', 'Inflation', 'GDP Growth',
                      'FX', 'Open Interest', 'Bid-Ask Spread', 'Country Spread']]
sns.heatmap(corr_data.corr(), annot=True, fmt=".2f", linewidths=0.5, cbar_kws={"shrink": .8})
plt.title('Correlation Heatmap of Explanatory Variables')
plt.tight_layout()
plt.savefig("correlation_heatmap.png", dpi=300)
plt.close()

print(model.summary())