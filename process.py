import pandas as pd
import matplotlib.pyplot as plt
import datetime

df = pd.read_pickle('data.pkl')

m_to_mi = 1.0 / 1000.0 / 1.609344
df['miles'] = df['distance'] * m_to_mi
m_to_ft = 3.28084
df['feet_gain'] = df['elevation'] * m_to_ft
df['meq'] = df['miles'] + df['feet_gain'] / 500.0
df['back_date'] = df['date'] - pd.to_timedelta(7, unit = 'd')
df = df[df['date'] > datetime.datetime(year = 2017, month = 5, day = 1)]
weekly = df.resample('W-SUN', on='back_date').sum()
monthly = df.resample('M', on='date').sum()

plt.figure(figsize = (20,10))
plt.plot(weekly.index.values, weekly['meq'], label = 'meq')
plt.plot(weekly.index.values, weekly['miles'], label = 'miles')
plt.plot(weekly.index.values, weekly['feet_gain'] / 500, label = 'elevation change (in 1000 ft)')
plt.xlabel('week')
plt.ylabel('mi')
plt.ylim([0,150])
plt.legend()
plt.grid(linestyle = 'dotted')
plt.savefig('mileage.pdf', bbox_inches='tight')
# plt.show()
#
# plt.figure(figsize = (10,10))
# plt.plot(monthly.index.values, monthly['meq'])
# plt.plot(monthly.index.values, monthly['miles'])
# plt.show()
