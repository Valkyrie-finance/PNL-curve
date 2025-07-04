import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import os

print("Current working directory:", os.getcwd())

# Read data from CSV file
# Expected CSV format:
# Date,PortfolioValue,DepositsWithdrawals,BTC_Price
# 2025-01-01,500000,10000,105642.93
# 2025-01-02,550000,5000,105594.01
# etc...
df = pd.read_csv('portfolio_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
# Convert columns to numeric, coercing errors to NaN
df['PortfolioValue'] = pd.to_numeric(df['PortfolioValue'], errors='coerce')
df['DepositsWithdrawals'] = pd.to_numeric(df['DepositsWithdrawals'], errors='coerce').fillna(0)
df['BTC_Price'] = pd.to_numeric(df['BTC_Price'], errors='coerce')

# Only drop duplicate rows where both have DepositsWithdrawals == 0
def dedup_keep_growth_and_deposit(df):
    df = df.sort_values(['Date', 'DepositsWithdrawals'])
    def keep_group(group):
        # If all DepositsWithdrawals are zero, keep only the last
        if (group['DepositsWithdrawals'] == 0).all():
            return group.tail(1)
        return group
    return df.groupby('Date', group_keys=False).apply(keep_group).reset_index(drop=True)

df = dedup_keep_growth_and_deposit(df)

# Filter out rows with missing PortfolioValue
valid_df = df[df['PortfolioValue'].notna()].copy()

# TWR calculation (ensure deposit is not counted as a gain)
twr = []
base = valid_df.iloc[0]['PortfolioValue']
cum_return = 1.0
for idx in range(len(valid_df)):
    row = valid_df.iloc[idx]
    if idx == 0:
        twr.append(0.0)
        base = row['PortfolioValue']
    elif row['DepositsWithdrawals'] != 0:
        base = row['PortfolioValue']
        twr.append(cum_return - 1)
    else:
        prev_row = valid_df.iloc[idx-1]
        daily_return = (row['PortfolioValue'] - prev_row['PortfolioValue']) / base
        cum_return *= (1 + daily_return)
        twr.append(cum_return - 1)
valid_df['TWR'] = np.array(twr) * 100  # as percent
valid_df['TWR'] = valid_df['TWR'].ffill()

# Calculate BTC returns (percentage change from first BTC price)
btc_valid = valid_df[valid_df['BTC_Price'].notna()].copy()
if not btc_valid.empty:
    first_btc_price = btc_valid['BTC_Price'].iloc[0]
    btc_valid['BTC_Return'] = ((btc_valid['BTC_Price'] - first_btc_price) / first_btc_price) * 100
    valid_df = valid_df.merge(btc_valid[['Date', 'BTC_Return']], on='Date', how='left')
else:
    valid_df['BTC_Return'] = np.nan

# Print TWR and BTC columns for debugging
print(valid_df[['Date', 'PortfolioValue', 'DepositsWithdrawals', 'TWR', 'BTC_Price', 'BTC_Return']])

# Calculate cumulative deposits/withdrawals for reference
valid_df['CumulativeDeposits'] = valid_df['DepositsWithdrawals'].cumsum()

# Calculate percent return for portfolio value
valid_df['PortfolioValueReturn'] = (valid_df['PortfolioValue'] - valid_df['PortfolioValue'].iloc[0]) / valid_df['PortfolioValue'].iloc[0] * 100

# Set black background for figure and axes
fig, ax1 = plt.subplots(figsize=(16, 8), facecolor='black')
ax1.set_facecolor('black')

# Plot TWR and BTC Return on the left axis
ln1 = ax1.plot(valid_df['Date'], valid_df['TWR'], color='#00bfff', linestyle='--', marker='x', markersize=9, linewidth=2.5, label='TWR (Portfolio Return %)')
ln2 = ax1.plot(valid_df['Date'], valid_df['BTC_Return'], color='yellow', linestyle='-', marker='s', markersize=8, linewidth=2.5, label='BTC Return (%)')

# Plot deposits as green triangle markers on the TWR curve
# Find indices where deposits occur
deposit_mask = valid_df['DepositsWithdrawals'] > 0
if deposit_mask.any():
    ln3 = ax1.plot(valid_df['Date'][deposit_mask], valid_df['TWR'][deposit_mask], linestyle='None', marker='^', markersize=14, color='lime', label='Deposits', markeredgecolor='black', markeredgewidth=2)
else:
    ln3 = None
ax1.set_ylabel('Return (%)', color='#00bfff', fontsize=16, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#00bfff', labelsize=13, colors='white')
ax1.set_ylim(min(valid_df['TWR'].min(), valid_df['BTC_Return'].min()) - 1, max(valid_df['TWR'].max(), valid_df['BTC_Return'].max()) + 1)

# Calculate max drawdown for TWR
twr_series = valid_df['TWR'].ffill()
roll_max = twr_series.cummax()
drawdown = twr_series - roll_max
max_drawdown = drawdown.min()  # This will be negative
max_drawdown_pct = abs(max_drawdown)

final_twr = valid_df['TWR'].ffill().iloc[-1]
final_btc = valid_df['BTC_Return'].ffill().iloc[-1]

print(f"Max Drawdown (TWR): {max_drawdown_pct:.2f}%")

# Show only a subset of x-axis date labels for clarity
N = max(1, len(valid_df) // 10)  # Show about 10 date labels
ax1.xaxis.set_major_locator(ticker.MultipleLocator(N))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
plt.setp(ax1.get_xticklabels(), rotation=30, ha='right', fontsize=13, color='white', fontweight='bold')

# Add grid with higher contrast
ax1.grid(True, which='major', axis='both', linestyle='--', linewidth=1.2, alpha=0.2, color='white')

# Add horizontal line at y=0
ax1.axhline(0, color='white', linewidth=1.2, linestyle='--', alpha=0.5)

# Add title and labels
plt.title('Portfolio vs BTC Performance', fontsize=22, fontweight='bold', pad=24, color='white')
ax1.set_xlabel('Date', fontsize=16, color='white', fontweight='bold')

# Enhanced legend at the bottom center, moved slightly lower
if ln3 is not None:
    legend = ax1.legend(
        [ln1[0], ln2[0], ln3[0]],
        [
            f"TWR (Portfolio Return %): {final_twr:.2f}% | Max DD: {max_drawdown_pct:.2f}%",
            f"BTC Return (%): {final_btc:.2f}%",
            'Deposits'
        ],
        loc='lower center',
        bbox_to_anchor=(0.5, -0.28),  # Move legend slightly lower
        ncol=3,
        fontsize=15,
        frameon=True,
        fancybox=True,
        framealpha=0.95
    )
else:
    legend = ax1.legend(
        [ln1[0], ln2[0]],
        [
            f"TWR (Portfolio Return %): {final_twr:.2f}% | Max DD: {max_drawdown_pct:.2f}%",
            f"BTC Return (%): {final_btc:.2f}%"
        ],
        loc='lower center',
        bbox_to_anchor=(0.5, -0.28),  # Move legend slightly lower
        ncol=2,
        fontsize=15,
        frameon=True,
        fancybox=True,
        framealpha=0.95
    )
legend.get_frame().set_edgecolor('#cccccc')
legend.get_frame().set_linewidth(2.5)
legend.get_frame().set_facecolor('black')
for text in legend.get_texts():
    text.set_color('white')
    text.set_fontweight('bold')

fig.tight_layout(pad=3)
fig.subplots_adjust(bottom=0.28)  # Increase bottom margin for clarity

# Only use rows with valid PortfolioValue for x-axis limits
ax1.set_xlim(valid_df['Date'].min(), valid_df['Date'].max())

plt.show()

# Print the current TWR and BTC return (final values)
print(f"Current TWR: {valid_df['TWR'].ffill().iloc[-1]:.2f}%")
print(f"Current BTC Return: {valid_df['BTC_Return'].ffill().iloc[-1]:.2f}%")
print(f"Portfolio vs BTC: {valid_df['TWR'].ffill().iloc[-1] - valid_df['BTC_Return'].ffill().iloc[-1]:.2f}%") 