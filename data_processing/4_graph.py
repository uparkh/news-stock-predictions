import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import textwrap


idf = pd.read_csv('./reddit-sentiment.csv')  # input df
sdf = pd.read_csv('../arishko2-yahoo/data/HistoricalData_1743103651771.csv')  # yahoo S&P500 data

# Convert 'Date' column to datetime format
sdf['Date'] = pd.to_datetime(sdf['Date'])
sdf_2024 = sdf[sdf['Date'].dt.year == 2024]
sdf_2024 = sdf_2024.sort_values(by=['Date'])
sdf_2024 = sdf_2024.reset_index(drop=True)

sdf_2024 = sdf_2024[['Date', 'Close/Last']]
sdf_2024

start_price = sdf_2024.iloc[0]['Close/Last']
end_price = sdf_2024.iloc[-1]['Close/Last']
baseline_slope = (start_price - end_price) / len(sdf_2024)

sdf_2024['Baseline'] = start_price - (baseline_slope * sdf_2024.index)
sdf_2024['Deviation'] = sdf_2024['Close/Last'] - sdf_2024['Baseline']

# convert month names to datetime objects
def month_to_datetime(month):
    return datetime.strptime(f"2024-{month}-01", "%Y-%b-%d")

mo_idf = idf.groupby('month', sort=False)['nltk_mu'].mean()
mo_idf_standardized = (mo_idf - mo_idf.mean()) / mo_idf.std()
mo_idf_standardized.index = mo_idf_standardized.index.map(month_to_datetime)

plt.figure(figsize=(12, 6))
# plt.plot(sdf_2024['Date'], sdf_2024['Close/Last'], linestyle=':', color='b', label='Close/Last')
# plt.plot(sdf_2024['Date'], sdf_2024['Baseline'], linestyle='--', color='orange', label='Baseline')
plt.plot(sdf_2024['Date'], sdf_2024['Deviation'], linestyle='-', color='purple', label='Deviation')
mag = sdf_2024['Deviation'].max()
mag += mag / 12

colors = ['green' if val > 0 else 'red' for val in mo_idf_standardized]
widths = [delta.days for delta in (mo_idf_standardized.index[1:] - mo_idf_standardized.index[:-1])] + [31]
plt.bar(mo_idf_standardized.index, mo_idf_standardized * (mag / 3), color=colors, width=widths, align='edge')

plt.title('2024 S&P 500: Adjusted Relative to Trendline')
plt.xlabel('Date')
plt.ylabel('Price Deviation from Trendline ($)')
plt.grid(True)
plt.xticks(rotation=45)

plt.ylim(-mag, mag)

plt.xlim(sdf_2024['Date'].iloc[0], sdf_2024['Date'].iloc[-1])
plt.tight_layout()
plt.show()




