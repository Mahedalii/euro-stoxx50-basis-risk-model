import pandas as pd
import numpy as np
from statsmodels.api import OLS, add_constant
from statsmodels.regression.rolling import RollingOLS
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Load data
data = pd.read_excel("Data.xlsx", sheet_name=None)

# Preprocessing functions
def convert_quarter_to_date(qtr_str):
    q, y = qtr_str.split()
    year = int(y)
    return {
        'Q1': f"{year}-03-31",
        'Q2': f"{year}-06-30",
        'Q3': f"{year}-09-30",
        'Q4': f"{year}-12-31"
    }[q]

# Individual sheets
basis = data['Basis'][['Date', 'Basis']]
futures = data['Futures'][['Date', 'Open Interest', 'Bid-Ask Spread', 'TTM (days)']].rename(columns={'TTM (days)': 'TTM'})
vstoxx = data['Volatility Index'][['Date', 'VSTOXX Price']].rename(columns={'VSTOXX Price': 'VSTOXX'})
euribor = data['Interest Rates'][['Date', 'EURIBOR 3M (%)', 'EURIBOR 6M (%)']].rename(columns={
    'EURIBOR 3M (%)': 'EURIBOR3M', 'EURIBOR 6M (%)': 'EURIBOR6M'
})
inflation = data['Inflation Rate'][['Date', 'YoY Inflation Rate (%, monthly)']].rename(columns={'YoY Inflation Rate (%, monthly)': 'Inflation'})
gdp = data['GDP Growth Rate'].rename(columns={'Time': 'Date', 'Real GDP Growth (%, quarterly, calculated YoY by same quarter of previous year)': 'GDP Growth'})
fx = data['Exchange Rate'][['Date', 'EUR/USD - FX']].rename(columns={'EUR/USD - FX': 'FX'})
country_spread = data['Country Spread']
eu_spread = country_spread[country_spread['Country'] == 'European Union']['Default Spread (%)'].values[0]

# Reformat inflation and GDP
gdp['Date'] = gdp['Date'].apply(convert_quarter_to_date)
gdp['Date'] = pd.to_datetime(gdp['Date'])
gdp = gdp.set_index('Date').resample('D').ffill().reset_index()

inflation['Date'] = pd.to_datetime(inflation['Date'])
inflation = inflation.set_index('Date').resample('D').ffill().reset_index()
# EU country spread
country_df = basis[['Date']].copy()
country_df['Country Spread'] = eu_spread

# Merge all dataframes on Date
dfs = {
    'Basis': basis,
    'Futures': futures,
    'VSTOXX': vstoxx,
    'EURIBOR': euribor,
    'Inflation': inflation,
    'GDP': gdp,
    'FX': fx,
    'Country Spread': country_df
}
merged_df = dfs['Basis']
for name, df in dfs.items():
    if name != 'Basis':
        merged_df = merged_df.merge(df, on='Date', how='inner')

# Convert to decimal
merged_df['EURIBOR3M'] /= 100
merged_df['EURIBOR6M'] /= 100
merged_df['Inflation'] /= 100
merged_df['GDP Growth'] /= 100
merged_df['Country Spread'] /= 100
merged_df = merged_df.dropna()

# === Split data: 80% train / 20% test ===
model_df = merged_df.copy()
X = model_df[['TTM', 'VSTOXX', 'EURIBOR3M', 'EURIBOR6M', 'Inflation',
              'GDP Growth', 'FX', 'Open Interest', 'Bid-Ask Spread', 'Country Spread']]
y = model_df['Basis']
X = add_constant(X)

split_idx = int(0.8 * len(X))
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

# Fit model and evaluate 
model = OLS(y_train, X_train).fit()
y_pred = model.predict(X_test)

# Evaluation metrics
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Validation Metrics:")
print(f"RMSE: {rmse:.2f}")
print(f"MAE: {mae:.2f}")
print(f"R-squared: {r2:.3f}")

# Rolling OLS (250-day expanding window)
X_rolling = X.copy()
y_rolling = y.copy()
rolling_model = RollingOLS(y_rolling, X_rolling, window=250).fit()
rolling_coefs = rolling_model.params

# Add Date for visualization
rolling_coefs['Date'] = model_df['Date'].iloc[-len(rolling_coefs):].values