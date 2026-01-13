import pandas as pd 
import numpy as np
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go 
import plotly.figure_factory as ff
import base64
import os
import joblib


# Page configuration
st.set_page_config(page_title="World COVID-19 Data Analysis",page_icon="🌍",layout="wide")

page_Backgound_Image = "Red-and-Blue-COVID-19-Virus.jpg"

name,extension = os.path.splitext(page_Backgound_Image)

# Page Background Configuration 
def get_image_of_bin_file(bin_file):
    try:
        with open(bin_file,"rb") as file:
            data = file.read() 
        return base64.b64encode(data).decode()
    except ValueError as e:
        return "File Doesn't Exist{e}"

def set_background(png_file):
    png_st = get_image_of_bin_file(png_file)
    png_b_img = f'''
    <style>
    .stApp {{
        background-image : url("data:image/{extension};base64,{png_st}");
        background-size : cover ;
        background-position : center ;
        background-repeat : no repeat ;
        background-attachment : fixed ;
    }}
    </style>
'''
    st.markdown(png_b_img , unsafe_allow_html=True)

set_background(page_Backgound_Image)

with st.container(border=True):
    st.markdown("""
    <style>
    .title-container {
        background: rgba(255, 255, 255, 0.25); /* white */
        backdrop-filter: blur(8px); /* blur effect */
        -webkit-backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        text-align: center;
    }
    .title-container h1 {
        color: white;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    .title-container p {
        color: #f0f0f0;
        font-style: italic;
    }
    .title-list {
        text-align: left;
        display: inline-block;
        margin-top: 10px;
        font-size: 1.05em;
    }
    </style>

    <div class='title-container'>
        <h1>🌍 World COVID-19 Data Analysis</h1>
        <p>This interactive dashboard analyzes global COVID-19 trends, highlights</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.title("Kaggle Dataset link")
st.sidebar.link_button(label="Kaggle DataSets",url="https://www.kaggle.com/datasets/imdevskp/corona-virus-report/data")

@st.cache_data
def loading_csv(file):
    df = pd.read_csv(file)
    return df

# Loading the worldometer_data csv
worldometer_data = "worldometer_data.csv"

@st.cache_data
def loading_worldometer_data():
    world_data = loading_csv(worldometer_data)
    float_cols = world_data.select_dtypes(include=['float64']).columns
    float_cols = float_cols.drop(['Tests/1M pop','Deaths/1M pop','Tot Cases/1M pop'])
    for col in float_cols:
        try:
            world_data[col] = world_data[col].astype('Int64')
        except Exception as e:
            print(f"Could not convert column '{col}'. Error: {e}")
    world_data =  world_data[world_data['Country/Region'] != 'Diamond Princess']
    mask = world_data['WHO Region'].isna()
    world_data.loc[mask, 'WHO Region'] = world_data.loc[mask, 'Continent']
    world_data.fillna(0,inplace=True)
    return world_data

# loading the data int a DataFrame
worldometer_data = loading_worldometer_data()

# --------------------------------------------------------------------------------

# Loading the Full_Grouped csv
Grouped = "full_grouped.csv"

@st.cache_data
def loading_full_Grouped_data():
    Full_Grouped = loading_csv(Grouped)

    Full_Grouped['Date'] = pd.to_datetime(Full_Grouped['Date'],format='mixed')
    Full_Grouped['Month'] = Full_Grouped['Date'].dt.month_name()
    
    return Full_Grouped

Full_Grouped = loading_full_Grouped_data()

st.sidebar.title("🚀 Navigation")
manu = st.sidebar.radio("Select Analysis View:", ["🌐 Worldmeter Analysis", "📅 Country Grouped Analysis"," Predicting the Severity "])

# font dictionary 
font_dict = dict(size=24, color='white')
bgcolor = 'rgba(0,0,0,0)'

if manu == "🌐 Worldmeter Analysis":
    st.header("Data source: worldometer_Data from World Health Organization ",divider=True,text_alignment='center')

    all_region = ["All"] + sorted(worldometer_data["WHO Region"].unique())

    selected_region = st.sidebar.selectbox("Select WHO Region",options=all_region)

    if selected_region == "All":
        filtered_df = worldometer_data
    else:
        filtered_df = worldometer_data[worldometer_data['WHO Region'] == selected_region]

    st.markdown("<h2 style='text-align:center; color:white;'>🔍 Covid-19 Worldometer Data </h2>", unsafe_allow_html=True)

    st.dataframe(filtered_df.head(5))

    st.markdown("<h2 style='text-align:center; color:white;'>🔥 Question 1: how the column corrolations related to each other.", unsafe_allow_html=True)

    # Data Cleaning 
    world_CP = filtered_df.copy()
    world_CP = world_CP.select_dtypes(include=['number'])

    # Compute Correlation 
    Correlations = world_CP.corr() * 100

    red_blue_green = [
    [0.0, 'rgb(0, 200, 0)'],    
    [0.5, 'rgb(0, 0, 200)'],    
    [1.0, 'rgb(200, 0, 0)']]

    fig_corr = ff.create_annotated_heatmap(
        z=Correlations.values,
        x=list(Correlations.columns),
        y=list(Correlations.index),
        annotation_text=Correlations.values.round(2),
        colorscale=red_blue_green,
        showscale=True,
        reversescale=True
    )

    fig_corr.update_layout(
        title=dict(
            text="Correlation Matrix of World COVID-19 Indicators",
            x=0.5,
            xanchor='center',
            font=font_dict
        ),
        height=850,
        margin=dict(l=100, r=100, t=100, b=50),
        paper_bgcolor=bgcolor,
        plot_bgcolor=bgcolor
    )

    st.plotly_chart(fig_corr,use_container_width=True)

    # Insight Section 
    with st.expander("🧠 Interpretation Tips"):
        st.markdown("""
        - **Positive correlations (red)** indicate that two variables increase together.
        - **Negative correlations (blue)** mean that as one increases, the other decreases.
        - Strong correlations (> 0.7 or < -0.7) suggest close relationships worth further analysis.
        """)


    # Top 10 Countries by Metrics
    st.markdown("<h2 style='text-align:center; color:white;'>🔥top 10 countries in Total Death, Total Cases, Total Tests ,Total Recovered Ordered by Every Metric", unsafe_allow_html=True)

    Metrics = ['TotalTests', 'TotalCases', 'TotalDeaths', 'TotalRecovered']

    for Metric in Metrics:
        Metric_df = filtered_df.groupby('Country/Region')[Metric].sum().reset_index().sort_values(by=Metric,ascending=False).head(10)
        fig_bar = px.bar(Metric_df,x='Country/Region',y=Metric,text=Metric,color='Country/Region',title="📊Top 10 Countries by {metric}")
        
        fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_bar.update_layout(   title=dict(
            text=f"📊 Top 10 Countries by {Metric} Cases",
            x=0.5,
            xanchor='center',
            font=font_dict
        ),
            xaxis_title="Country/Region",
            yaxis_title=Metric,
            showlegend=False,
            plot_bgcolor=bgcolor,
            paper_bgcolor=bgcolor,
            height=500
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with st.expander("🧠 Interpretation"):
        st.markdown("""
    - from the graph we found out that :-
    - 1- that **USA, Russia and India** are the top 3 countries that **run Covid tests** on it's population.
    - 2- **by far USA** have **63139605 Covid test cases** alone make it **the most country to run Covid testes** over the time of the first Pandemic.

    - 3- that **USA, Brazil and India** are the top 3 countries that **acknowledge Covid Cases** on it's population.
    - 4- **by far USA** have **5032179 acknowledge Covid cases** alone make it **the most country** to **acknowledge Covid Cases** over the time of the first Pandemic.

    - 5- that **USA, Brazil and Mexico** are the top 3 countries that **acknowledge Covid Deaths** on it's population.
    - 6- **by far USA** have **162804 Death cases** alone make it **the most country** to **acknowledge Covid Deaths** over the time of the first Pandemic.

    - 7- that **USA, Brazil and Mexico** are the top 3 countries that **Recovered Covid cases** on it's population.
    - 8- **by far USA** have **2576668 Recovered Covid cases** alone make it **the most country** to **Recovered Covid cases** over the time of the first Pandemic.      
        """)

    # 3️⃣ Combined Comparison

    st.markdown("<h2 style='text-align:center; color:white;'>🌍 Comparison of Top 10 Countries by All Metrics</h2>", unsafe_allow_html=True)

    Metric_df = filtered_df.groupby('Country/Region')[Metrics].sum().reset_index().sort_values(by=Metrics,ascending=False).head(10)
    Metric_Melted = Metric_df.melt(id_vars=['Country/Region'],value_vars=Metrics,var_name='Metric', value_name='Number')

    fig_melt = px.bar(
        Metric_Melted,
        x='Country/Region',
        y='Number',
        color='Metric',
        barmode='group',
    )
    fig_melt.update_traces(texttemplate='%{text:.2s}', textposition='outside')

    fig_melt.update_layout(    title=dict(
            text="🌐 Top 10 Countries by Deaths, Cases, Tests & Recovery Cases",
            x=0.5,
            xanchor='center',
            font=font_dict
        ),
            plot_bgcolor=bgcolor,
            paper_bgcolor=bgcolor,height=600)

    st.plotly_chart(fig_melt, use_container_width=True)

    with st.expander("🧠 Interpretation"):
        st.markdown("""
    - from the graph we found out that :-
    - **Grouping the data of 'TotalTests','TotalCases','TotalDeaths' and 'TotalRecovered' into single graph to show case the data ordered by total deaths happened by Covid 19**
        """)

    # Top 10 Countries by Metrics
    st.markdown("<h2 style='text-align:center; color:white;'>🔥top 10 countries in Total Cases, Total Death, Total Tests Ordered by Every metric Per 1 M Population", unsafe_allow_html=True)

    Metrics = ['Tot Cases/1M pop', 'Deaths/1M pop', 'Tests/1M pop']

    for Metric in Metrics:
        Metric_df = filtered_df.groupby('Country/Region')[Metric].sum().reset_index().sort_values(by=Metric,ascending=False).head(10)
        fig_bar = px.bar(Metric_df,x='Country/Region',y=Metric,text=Metric,color='Country/Region',title="📊Top 10 Countries by {metric}")
        
        fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_bar.update_layout(   title=dict(
            text=f"📊 Top 10 Countries by {Metric} Cases",
            x=0.5,
            xanchor='center',
            font=font_dict
        ),
            xaxis_title="Country/Region",
            yaxis_title=Metric,
            showlegend=False,
            plot_bgcolor=bgcolor,
            paper_bgcolor=bgcolor,
            height=500
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    with st.expander("🧠 Interpretation"):
        st.markdown("""
    - from the graph we found out that :-
    - 1- that **Luxembourg, Monaco and Faeroe Islands** are the top 3 countries thats runs **Total Covid Tests Per 1 Million People** on it's population.
    - 2- this metrics showcases that most small countries in Population have more testing abilities to get the potential cases for checking Covid-19.
                    
    - 3- that **Qatar, French Guiana and Bahrain** are the top 3 countries thats runs **Total Covid Cases Per 1 Million People** on it's population.
    - 4- this Graph showcases that most small countries in Population have more abilities to get the cases for checking Covid-19 Spreading.
                    
    - 5- that **San-Marino, Belgium Guiana and Uk** are the top 3 countries thats runs **Total Covid Death Cases Per 1 Million People** on it's population.
    - 6- this Graph showcases that most small countries in Population have **high Amount** of **Death Cases** Compared to their population but low compared to **other Countries** Becoause of Covid 19 Spreading.
        """)

elif manu == "📅 Country Grouped Analysis":
    st.header("Data source: Full_Grouped from World Health Organization ",divider=True,text_alignment='center')

    all_region = ["All"]+ sorted(Full_Grouped['WHO Region'].unique())
    selected_region = st.sidebar.selectbox('Select WHO Region',options=all_region)

    if selected_region == "All":
        filtered_df = Full_Grouped
    else:
        filtered_df = Full_Grouped[Full_Grouped['WHO Region'] == selected_region]

    st.markdown("<h2 style='text-align:center; color:white;'>🔍 Covid-19 Full Grouped Data </h2>", unsafe_allow_html=True)

    st.dataframe(filtered_df.head(5))

    Group_cp = filtered_df.copy()
    Group_cp = Group_cp.select_dtypes(include=['number','datetime64'])

    Correlations = Group_cp.corr() * 100

    red_blue_green = [
    [0.0, 'rgb(0, 200, 0)'],    
    [0.5, 'rgb(0, 0, 200)'],    
    [1.0, 'rgb(200, 0, 0)']]

    fig_corr = ff.create_annotated_heatmap(
        z=Correlations.values,
        y=list(Correlations.columns),
        x=list(Correlations.index),
        annotation_text=Correlations.values.round(2),
        colorscale=red_blue_green,
        showscale=True,
        reversescale=True
    )

    fig_corr.update_layout(
        title=dict(
            text="Correlation Matrix of Fully_Grouped Covid-19 Indicators.",
            x=0.5,
            xanchor="center",
            font=font_dict
        ),
        height=850,
        margin=dict(l=100, r=100, t=100, b=50),
        paper_bgcolor=bgcolor,
        plot_bgcolor=bgcolor
    )

    st.plotly_chart(fig_corr,use_container_width=True)

    with st.expander("🧠 Interpretation"):
        st.markdown("""
    - From the Graph above the Correlations Of our Focus **Confirmed , Death , Recovered Covid 19 Cases** For each other is **High** all their **Correlations** Are between **90%** and **95%**  
        """)

    # how Confirmed, Deaths, Recovered, Active Change over time 
    Totals = ['Confirmed','Deaths','Recovered','Active']
    color_discrete_map={
        'Deaths': 'red', 
        'Recovered': 'green', 
        'Active': 'orange',
        'Confirmed':"blue"
    } 
    Totals_Grouped = filtered_df.groupby(['Month'])[Totals].sum().reset_index()
    Totals_Grouped = Totals_Grouped.sort_values(by='Deaths', ascending=True)

    Totals_Grouped_Melted = Totals_Grouped.melt(id_vars='Month',value_vars=Totals,var_name='Status', value_name='Count')

    fig = px.line(data_frame=Totals_Grouped_Melted,x='Month',y='Count',color='Status',color_discrete_map=color_discrete_map)

    fig.update_layout(title=dict(
        text="World Total Covid Cases Trends Per Months",
        x=0.5,
        xanchor='center',
        font=font_dict
    ),
    height=650,showlegend=True,margin=dict(t=100,b=100,l=100,r=100),
                            paper_bgcolor=bgcolor,
                            plot_bgcolor=bgcolor)

    st.plotly_chart(fig,use_container_width=True)

    with st.expander("🧠 Interpretation"):
        st.markdown("""
    - from the graph we found out that :-
    - 1- Over the Period of the **Pandemic** of the **Covid 19** the the Cases were **increasing** in a rapid rate **skyrocketing** from **Marsh onwards** with more cases are being **active**.
    - 2- their is a **trend** in active Cases being more than the **Recovered** People till **June**.
    - 3- **Death Cases** over the **World** were at the same rate **During** the **Pandemic** **compared** to the **increase** in the **Confirmed** Cases **Infected** during the same **Period**.  
        """)

    # Plotting the Comparisons of Each Country for Death, Recovered and Confirmed cases  
    Totals = ['Deaths','Recovered','Active']
    color_map={
        'Deaths': 'red', 
        'Recovered': 'green', 
        'Active': 'orange'
    } 

    Totals_Grouped = filtered_df.groupby('Country/Region')[Totals].sum().reset_index()
    top_n = 10
    Totals_Grouped = Totals_Grouped.sort_values(by='Recovered', ascending=False).head(top_n)
    Totals_Grouped_Melted = Totals_Grouped.melt(id_vars='Country/Region',value_vars=Totals,var_name='Status', value_name='Count')

    fig = px.pie(data_frame=Totals_Grouped_Melted,values='Count',names='Status',
                    facet_col='Country/Region',facet_col_wrap=5,color='Status',color_discrete_map=color_map,
                    hole=0.5
                    )
    fig.update_traces(textposition='inside', textinfo='percent')
    fig.for_each_annotation(lambda x: x.update(text=x.text.split("=")[-1]))
    fig.update_annotations(font_size=15, font_color="white")
    fig.update_layout(title=dict(
            text=f'Distribution of COVID-19 Metrics for Top {top_n} Countries (Based on Total Recovered Cases)',
            x=0.5,
            xanchor="center",
            font=font_dict
        ),
        height=850,showlegend=True,margin=dict(t=100,b=50,l=50,r=50),
                            paper_bgcolor=bgcolor,
                            plot_bgcolor=bgcolor)

    st.plotly_chart(fig,use_container_width=True)

    with st.expander("🧠 Interpretation"):
        st.markdown("""
    - from the graph we found out that :-
    - 1- **all Countries** have **more** than **50%** Recovered Cases other than **US** with about **25%** Reflecting **Poor Capability** to **Contain** the **pandemic**.
    - 2- **Italy** and **Spain** having **more** **Death** Cases as Percentage Compared to Other **Nations** by about **14%** and **11%** Respectively
                        Reflecting maybe more **elderly** or **babies** **death** due to nature of the **Virus**.
    - 3- **Chile** and **Russia** having the **lowest** **Death** Cases by about **less** than **2%** of the total Cases.
        """)

    # What is the Percentages of total Deaths, Recovered, Active Cases for WHO Regions ordered by Recovered Cases

    Totals_Grouped = filtered_df.groupby('WHO Region')[Totals].sum().reset_index()
    Totals_Grouped = Totals_Grouped.sort_values(by='Recovered', ascending=False)
    Totals_Grouped_Melted = Totals_Grouped.melt(id_vars='WHO Region',value_vars=Totals,var_name='Status', value_name='Count')

    fig = px.pie(data_frame=Totals_Grouped_Melted,values='Count',names='Status',
                    facet_col='WHO Region',facet_col_wrap=3,color='Status',color_discrete_map=color_map,hole=0.5)
    fig.update_traces(textposition='inside',textinfo='percent')
    fig.for_each_annotation(lambda x: x.update(text=x.text.split("=")[-1]))
    fig.update_layout(title=dict(
        text='Distribution of COVID-19 Metrics for Each WHO Region (Based on Total Recovered Cases)',
        x=0.5,
        xanchor='center',
        font=font_dict
    ),
    height=600,showlegend=True,margin=dict(t=100,b=50,l=50,r=50),
                    paper_bgcolor=bgcolor,
                    plot_bgcolor=bgcolor
    )
    st.plotly_chart(fig,use_container_width=True)

    with st.expander("🧠 Interpretation"):
        st.markdown("""
    - from the graph we found out that :-
    - 1- **Americas** Region has the **Highest** **Active** Cases in all regions by about **39%** and the **second Highest** **Death** cases by **5%** After **Europe** by **7.7%**.
    - 2- **Africa** Region has the **lowest** Death cases compared to all regions by about **2%** and the **second Highest** **Active** Cases by **47%** after **Americas** by **39%**.
    - 3- **Western Pacific** have the **Highest** Rate of **Recovering** by about **71.5%** and **lowest** **Active** Cases by about **25%** Reflecting a better **Healthcare** System Compared to *Other Regions**. 
        """)
else:
    st.markdown("حظ اوفر فى المرة القادمة",unsafe_allow_html=True)

    all_region = ["All"]+ sorted(Full_Grouped['WHO Region'].unique())
    selected_region = st.sidebar.selectbox('Select WHO Region',options=all_region)

    if selected_region == "All":
        filtered_df = Full_Grouped
    else:
        filtered_df = Full_Grouped[Full_Grouped['WHO Region'] == selected_region]
    
    features = filtered_df[['Confirmed', 'Deaths', 'Recovered']]
    filtered_df['Severe'] = (filtered_df['Deaths'] / filtered_df['Confirmed']) > 0.05
    labels = filtered_df['Severe'].astype("int")





