import pandas as pd 
import numpy as np
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go 
import plotly.figure_factory as ff
import base64
import os
import joblib
import google.generativeai as genai

# Giminai Config
Api_Key = genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
AI_model = genai.GenerativeModel("gemini-3-flash-preview") 

@st.cache_data
def AI_Insights(df_markdown, context="General"):
    # Select specialized instructions based on where the button was clicked
    instructions = {
        "correlation": "Explain the strongest health indicators and their relationship to mortality.",
        "prediction": "Analyze the ML model's logic. Explain why certain features drive 'Severe' flags.",
        "trends": "Identify the top 3 outliers and explain the month-over-month growth trends.",
        "General": "Summarize the key takeaways from this health dataset."
    }
    
    selected_instruction = instructions.get(context, instructions["General"])

    prompt = f"""
    System: You are a WHO Senior Health Analyst. {selected_instruction}
    
    Data (Markdown format):
    {df_markdown}
    
    Task: Provide 3 concise bulleted insights. Use professional medical terminology. 
    Keep it strictly under 150 words.
    """
    
    try:
        response = AI_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI Insight currently unavailable. (Error: {str(e)})"

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

st.markdown("""
<style>
    .title-container {
        background: rgba(255, 255, 255, 0.2); 
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    .title-container h1 { color: white; font-size: 2.5em; margin-bottom: 10px; }
    .title-container p { color: #f0f0f0; font-style: italic; }

    /* Apply Glassmorphism to ALL Plotly Charts */
    [data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] { color: white !important; }
    [data-testid="stMetricLabel"] { color: #f0f0f0 !important; }
</style>

<div class='title-container'>
    <h1>🌍 World COVID-19 Data Analysis</h1>
    <p>Global trends and machine learning severity predictions</p>
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

    st.markdown("<h2 style='text-align:center; color:white;'>🔥 how the column corrolations related to each other.", unsafe_allow_html=True)

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
    if st.button("🪄 Generate AI Interpretation",key="Correlation Worldometer"):
        with st.spinner("Gemini is analyzing the trends..."):
            # Get dynamic insight
            dynamic_text = AI_Insights(Correlations,context="correlation")
            
            # Display in a styled glass container
            st.markdown(f"""
            <div class="glass-chart" style="margin-top:20px;">
                <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
            </div>
            """, unsafe_allow_html=True)

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

        if st.button("🪄 Generate AI Interpretation",key=f"{Metric}"):
            with st.spinner("Gemini is analyzing the trends..."):
                # Get dynamic insight
                dynamic_text = AI_Insights(Metric_df)
                
                # Display in a styled glass container
                st.markdown(f"""
                <div class="glass-chart" style="margin-top:20px;">
                    <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                    <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
                </div>
                """, unsafe_allow_html=True)

    # 3️⃣ Combined Comparison

    st.markdown("<h2 style='text-align:center; color:white;'>🌍 Comparison of Top 10 Countries by All Metrics</h2>", unsafe_allow_html=True)

    Metric_df = filtered_df.groupby('Country/Region')[Metrics].sum().reset_index().sort_values(by=Metrics,ascending=False).head(10)
    Metric_Melted = Metric_df.melt(id_vars=['Country/Region'],value_vars=Metrics,var_name='Metric', value_name='Number')

    fig_melt = px.bar(Metric_Melted,x='Country/Region',y='Number',color='Metric',barmode='group',text_auto='.2s')
    fig_melt.update_traces(textposition='outside',textfont_size=12)
    fig_melt.update_layout(title=dict(
            text="🌐 Top 10 Countries by Deaths, Cases, Tests & Recovery Cases",
            x=0.5,
            xanchor='center',
            font=font_dict
        ),
            plot_bgcolor=bgcolor,
            paper_bgcolor=bgcolor,height=600)

    st.plotly_chart(fig_melt, use_container_width=True)

    if st.button("🪄 Generate AI Interpretation",key="Combined Comparison"):
        with st.spinner("Gemini is analyzing the trends..."):
            # Get dynamic insight
            dynamic_text = AI_Insights(Metric_Melted)
            
            # Display in a styled glass container
            st.markdown(f"""
            <div class="glass-chart" style="margin-top:20px;">
                <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
            </div>
            """, unsafe_allow_html=True)

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

        if st.button("🪄 Generate AI Interpretation",key=f"Top 10{Metric}"):
            with st.spinner("Gemini is analyzing the trends..."):
                # Get dynamic insight
                dynamic_text = AI_Insights(Metric_df)
                
                # Display in a styled glass container
                st.markdown(f"""
                <div class="glass-chart" style="margin-top:20px;">
                    <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                    <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
                </div>
                """, unsafe_allow_html=True)

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

    if st.button("🪄 Generate AI Interpretation",key="Correlations Grouped by"):
        with st.spinner("Gemini is analyzing the trends..."):
            # Get dynamic insight
            dynamic_text = AI_Insights(Correlations,context="correlation")
            
            # Display in a styled glass container
            st.markdown(f"""
            <div class="glass-chart" style="margin-top:20px;">
                <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
            </div>
            """, unsafe_allow_html=True)

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

    if st.button("🪄 Generate AI Interpretation",key="metrics over time"):
        with st.spinner("Gemini is analyzing the trends..."):
            # Get dynamic insight
            dynamic_text = AI_Insights(Totals_Grouped_Melted)
            
            # Display in a styled glass container
            st.markdown(f"""
            <div class="glass-chart" style="margin-top:20px;">
                <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
            </div>
            """, unsafe_allow_html=True)

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

    if st.button("🪄 Generate AI Interpretation",key="pie Charts"):
        with st.spinner("Gemini is analyzing the trends..."):
            # Get dynamic insight
            dynamic_text = AI_Insights(Totals_Grouped_Melted)
            
            # Display in a styled glass container
            st.markdown(f"""
            <div class="glass-chart" style="margin-top:20px;">
                <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
            </div>
            """, unsafe_allow_html=True)

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

    if st.button("🪄 Generate AI Interpretation",key="final Charts"):
        with st.spinner("Gemini is analyzing the trends..."):
            # Get dynamic insight
            dynamic_text = AI_Insights(Totals_Grouped_Melted)
            
            # Display in a styled glass container
            st.markdown(f"""
            <div class="glass-chart" style="margin-top:20px;">
                <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
            </div>
            """, unsafe_allow_html=True)

else:

    all_region = ["All"]+ sorted(Full_Grouped['WHO Region'].unique())
    selected_region = st.sidebar.selectbox('Select WHO Region',options=all_region)

    if selected_region == "All":
        filtered_df = Full_Grouped
    else:
        filtered_df = Full_Grouped[Full_Grouped['WHO Region'] == selected_region]

    Case_Fetality_Rate = (sum(filtered_df['Deaths']) / sum(filtered_df['Confirmed'])) * 100

    model = joblib.load("Covid_19_Grouped_Logistic_Regression.pkl")

    features = filtered_df[['Confirmed', 'Deaths', 'Recovered']]
    filtered_df['Severe'] = (filtered_df['Deaths'] / filtered_df['Confirmed']) > 0.05
    labels = filtered_df['Severe'].astype("int")

    prediction = model.predict(features)
    prediction_Proba = model.predict_proba(features)[:,1]
    filtered_df["Predicted Severity"] = prediction
    filtered_df["Model Probability"] = prediction_Proba

    Accuracy = np.mean(prediction == labels)
    st.subheader("📊 Severity Prediction Analysis",anchor='center',divider=True)
    st.markdown("📊 Model Performance vs. Actual Data",unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Model Accuracy", f"{Accuracy:.1%}")
    col2.metric("Model Avg Risk", f"{prediction_Proba.mean():.1%}")
    col3.metric("Actual Case Fetality Rate", f"{Case_Fetality_Rate:.2f}%")

    group = ["Severe","Predicted Severity"]
    filtered_grouped = filtered_df.groupby("Country/Region")[group].sum().reset_index().sort_values(by=group[0],ascending=False).head(10)
    Melted_df = filtered_grouped.melt(id_vars="Country/Region",value_vars=group,var_name='Severity Type', value_name='Count')
    st.dataframe(data=Melted_df.head(5))

    fig = px.bar(data_frame=Melted_df,x="Country/Region",y='Count',barmode='group',color='Severity Type',color_discrete_map={"Severe": "#ef553b", "Predicted Severity": "#636efa"},text_auto='.2s')
    fig.update_traces(textposition='outside',textfont_size=12)
    fig.update_layout(title=dict(
        text = "Actual Severity Vs Predicted Severity",
        x=0.5,
        xanchor='center',
        font=font_dict
    ),
    height=650,paper_bgcolor=bgcolor,plot_bgcolor=bgcolor
    )

    st.plotly_chart(fig,use_container_width=True)

    with st.expander("🔎 View Prediction Discrepancies"):
        # Filter rows where prediction does not match reality
        errors = filtered_df[filtered_df["Severe"] != filtered_df["Predicted Severity"]]
        if not errors.empty:
            st.write("The following countries were flagged differently by the model vs. the 5% CFR rule:")
            st.dataframe(errors[['Country/Region', 'Confirmed', 'Deaths', 'Severe', 'Predicted Severity', 'Model Probability']])
        else:
            st.success("Perfect Match! The model is 100% aligned with the 5% CFR rule in this selection.")

    if st.button("🪄 Generate AI Interpretation",key="Finally"):
        with st.spinner("Gemini is analyzing the trends..."):
            # Get dynamic insight
            dynamic_text = AI_Insights(Melted_df,context="prediction")
            
            # Display in a styled glass container
            st.markdown(f"""
            <div class="glass-chart" style="margin-top:20px;">
                <h3 style="color:white;">🤖 AI Data Interpretation</h3>
                <p style="color:white; font-size:1.1em;">{dynamic_text}</p>
            </div>
            """, unsafe_allow_html=True)

