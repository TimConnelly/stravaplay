import pandas as pd
import matplotlib.pyplot as plt
import datetime

from bokeh.plotting import figure, output_file, show
from bokeh.models import LinearAxis, Range1d

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
    
def activity_color(activity_type):
    if activity_type == 'Run':
        return "#f00000"
    if activity_type == 'Hike':
        return "#f00000"
    if activity_type == 'BackcountrySki':
        return "#0000ff"
    if activity_type == 'NordicSki':
        return "#0000ff"
    if activity_type == 'AlpineSki':
        return "#0000ff"
    if activity_type == 'Ride':
        return "#f0f000"
    if activity_type == 'RockClimbing':
        return "#00ff00"
    else:
        return 0
    
def run_to_meq(miles, gain_feet):
    return miles + gain_feet / 500.0
# %%
import math
import numpy as np

def extract_lat(row):
    lat = 0.0
    try:
        lat = row['start_latlng'][0]
    except TypeError:
        lat=np.nan
    return lat

def extract_lng(row):
    lng = 0.0
    try:
        lng=row['start_latlng'][1]
    except TypeError:
        lng=np.nan
    return lng


def merc_x(lon):
  r_major=6378137.000
  return r_major*math.radians(lon)

def lat2y(a, x, lng):
    scale = x/lng
    return 180.0/math.pi*math.log(math.tan(math.pi/4.0+a*(math.pi/180.0)/2.0))*scale

def timedelta_to_hours(td):
    return td.seconds / 3600.0

# In[]: Loand and process saved data
df = pd.read_pickle('data.pkl')

df.index = df['date']
df = pd.concat([df['2018-01-01':],df[:'2017-12-31']])

df['miles'] = meters_to_miles(df['distance'])
df['feet_gain'] = meters_to_feet(df['elevation'])

df['meq'] = df.apply(lambda row: generic_to_meq(row['miles'], row['feet_gain'], row['atype']), axis=1)
df['activity_color'] = df.apply(lambda row: activity_color(row['atype']), axis=1)
df['lat'] = df.apply(lambda row: extract_lat(row), axis=1)
df['lng'] = df.apply(lambda row: extract_lng(row), axis=1)
df['hours'] = df.apply(lambda row: timedelta_to_hours(row['duration']), axis=1)
df = df.interpolate(method='nearest')

df['merc_x'] = df.apply(lambda row: merc_x(row['lng']), axis=1)
df['merc_y'] = df.apply(lambda row: lat2y(row['lat'], 
                                    row['merc_x'], 
                                    row['lng']), axis=1)
df['back_date'] = df['date'] - pd.to_timedelta(7, unit = 'd')
df = df[df['date'] > datetime.datetime(year = 2017, month = 5, day = 1)]
weekly = df.resample('W-MON', on='back_date').sum()
weekly['date'] = weekly.index
monthly = df.resample('M', on='date').sum()

# In[]:

run_df = df.loc[lambda df: df.atype == 'Run']
fig, ax = plt.subplots(nrows=2, ncols=2,figsize=(20,10))
ax_cur = ax[0][0]
ax_cur.scatter(run_df['miles'], run_df['feet_gain'])
ax_cur.set_xlabel('Distace (miles)')
ax_cur.set_ylabel('Vert Gain (ft)')

ax_cur = ax[0][1]
ax_cur.scatter(run_df['miles'], run_df['meq'])
ax_cur.set_xlabel('Distace (miles)')
ax_cur.set_ylabel('Miles Equiv')

ax_cur = ax[1][0]
ax_cur.scatter(run_df['miles'], run_df['hours'])
ax_cur.set_xlabel('Distace (miles)')
ax_cur.set_ylabel('Time (hours)')

ax_cur = ax[1][1]
ax_cur.scatter(run_df['feet_gain'], run_df['hours'])
ax_cur.set_xlabel('Vert (ft)')
ax_cur.set_ylabel('Time (hours)')

fig.tight_layout()
plt.savefig('road_trip_scatter.pdf', bbox_inches='tight')

# %%
import plot_helper as ph

#ph.plot_data_single(df, 'date', 'meq','Miles Equivalent')
ph.plot_data_two_xdate(weekly, 'date', 'meq', 'feet_gain', 'Weekly Miles Equivalent')

# %% Plot activities on map

from bokeh.tile_providers import CARTODBPOSITRON, STAMEN_TERRAIN
from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool, value

output_file("RoadTrip.html", title='US Road Trip')

hover=HoverTool(tooltips=[
            ("Activity", "@atype"),
            ("Date", "@Date{%m-%d-%Y}"),
            ("MEQ", "@meq"),
            ("Distance", "@miles"),
            ("Vert(ft)", "@feet_gain")
        ], formatters={"Date":"datetime"})
    
# range bounds supplied in web mercator coordinates
p = figure(x_range=(-14000000, -7500000), y_range=(0, 8000000),
           x_axis_type="mercator", y_axis_type="mercator",
           plot_width=1200,
           plot_height=800,
           tools=[hover,",pan,box_zoom,wheel_zoom,reset,save"],
           active_scroll='wheel_zoom'
           )
p.add_tile(STAMEN_TERRAIN)

source = ColumnDataSource(data={
        'lat':df['merc_y'],
        'lng':df['merc_x'],
        'meq':df['meq'],
        'Date':df['date'],
        'miles':df['miles'],
        'feet_gain':df['feet_gain'],
        'atype': df['atype'],
        'activity_color':df['activity_color'],
        'size': 3*df['hours']
        })
    
p.circle(x="lng", y="lat", size='size', fill_color="activity_color", 
         fill_alpha=0.5, source=source, legend='atype')
p.line('lng', 'lat', source=source, color='#0f0f0f', line_width=0.5, alpha=0.5)
leg = p.legend
leg.location = "top_right"
leg.background_fill_alpha = 90
show(p)

# %% Google map 
"""

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, GMapOptions
from bokeh.plotting import gmap

output_file("gmap.html")

map_options = GMapOptions(lat=30.2861,lng=-97.7394,map_type="roadmap",zoom=11)

# For GMaps to function, Google requires you obtain and enable an API key:
#
# https://developers.google.com/maps/documentation/javascript/get-api-key
#
# Replace the value below with your personal API key:
key = open('gmap.key').read().strip()
p = gmap(key, map_options, title="Road Trip")

source = ColumnDataSource(data={
        'lat':df['lat'],
        'lon':df['lng']}
        )

p.circle(x="lon",y="lat",size=15,fill_color="blue",fill_alpha=0.8, source=source)

show(p)

"""