# %%
#MOST RECENT UPDATE: 2020-10-23 
#AUTHOR: JONATHAN CHAN
#FINALIZE CODE INTO INDIVIDUAL SECTION

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import calendar
from pandas.api.types import CategoricalDtype
from plotly.colors import n_colors
import plotly.figure_factory as ff
from kaleido.scopes.plotly import PlotlyScope
import plotly.graph_objects as go
import os


raw_folder = "data/"
raw_file = "2019-2020_mood-sleep-data-ONESHEET_updated-to-2020-06-30 - Sheet1.csv"

raw_filename = raw_folder + raw_file


def get_block(test_date):
    """returns a string of the block that contains the given datetime"""
    b1_start = datetime.strptime("September 09, 2019", "%B %d, %Y")
    b1_end = datetime.strptime("October 13, 2019", "%B %d, %Y")

    b2_start = datetime.strptime("October 14, 2019", "%B %d, %Y")
    b2_end = datetime.strptime("November 17, 2019", "%B %d, %Y")

    b3_start = datetime.strptime("November 18, 2019", "%B %d, %Y")
    b3_end = datetime.strptime("December 22, 2019", "%B %d, %Y")

    b4_start = datetime.strptime("January 13, 2020", "%B %d, %Y")
    b4_end = datetime.strptime("February 16, 2020", "%B %d, %Y")

    b5_start = datetime.strptime("February 24, 2020", "%B %d, %Y")
    b5_end = datetime.strptime("March 29, 2020", "%B %d, %Y")

    b6_start = datetime.strptime("March 30, 2020", "%B %d, %Y")
    b6_end = datetime.strptime("May 03, 2020", "%B %d, %Y")

    cp_start = datetime.strptime("May 04, 2020", "%B %d, %Y")
    cp_end = datetime.strptime("June 30, 2020", "%B %d, %Y")

    start_dates = [b1_start, b2_start, b3_start, b4_start, b5_start, b6_start, cp_start]
    end_dates = [b1_end, b2_end, b3_end, b4_end, b5_end, b6_end, cp_end]
    mds_block = ["block_1", "block_2", "block_3", "block_4", "block_5", "block_6", "capstone"]
    
    mds_component = "other"
    
    for i in range(len(start_dates)):
        if test_date >= start_dates[i] and test_date <= end_dates[i]:
            mds_component = mds_block[i]
    return mds_component

def get_mood_str(mood_num):
    """return a string about the given mood score
    
    Assume scores only move in 0.5 increments
    
    good = 3.5 to 5 (inclusive) 
    neutral = 3 to 2.5 (inclusive)
    bad = 2 to 0 (inclusive)"""
    
    mood_str = "neutral"
    
    if mood_num >= 3.5:
        mood_str = "good"
    elif mood_num <= 2.0:
        mood_str = "bad"
    return mood_str

def workout_str(value):
    """returns the string for each type of workout:
    
    S = strength
    R = Run 
    C = Cardio
    - = None
    
    """
    #print(value)
    if value.upper() ==  "S":
        string = "Strength"
        
    elif value.upper() ==  "C":
        string = "Yoga/Cardio"
    elif value.upper() ==  "R":
        string = "Run"
    else:
        string = "No workout"
    return string

def preprocess_df(filename, col_list=None):
    """returns the formatted dataframe with columns from col_list.
    
    df has datetime formatted columns and date component columns added
    
    
    input:
        filename: filepath to input csv
        col_list: list of column names (list of strings)
    
    """
    raw_df = pd.read_csv(filename)
    raw_df = raw_df.dropna()

    #process strings into datetime objects
    for index, row in raw_df.iterrows():
        raw_df.at[index, "date"] = datetime.strptime(row["date"], "%d-%b-%y")
        raw_df.at[index, "waketime"] = datetime.strptime(row["waketime"], "%Y-%m-%d %H:%M")
        raw_df.at[index, "bedtime"] = datetime.strptime(row["bedtime"], "%Y-%m-%d %H:%M")
    if col_list:
        df = raw_df[col_list]
    else:
        df=raw_df
    dayname = []
    for index, row in df.iterrows():
        dayname.append(row["date"].strftime("%A"))

    df["dayname"] = dayname
    df["year"] = pd.DatetimeIndex(df['date']).year
    df["month"] = pd.DatetimeIndex(df['date']).month
    df["day"] = pd.DatetimeIndex(df['date']).day 
    return df



def get_courses_df(full_df):
    """returns a dataframe containing rows from the MDS-CL 2019/2020 course blocks
    
    check get_block() function for dates
    
    assume full_df contains rows from 2019-09-01 to 2020-06-30 
    
    """
    #create list of block values, mood values for each row 
    block_list = []
    mood_list = []
    for index, row in full_df.iterrows():
        
        block_value = get_block(row["date"])
        block_list.append(block_value)
        
        mood_value = get_mood_str(row["overall_mood"])
        mood_list.append(mood_value)

    block_df = full_df
    block_df["block"] = block_list
    block_df["mood_str"] = mood_list
    
    #remove all rows that were not included in blocks 1-6
    block_df = block_df[block_df.block != "other"]
    block_df= block_df[block_df.block != "capstone"]
    block_df
    
    #get blockday count (from count 0 to 34 for each of the 35 days in a block)
    ind = 0
    count_list = []
    row_iterator = full_df.iterrows()
    _, last = next(row_iterator)
    for index, row in block_df.iterrows():
        if row['block'] == last['block']:
            ind += 1
        else:
            ind = 0
        count_list.append(ind)
        last = row

    block_df["blockday"] = count_list
    
    return block_df


def create_full_df(filename):
    """returns df with only the rows from the course blocks (formats time columns)"""
    
    #create main dataframe - all dates, all rows

    df = preprocess_df(filename)
    df["workout"] = df["workout"].apply(workout_str)

    
    df["time_wake"] = np.NaN
    df["time_bed"] = np.NaN

    for index, row in df.iterrows():
        df.at[index, "time_wake"] = row["waketime"].time()
        df.at[index, "time_bed"] = row["bedtime"].time()

    df['time_wake'] =  pd.to_datetime(df['time_wake'], format='%H:%M:%S')
    df['time_bed'] =  pd.to_datetime(df['time_bed'], format='%H:%M:%S')
    
    return df

def create_courses_df(filename):
    """create the final courses df"""
    
    full_df = create_full_df(raw_filename)
    
    courses_df = get_courses_df(full_df)
    
    #add count for week_num
    ind = 0
    week_count = 1

    for index, row in courses_df.iterrows():
        courses_df.at[index, "weeknum"] = week_count

        ind += 1
        if ind % 7 == 0:
            week_count += 1
        
    return courses_df
    
    
def create_agg_df(df, grouping_col, agg_type):
    """returns the the aggregated function""" 
    return df.groupby([grouping_col]).agg(agg_type).reset_index()



def create_corr_df(df, col_list):
    """return the correlation matrix for a given dataframe's specified columns"""
    return df[col_list].corr()



def make_sleep_ridgeplot(df):
    """returns the visualization - hours of sleep per weekday
    
    Assume df contains columns: 'sleep_hrs' and 'dayname'
    """
    colors = n_colors('rgb(68, 149, 189)','rgb(0, 172, 145)',  7, colortype='rgb')
    daynames = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']

    fig = go.Figure()

    for i in range(len(daynames)):
        day = daynames[i]
        dayvals = df['sleep_hrs'][df['dayname'] == day]
        fig.add_trace(go.Violin(x=dayvals, line_color=colors[i], name = day))

    fig.update_traces(orientation='h', side='positive', width=3, points=False)
    fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False, legend={'traceorder':'reversed'} ,
                    title='Hours of sleep per day of week',
                    xaxis_title = "Amount of sleep (hrs)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                     )

    fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    #fig.show()
    
    return fig
    


def make_wake_ridgeplot(courses_df):
    """returns the following viz: waketime per day of week"""
    daynames = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']
    colors = n_colors('rgb(68, 149, 189)','rgb(0, 172, 145)',  7, colortype='rgb')
    fig = go.Figure()

    for i in range(len(daynames)):
        day = daynames[i]
        dayvals = courses_df['time_wake'][courses_df['dayname'] == day]
        fig.add_trace(go.Violin(x=dayvals, 
                                name = day,
                                line_color=colors[i]
                               )
                     )

    fig.update_traces(orientation='h', side='positive', width=3, points=False)
    fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False, legend={'traceorder':'reversed'} ,
                    title='Wake-up time per day of week',
                    xaxis_title="Time of day",
                    plot_bgcolor='rgba(0,0,0,0)')



    fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')

    fig.update_layout(
        xaxis_tickformat = '%H:%M',
        showlegend=False
    )

    # fig.show()
    return fig

def make_corr_heatmap(corrs):
    """return correlation heatmap for sleep habits"""
    
    colors = [[0, "rgb(140, 31, 34)"], [0.5, "rgb(247, 247, 248)"], [1.0, "rgb(65, 135, 174)"]]
    
    fig = ff.create_annotated_heatmap(
        z=corrs.values,
        x=list(corrs.columns),
        y=list(corrs.index),
        annotation_text=corrs.round(2).values,
        colorscale=colors,
        showscale=True)

    fig.update_layout(
        title = "Correlation between sleep habits and hours slept",
        xaxis = dict(
            tickangle = 20,
            tickfont = dict(size=9),
            tickmode = 'array',
            tickvals = ["yellow_glasses", "meditate", "foot_soak", "read", "sleep_hrs"],
            ticktext = ['Wore blue light glasses ', 'Meditation', 'Hot bath/foot soak', 'Read', 'Hours of sleep']
        ),
        yaxis = dict(
            tickmode = 'array',
            tickvals = ["yellow_glasses", "meditate", "foot_soak", "read", "sleep_hrs"],
            ticktext = ['Wore blue light glasses ', 'Meditation', 'Hot bath/foot soak', 'Read', 'Hours of sleep']
        )
    )

    return fig

def make_daily_heatmap(courses_df):
    """return heatmap visualization for daily mood per course week"""
    colors = [[0, "rgb(140, 31, 34)"], [0.5, "rgb(247, 247, 248)"], [1.0, "rgb(65, 135, 174)"]]
    fig = go.Figure(data=go.Heatmap(
            z=courses_df["overall_mood"],
            x=courses_df["dayname"],
            y=courses_df["weeknum"],
            colorscale=colors,
            reversescale=True))

    fig.update_layout(
        title='Daily mood ranking per course week (5-point scale)',
        yaxis_title="Week of program",
        yaxis_nticks = 30,
        xaxis_nticks=7)
    fig['layout']['yaxis']['autorange'] = "reversed"
    #fig.show()
    
    return fig 

def make_avg_mood_linechart(mood_per_blockday_df): 
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=mood_per_blockday_df["blockday"], y=mood_per_blockday_df["overall_mood"],
                             line=dict(color='rgb(65, 135, 174)', width=2)))
    fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
         shapes=[
            dict( #week 1: day 0-6
                type="rect", xref="x", yref="paper",
                x0=0, y0=0, x1=6, y1=1,
                fillcolor="rgb(247, 247, 248)", opacity=0.5,layer="below", line_width=0,
            ),
            dict( #week 2: day 6-13
                type="rect", xref="x", yref="paper",
                x0=6,y0=0, x1=13, y1=1,
                fillcolor="rgb(134, 236, 251)", opacity=0.5,layer="below", line_width=0,
            ),
            dict( # week 3: 13-20
                type="rect", xref="x", yref="paper",
                x0=13,y0=0, x1=20, y1=1,
                fillcolor="rgb(247, 247, 248)", opacity=0.5,layer="below", line_width=0,
            ),
            dict( # week 4: 20-27
                type="rect", xref="x", yref="paper",
                x0=20,y0=0, x1=27, y1=1,
                fillcolor="rgb(134, 236, 251)", opacity=0.5,layer="below", line_width=0,
            ),
            dict( #week 5: 27-34
                type="rect", xref="x", yref="paper",
                x0=27,y0=0, x1=34, y1=1,
                fillcolor="rgb(247, 247, 248)", opacity=0.5,layer="below", line_width=0,
            ),

        ]
    )

    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [0, 6, 13, 20, 27, 34],
            ticktext = ['Day 1', 'Day 7', 'Day 14', 'Day 21', 'Day 28', "Day 35"]
        ),
        yaxis = dict(
            tickmode = 'array',
            tickvals = [ 2, 2.5, 3, 3.5, 4.0, 4.5],
            ticktext = [ "bad", 'subpar', 'decent', 'good', 'great',"amazing"]
        )
    )
    fig.update_layout(
        title="Average mood over duration of course block",
        xaxis_title="Day of Block",
        yaxis_title="Daily mood",

    )
    fig.update_yaxes(range=[1.75, 3.75])
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    
    return fig

def make_block_heatmap(courses_df):
    """return mood per course block visualization"""
    colors = [[0, "rgb(140, 31, 34)"], [0.5, "rgb(247, 247, 248)"], [1.0, "rgb(65, 135, 174)"]]
    fig = go.Figure(data=go.Heatmap(
            x0=0,dx=0.5,
            z=courses_df["overall_mood"],
            x=courses_df["blockday"],
            y=courses_df["block"],
            colorscale= colors,
            reversescale=True))

    fig.update_layout(
        title='Daily mood per course block (5-point scale)',
        xaxis_nticks=5)

    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [0, 6, 13, 20, 27, 34],
            ticktext = ['Day 1', 'Day 7', 'Day 14', 'Day 21', 'Day 28', "Day 35"]
        ),
        yaxis = dict(
            tickmode = 'array',
            tickvals = [ "block_1", "block_2", "block_3", "block_4", "block_5", "block_6"],
            ticktext = [ "Block 1", 'Block 2', 'Block 3', 'Block 4', 'Block 5',"Block 6"]
        )
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickangle=45)

    return fig

def make_workout_pie(workout_df):
    """Make pie chart visualization for student habits """
    
    labels = workout_df["workout"]
    values = workout_df["overall_mood"]
    colors = ['rgb(247, 247, 248)', 'rgb(134, 236, 251)', 'rgb(165, 38, 45)','rgb(0, 172, 145)' ]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, opacity = 0.8)])
    fig.update_layout(
        title='Days with/without physical activity',
        showlegend=False
    )
    fig.update_traces(hoverinfo='label+percent+value', textinfo='label+percent', textfont_size=16,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2)))

    return fig

def make_coffee_barchart(courses_df_sum):
    """make visualization """
    daynames = ['Monday', 'Tuesday', "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    colors = n_colors('rgb(68, 149, 189)','rgb(0, 172, 145)',  7, colortype='rgb')
    vals_coffee = []
    fig = go.Figure()

    for i in range(len(daynames)):
        day = daynames[i]
        val_c = courses_df_sum["coffees"][courses_df_sum["dayname"]==day]
        vals_coffee.append(val_c.values[0])

    fig = go.Figure(data=[
        go.Bar(name="coffee", x=daynames, y=vals_coffee, marker_color = colors)
    ])
    fig.update_layout(
                    title='Number of coffees consumed per day of week',
        yaxis_title = "Total coffees (12 oz)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    barmode="group")
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    return fig

def make_phone_violinplot(courses_df):
    fig = go.Figure()
    overall_mood = ["bad", "neutral", "good"]
    colors = [[0, "rgb(215, 85, 90)"], [0.5, "rgb(0, 172, 145)"], [1.0, "rgb(134, 236, 251)"]]

    for i in range(len(overall_mood)):
        mood = overall_mood[i]
        fig.add_trace(go.Violin(x=courses_df['mood_str'][courses_df['mood_str'] == mood],
                                y=courses_df['phone_time'][courses_df['mood_str'] == mood],
                                fillcolor = colors[i][1],
                                line = dict(color = "black"),
                                opacity=0.66,
                                name=mood,
                                box_visible=True,
                                points='all',
                                meanline_visible=True))
    fig.update_layout(
                    title='Daily phone use vs. overall mood',
                    yaxis_title = "Daily Phone Use <br>(hours)",
                    xaxis_title = "Daily Mood",
                    plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', range=[-0, 10])
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    return fig

def make_phone_linechart(df):
    """return visualization for phone use over time chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["phone_time"],
                             line=dict(color='rgb(65, 135, 174)', width=2)))

    fig.add_shape(
                type="line",
                x0="2020-03-17",
                y0=10,
                x1="2020-03-17",
                y1=-1,
                line=dict(
                    color="rgb(215, 85, 90)",
                    width=4,
                    dash="dashdot",
                ),
        )
    fig.update_layout(
        showlegend=False,
        annotations=[
            dict(
                x="2020-03-17",
                y=8,
                xref="x",
                yref="y",
                text="Start of quarantine",
                bordercolor="rgb(215, 85, 90)",
                borderwidth=2,
                borderpad=4,
                bgcolor="rgb(215, 85, 90)",
                font=dict(
                family="Courier New, monospace",
                size=12,
                color="#ffffff"
                )
            )
        ]
    )
    fig.update_layout(
        title="Phone use over grad program's duration",
        xaxis_title="Date",
        yaxis_title="Daily phone use (hours)",
        plot_bgcolor='rgba(0,0,0,0)',
    )

    fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')

    return fig




def main():
    """creates the main visualizations - export to 'export' folder"""
    #create full dataframe
    df = create_full_df(raw_filename)

    #create dataframe containing rows from course-block months (exclude holidays, capstone)
    courses_df = create_courses_df(raw_filename)

    #specific visualization dataframes
    sleep_df = create_corr_df(courses_df, ["yellow_glasses", "meditate", "foot_soak", "read", "sleep_hrs"])
    mood_per_blockday_df = create_agg_df(courses_df, "blockday","mean" )
    coffee_df = create_agg_df(courses_df, "dayname", "sum")
    workout_df = create_agg_df(courses_df, "workout", "count")
    final_figs = []

    final_figs.append(make_sleep_ridgeplot(df))
    final_figs.append(make_wake_ridgeplot(df))
    final_figs.append(make_corr_heatmap(sleep_df))
    final_figs.append(make_daily_heatmap(courses_df))
    final_figs.append(make_avg_mood_linechart(mood_per_blockday_df))
    final_figs.append(make_block_heatmap(courses_df))
    final_figs.append(make_workout_pie(workout_df))
    final_figs.append(make_coffee_barchart(coffee_df))
    final_figs.append(make_phone_violinplot(courses_df))
    final_figs.append(make_phone_linechart(df))
    scope = PlotlyScope()

    for i in range(len(final_figs)):

        fig = final_figs[i]
        fig_name = "export/fig_" + str(i) + ".png"

        with open(fig_name, "wb") as f:
            f.write(scope.transform(fig, format="png"))



if __name__ == '__main__':
    main()
    print("SAVE COMPLETE: visualizations in 'exports' folder")

