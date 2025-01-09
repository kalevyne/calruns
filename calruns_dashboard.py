# import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import calendar

# page configuration
st.set_page_config(page_title="Calvin's Running Dashboard", 
                   page_icon=":runner:", 
                   layout="centered")

alt.themes.enable("dark")

# define data
data = pd.read_csv('data/simple_data.csv')
data['Year'] = data['Date'].str[:4].astype(int)
data['Month_int'] = data['Date'].str[5:7].astype(int)
data['Month_name'] = data['Month_int'].apply(lambda x: calendar.month_name[x])
#try in the future with og data: data(columns="select columns wanted")

# make monthly distance data
monthly = data.groupby(['Year', 'Month_name'])['Distance'].sum().reset_index()


with st.sidebar:
    st.title(":runner:" + "Calvin's Running Dashboard")

    years = list(data['Year'].unique())

    selected_year = st.selectbox('Select a year', years)
    data_year = data[data['Date'].str[:4] == selected_year]

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)



# plots
def make_heatmap(input_data, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_data).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="Month", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
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
    heatmap = make_heatmap(monthly, 'Year', 'Month_name', 'Distance', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)