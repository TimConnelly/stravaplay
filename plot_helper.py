# -*- coding: utf-8 -*-
"""
Created on Tue May  1 18:48:56 2018

@author: Tim Connelly

Plotting helper functions

Requires Pandas and Bokeh
"""

from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import LinearAxis, Range1d, HoverTool
from bokeh.models.formatters import DatetimeTickFormatter

def series_extrema(s):
    return (s.min(), s.max())

def make_plot_range(s, pad_percent=0.1):
    extr = series_extrema(s)
    plot_lower = extr[0] - pad_percent*extr[0]
    plot_upper = extr[1] + pad_percent*extr[1]
    return (plot_lower, plot_upper)

def plot_data_single(df, x_name, y_name, plot_name="plot"):
    output_file(plot_name + ".html")
    p = figure(
        tools="pan,box_zoom,reset,save",
        #x_range=[0, 100000], y_range=[3000, 5000], 
        title=plot_name,
        x_axis_label=x_name, y_axis_label=y_name
    )
    
    p.line(df[x_name], df[y_name])
    show(p)
    
def plot_data_two(df, x_name, y_name1, y_name2, plot_name="plot"):
    output_file(plot_name + ".html", title=plot_name)

    source = ColumnDataSource(data={
            'Date':df['date'],
            y_name1:df[y_name1],
            y_name2:df[y_name2]
            })
    
    axis1_range = make_plot_range(df[y_name1], 0.1)
    axis2_range = make_plot_range(df[y_name2], 0.1)
    hover=HoverTool(tooltips=[
            ("index", "$index"),
            ("(x),y)", "($x, $y)"),
            ("Date", "@Date{%m-%d-%Y}"),
            ("MEQ", "@meq"),
            ("Distance", "@miles"),
            ("Vert(ft)", "@feet_gain")
        ], formatters={"date":"datetime"})
    
    p = figure(
            plot_width=800,
            plot_height=600,
         tools=[hover,",pan,box_zoom,reset,save"],
         toolbar_location="above",
         source=source,
        # x_range=[0, 100000], 
         y_range=list(axis1_range), 
         title=plot_name,
         x_axis_label=x_name, y_axis_label=y_name1
    )
    #p.xaxis[0].formatter = DatetimeTickFormatter(formats=dict(days=['%H-%H-%S']))
    p.xaxis[0].formatter = DatetimeTickFormatter(days=['%m-%d-%Y'])
    p.extra_y_ranges = {"axis2": Range1d(axis2_range[0], axis2_range[1])}
    p.add_layout(LinearAxis(y_range_name="axis2", axis_label=y_name2), "right")
    #p.line(df.index, df[y_name1])
    #p.line(df.index, df[y_name2], y_range_name="axis2", color='#00ff00')
    p.line(df[x_name], df[y_name1])
    p.line(df[x_name], df[y_name2], y_range_name="axis2", color='#00ff00')
    show(p)
    
# %%
def plot_data_two_xdate(df, x_name, y_name1, y_name2, plot_name="plot"):
    output_file(plot_name + ".html", title=plot_name)

    source = ColumnDataSource(data={
            'Date':df['date'],
            y_name1:df[y_name1],
            y_name2:df[y_name2],
            'miles':df['miles']
            })
    
    axis1_range = make_plot_range(df[y_name1], 0.1)
    axis2_range = make_plot_range(df[y_name2], 0.1)
    hover=HoverTool(tooltips=[
            ("Date", "@Date{%m-%d-%Y}"),
            ("MEQ", "@meq"),
            ("Distance", "@miles"),
            ("Vert(ft)", "@feet_gain")
        ], formatters={"Date":"datetime"})
    #hover.formatters = dict(date="datetime")    
    
    p = figure(
            plot_width=1000,
            plot_height=600,
         tools=[hover,",pan,box_zoom,reset,save"],
         toolbar_location="above",
        # x_range=[0, 100000], 
         y_range=list(axis1_range), 
         title=plot_name,
         x_axis_label=x_name, y_axis_label=y_name1
    )
    #p.xaxis[0].formatter = DatetimeTickFormatter(formats=dict(days=['%H-%H-%S']))
    p.xaxis[0].formatter = DatetimeTickFormatter(days=['%m-%d-%Y'])
    p.extra_y_ranges = {"axis2": Range1d(axis2_range[0], axis2_range[1])}
    p.add_layout(LinearAxis(y_range_name="axis2", axis_label=y_name2), "right")
    p.line('Date', y_name1, source=source)
    p.line('Date', 'miles', source=source, color='#ff0000')
    p.line('Date', y_name2, source=source, y_range_name="axis2", color='#00ff00')
    
    show(p)