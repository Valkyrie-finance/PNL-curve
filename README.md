# PNL Curve

This folder contains scripts for tracking and visualizing your portfolio's performance versus BTC, including TWR (Time-Weighted Return), max drawdown, and more.

## Getting Started

1. **Clone or download this repository.**
2. **Copy the template CSV:**
   - Duplicate `portfolio_data_template.csv` and rename the copy to `portfolio_data.csv`.
   - Fill in your own data in `portfolio_data.csv` (do not edit the template).
3. **Run the scripts:**
   - `get_bitcoin_price.py` will update BTC prices in your portfolio data.
   - `PNL curve.py` will plot your portfolio performance and compare it to BTC.

## File Descriptions
- `PNL curve.py`: Main script for plotting portfolio and BTC performance.
- `get_bitcoin_price.py`: Script to fetch and update BTC prices for your portfolio dates.
- `portfolio_data_template.csv`: Blank template for your portfolio data. Copy and rename to `portfolio_data.csv` before use.
- `.gitignore`: Prevents your real `portfolio_data.csv` from being uploaded to GitHub.

## CSV Format
The CSV should have the following columns:
```
Date,PortfolioValue,DepositsWithdrawals,BTC_Price
```
- **Date**: Date of the entry (YYYY-MM-DD)
- **PortfolioValue**: Total value of your portfolio on that date
- **DepositsWithdrawals**: Net deposits or withdrawals on that date (positive for deposit, negative for withdrawal, 0 if none)
- **BTC_Price**: (Will be filled automatically by the script)

## Notes
- Only the template CSV is tracked in git. Your real data stays private.
- For any issues or questions, open an issue or contact [valkyrie-finance](https://github.com/valkyrie-finance). 