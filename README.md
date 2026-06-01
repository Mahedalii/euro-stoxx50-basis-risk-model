# Predictive Modeling of Basis Risk in EURO STOXX 50 Futures

This project analyzes the key drivers of basis risk in EURO STOXX 50 equity index futures using a multi-factor Ordinary Least Squares (OLS) regression framework. The analysis uses daily data from 2020-2024 sourced independently, cleaned and compiled for empirical analysis.

The project was developed as part of a Financial Risk Management assignment and focuses on understanding how macroeconomic, liquidity, volatility, and contract-specific variables affect futures basis risk.

## Project Objective

The objective of this project is to model and interpret basis risk in EURO STOXX 50 futures by examining the relationship between the futures basis and several explanatory variables, including interest rates, bid-ask spreads, open interest, trading volume, time to maturity, and market volatility proxies.

## Methodology

The project uses an econometric modeling approach based on multiple linear regression.
Main steps include:

* Data cleaning and preparation
* Construction of the basis variable
* Exploratory correlation analysis
* Multi-factor OLS regression
* In-sample model interpretation
* Train-test validation using an 80/20 split
* Out-of-sample performance evaluation
* Rolling OLS analysis using a 250-day rolling window to assess coefficient stability

## Files

### `model.py`

This script performs the main regression analysis.
It:

* Loads the cleaned dataset
* Prepares the dependent and explanatory variables
* Estimates the multi-factor OLS regression model
* Prints the full regression summary in the terminal
* Exports the regression output to Excel
* Generates visual outputs such as:

  * Actual vs fitted basis plot
  * Correlation heatmap

### `training.py`

This script performs model validation and robustness checks.
It:

* Splits the dataset into training and test samples
* Fits the OLS model on the training set
* Predicts basis risk on the test set
* Calculates out-of-sample performance metrics:

  * RMSE
  * MAE
  * R²
* Estimates Rolling OLS coefficients using a 250-day rolling window

### `report.pdf`

This is the final project report containing the empirical analysis, interpretation of results, figures, tables, and discussion.

### `actual_vs_fitted_basis.png`

This plot compares the actual basis values with the fitted values from the OLS regression model.

### `correlation_heatmap.png`

This figure shows the correlation matrix of the explanatory variables used in the model.

### `regression_summary.xlsx`

This Excel file contains the exported regression output and model results.

## Data

The dataset used in this project was independently collected, cleaned, and compiled by the author using publicly available financial and macroeconomic data sources, including Yahoo Finance and other public market-data sources.

The cleaned dataset is included in this repository as:

```text
Data.xlsx
```

The dataset includes variables related to:

* EURO STOXX 50 spot and futures prices
* Futures basis
* EURIBOR interest rates
* Bid-ask spread
* Open interest
* Trading volume
* Time to maturity
* Market volatility proxies
* Macroeconomic indicators

## Key Results

The main OLS regression achieved:

* R²: 32.9%
* Adjusted R²: approximately 32.4%

The model shows moderate in-sample explanatory power, while out-of-sample validation indicates weaker forecasting performance. This suggests that basis risk may be affected by time-varying dynamics, regime changes, nonlinear effects, or omitted variables.

## Requirements

The project requires Python 3 and the following libraries:

```text
pandas
numpy
matplotlib
seaborn
statsmodels
scikit-learn
openpyxl
```

Install the required libraries using:

```bash
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn openpyxl
```

## How to Run

First, make sure `data.xlsx` is placed in the same folder as `model.py` and `training.py`.

To run the main regression model:

```bash
python model.py
```

To run the training and validation script:

```bash
python training.py
```

## Outputs

Running the scripts generates or uses the following output files:

```text
regression_summary.xlsx
actual_vs_fitted_basis.png
correlation_heatmap.png
```

The terminal also displays:

* OLS regression summary
* Coefficient estimates
* Statistical significance measures
* Model validation metrics
* Out-of-sample performance results

## Tools Used

* Python
* pandas
* NumPy
* statsmodels
* scikit-learn metrics
* matplotlib
* seaborn
* Excel

## Project Type

This is an econometric and statistical modeling project. Although the project includes out-of-sample validation, the main model is based on OLS regression rather than advanced machine learning methods.

## Author

Mahed Ali
M.Sc. Quantitative Finance
University of Bologna
