# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 21:26:48 2018

@author: Tim Connelly
"""

import matplotlib.pyplot as plt
import datetime

import pandas as pd 

from scipy import stats
# %%
def meters_to_miles(meters):
    m_to_mi = 1.0 / 1000.0 / 1.609344
    return meters*m_to_mi

def meters_to_feet(meters):
    m_to_ft = 3.28084
    return meters*m_to_ft

'''
Fiddle with these formulas
'''
def generic_to_meq(miles, gain_feet, activity_type):
    if activity_type == 'Run':
        return miles + gain_feet / 500.0
    if activity_type == 'Hike':
        return miles + gain_feet / 500.0
    if activity_type == 'BackcountrySki':
        return 1.2*miles + gain_feet / 500.0
    if activity_type == 'NordicSki':
        return miles + gain_feet / 500.0
    if activity_type == 'AlpineSki':
        return miles/10 + gain_feet / 1000.0
    if activity_type == 'Ride':
        return miles/3 + gain_feet / 100.0
    if activity_type =='RockClimbing':
        return miles + gain_feet / 100.0
    else:
        return 0
        
def run_to_meq(miles, gain_feet):
    return miles + gain_feet / 500.0

# %%

def timedelta_to_hours(td):
    return td.seconds / 3600.0

# In[]: Load and process saved data
df = pd.read_pickle('data.pkl')

df.index = df['date']
df = pd.concat([df['2018-01-01':],df[:'2017-12-24']])

# In[]:
# Fix the bad data because strava won't let you
try: 
    #R2R2R
    df.loc['2017-11-05 12:40:14+00:00', 'distance'] = 77230
    df.loc['2017-11-05 12:40:14+00:00', 'elevation'] = 3322.32  
    #C2C2C
    df.loc['2017-12-04 14:31:50+00:00', 'distance'] = 46350
    df.loc['2017-12-04 14:31:50+00:00', 'elevation'] = 3183.33
    #Whitney
    df.loc['2017-12-21 15:28:34+00:00', 'distance'] = 33310
    df.loc['2017-12-21 15:28:34+00:00', 'elevation'] = 1991.25
except:
    pass

# In[]:
df['miles'] = meters_to_miles(df['distance'])
df['feet_gain'] = meters_to_feet(df['elevation'])

df['meq'] = df.apply(lambda row: generic_to_meq(row['miles'], 
  row['feet_gain'], row['atype']), axis=1)
df['hours'] = df.apply(lambda row: timedelta_to_hours(row['duration']), axis=1)
df = df.interpolate(method='nearest')

df['ft_per_mile'] = df['feet_gain']/df['miles']
df['ft_per_hour'] = df['feet_gain']/df['hours']

df['back_date'] = df['date'] - pd.to_timedelta(7, unit = 'd')

# In[]:
run_df = df.loc[lambda df: df.atype == 'Run']

# In[]
# fit data
slope, intercept, r_value, p_value, std_err \
= stats.linregress(run_df['feet_gain'], run_df['hours'])
slope_fpm, intercept_fpm, r_value_fpm, p_value_fpm, std_err_fpm \
= stats.linregress(run_df['ft_per_mile'], run_df['hours'])
slope_rates, intercept_rates, r_value_rates, p_value_rates, std_err_rates \
= stats.linregress(run_df['ft_per_mile'], run_df['ft_per_hour'])
# In[] 
# plot data

fig, ax = plt.subplots(figsize=(20,10))
ax.scatter(run_df['feet_gain'], run_df['hours'])
ax.plot(run_df['feet_gain'], 
        intercept + slope*run_df['feet_gain'], 
        'r', label='fitted line'
        )
ax.set_xlabel('Vert (ft)')
ax.set_ylabel('Time (hours)')
plt.title('Vertical Gain Times')
plt.savefig('gain_rate.pdf', bbox_inches='tight')

# In[]
fig, ax = plt.subplots(figsize=(20,10))
ax.scatter(run_df['ft_per_mile'], run_df['hours'])
ax.plot(run_df['ft_per_mile'],
        intercept_fpm + slope_fpm*run_df['ft_per_mile'], 
        'r', label='fitted line'
        )
ax.set_xlabel('Vert rate (ft/mi)')
ax.set_ylabel('Time (hours)')
#ax.title('Vertical Gain Times')
plt.title('Vertical Gain Times')
plt.savefig('gain_rate.pdf', bbox_inches='tight')

# In[]
fig, ax = plt.subplots(figsize=(20,10))
plt.scatter(run_df['ft_per_mile'], 
            run_df['ft_per_hour'], 
            10*(run_df['hours']),
            alpha=0.7)
ax.plot(run_df['ft_per_mile'], 
        intercept_rates + slope_rates*run_df['ft_per_mile'], 
        'r', label='fitted line'
        )
ax.set_xlabel('Feet per mile')
ax.set_ylabel('Feet per hour')
plt.title('Vert per hour vs Vert per mile (size ~ time)')
#plt.savefig('Vertical_rates.pdf', bbox_inches='tight')

# In[]
from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool

hover=HoverTool(tooltips=[
            ("Feet/mile", "@ft_per_mile"),
            ("Feet/hour", "@ft_per_hour"),
            ("Date", "@Date{%m-%d-%Y}"),
            ("MEQ", "@meq"),
            ("Distance", "@miles"),
            ("Total Vert(ft)", "@feet_gain")
        ], formatters={"Date":"datetime"})

TOOLS = [hover,",crosshair,pan,wheel_zoom,reset,tap"]

source = ColumnDataSource(data={
        'ft_per_mile':run_df['ft_per_mile'],
        'ft_per_hour':run_df['ft_per_hour'],
        'meq':run_df['meq'],
        'Date':run_df['date'],
        'miles':run_df['miles'],
        'feet_gain':run_df['feet_gain'],
        'atype': run_df['atype'],
        'size': (run_df['meq']/10.0)
        })

p = figure(plot_width=1200,
           plot_height=800,
           tools=TOOLS,
           title='Climb Rates',
           x_axis_label='Course rate (ft/mile)',
           y_axis_label='Time rate (ft/hour)')

p.scatter(x='ft_per_mile', 
          y='ft_per_hour',
          radius='size',
          source=source,
          fill_alpha=0.7)

output_file("run_scatter.html", title="Vert rates")

show(p)

# In[]
'''
More data is needed to make this plot look good

from scipy.interpolate import griddata

X, Y = np.meshgrid(run_df['ft_per_mile'], run_df['ft_per_hour'])
grid_x, grid_y = np.mgrid[0:np.max(run_df['ft_per_mile']), 
                          0:np.max(run_df['ft_per_hour'])]

grid_z0 = griddata((run_df['ft_per_mile'], 
                    run_df['ft_per_hour']), 
                    run_df['hours'], 
                    (grid_x, grid_y), 
                    method='linear')

fig, ax = plt.subplots(figsize=(20,10))
#plt.imshow(grid_z0)
plt.contour(grid_x, grid_y, grid_z0)
'''