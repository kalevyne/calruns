# import libraries
import streamlit as st
import pandas as pd
import altair as alt
import calendar

# page configuration
st.set_page_config(page_title="Calvin's Running Dashboard", 
                   page_icon="🏃", 
                   layout="centered")

alt.themes.enable("dark")

def time_to_seconds(time_str):
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    if '.' in parts[2]:  # Check if fractional seconds are present
        seconds = float(parts[2])  # Convert to float for fractional seconds
    else:
        seconds = int(parts[2])  # Convert to int if no fraction
    return hours * 3600 + minutes * 60 + seconds
def seconds_to_time(seconds):
    # Get hours, minutes, seconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60
    
    # Format the output with fractional seconds
    if remaining_seconds % 1 == 0:  # No decimal part
        return f"{hours:02}:{minutes:02}:{int(remaining_seconds):02}"
    else:  # Include decimal part
        return f"{hours:02}:{minutes:02}:{remaining_seconds:05.1f}"

# define and manipulate data
data = pd.read_csv('data/simple_data.csv')
data['Year'] = data['Date'].str[:4].astype(int)
data['Month_int'] = data['Date'].str[5:7].astype(int)
data['Month'] = data['Month_int'].apply(lambda x: calendar.month_name[x])
data['Distance'] = data['Distance'].astype(float)
data['Steps']= data['Steps'].str.replace(',', '').astype(int)
data['Total Ascent'] = data['Total Ascent'].replace('--', '0')
data['Total Ascent'] = data['Total Ascent'].str.replace(',', '').astype(int)
data['Time'] = data['Time'].apply(time_to_seconds)
data['Seconds_Pace'] = data['Avg Pace'].str.split(':').apply(lambda x:int(x[0]) * 60 + int(x[1]))
#try in the future with og data: data(columns="select columns wanted")

# make monthly distance data
month_order = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"]
monthly = data.groupby(['Year', 'Month']).agg(
    Distance=('Distance', 'sum'),
    Time=('Time', 'sum'),
    Seconds_Pace=('Seconds_Pace', 'mean'),
    Elevation=('Total Ascent', 'sum'),
    Long=('Distance', 'max'),
    Steps=('Steps', 'sum')
).reset_index()
monthly['Display_Time'] = monthly['Time'].apply(seconds_to_time)
monthly['Average_Pace'] = monthly['Seconds_Pace'].apply(lambda x: f"{int(x //60)}:{int(x % 60):02d}")
monthly['Month'] = pd.Categorical(monthly['Month'], categories=month_order, ordered=True)
monthly_sorted = monthly.sort_values(by=['Year', 'Month'], axis=0)


with st.sidebar:
    st.title("🏃 Calvin's Running Dashboard")

    # year selection
    years = list(data['Year'].unique())
    selected_year = st.selectbox('Select a year', years)
    data_year = data[data['Date'].str[:4] == selected_year]

    # focus statistic selection
    stats = list(['Distance', 'Time', 'Average Pace', 'Elevation', 'Long', 'Steps'])
    user_selected_stat = st.selectbox('Select a heatmap Statistic', stats)
    stats_dict = {'Distance': 'Distance',
                  'Time': 'Time',
                  'Average Pace': 'Seconds_Pace',
                  'Elevation': 'Elevation',
                  'Long': 'Long',
                  'Steps': 'Steps'}
    selected_stat = stats_dict[user_selected_stat]
    

    # color theme selection
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)




# plots
def make_heatmap(input_data, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_data).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', 
                    axis=alt.Axis(
                        title="Year", 
                        titleFontSize=18, 
                        titlePadding=15, 
                        titleFontWeight=900, 
                        labelAngle=0
                    )),
            x=alt.X(f'{input_x}:O', 
                    axis=alt.Axis(
                        title="Month", 
                        titleFontSize=18, 
                        titlePadding=15, 
                        titleFontWeight=900
                    ), sort=month_order),           #ensure months are in order on heatmap
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap



# dashboard
col = st.columns(1)

with col[0]:
    heatmap = make_heatmap(monthly_sorted, 'Year', 'Month', selected_stat, selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)



if __name__ == "__main__": #only run if file is executed, if imported it is ignored
    print(monthly_sorted)