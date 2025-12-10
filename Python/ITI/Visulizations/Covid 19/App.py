import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import base64


# PAGE CONFIGURATION

st.set_page_config(
    page_title="COVID-19 Global Dashboard",
    page_icon="🌍",
    layout="wide"
)


# BACKGROUND IMAGE SETUP

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background("Red-and-Blue-COVID-19-Virus.jpg")


# TITLE AND INTRODUCTION

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
    <h1>🌍 COVID-19 Global Dashboard</h1>
    <p>This interactive dashboard analyzes global COVID-19 trends, highlighting:</p>
    <div class='title-list'>
        - 📈 Global case, death, and recovery trends<br>
        - 🌎 Regional disparities in mortality<br>
        - 🖐️ Top 5 most affected countries<br>
    </div>
    <p><b>Data source:</b> Fully Grouped Data from World Health Organization</p>
</div>
""", unsafe_allow_html=True)

st.info("👉 Start by choosing a page from the left sidebar.")

st.set_page_config(page_title="World Analysis", page_icon="🌐", layout="wide")
st.markdown("<h2 style='text-align:center; color:white;'>🌍 World COVID-19 Data Analysis</h2>", unsafe_allow_html=True)

@st.cache_data
def load_world_data():
    df = pd.read_csv("worldometer_data.csv")
    float_cols = df.select_dtypes(include=['float64']).columns
    float_cols = float_cols.drop(['Tests/1M pop','Deaths/1M pop','Tot Cases/1M pop'])
    for col in float_cols:
        try:
            df[col] = df[col].astype('Int64')
        except Exception as e:
            print(f"Could not convert column '{col}'. Error: {e}")
    world_data =  df[df['Country/Region'] != 'Diamond Princess']
    mask = world_data['WHO Region'].isna()
    world_data.loc[mask, 'WHO Region'] = world_data.loc[mask, 'Continent']
    world_data = world_data.fillna(0,inplace=True)
    return df

world_data = load_world_data()

st.markdown(
    "<h2 style='text-align:center; color:white;'>🔍 Covid-19 World Data </h2>", 
    unsafe_allow_html=True
)

st.dataframe(world_data.head(5))


# 1️⃣ Correlation Heatmap
st.markdown(
    "<h2 style='text-align:center; color:white;'>🔥 Question 1: See the Correlations Between Columns</h2>", 
    unsafe_allow_html=True
)


# --- Data Cleaning ---
world_CP = world_data.copy()
world_CP = world_CP.select_dtypes(include=['number'])  # keep numeric only

# --- Compute Correlation ---
Correlations = world_CP.corr()


fig_corr = ff.create_annotated_heatmap(
    z=Correlations.values,
    x=list(Correlations.columns),
    y=list(Correlations.index),
    annotation_text=Correlations.values.round(2),
    colorscale="RdBu",
    showscale=True,
    reversescale=True,
)

fig_corr.update_layout(
    title=dict(
        text="Correlation Matrix of World COVID-19 Indicators",
        x=0.5,
        xanchor='center',
        font=dict(size=20, color='white')
    ),
    height=750,
    margin=dict(l=100, r=100, t=80, b=100),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)

st.plotly_chart(fig_corr, use_container_width=True)

# --- Optional Insight Section ---
with st.expander("🧠 Interpretation Tips"):
    st.markdown("""
    - **Positive correlations (red)** indicate that two variables increase together.
    - **Negative correlations (blue)** mean that as one increases, the other decreases.
    - Strong correlations (> 0.7 or < -0.7) suggest close relationships worth further analysis.
    """)


# -------------------------
# 2️⃣ Top 10 Countries by Metric
# -------------------------
st.markdown("<h2 style='text-align:center; color:white;'>📊 Top 10 Countries by Metrics</h2>", unsafe_allow_html=True)

metrics = ['TotalTests', 'TotalCases', 'TotalDeaths', 'TotalRecovered']

for metric in metrics:
    df_metric = (
        world_data.groupby('Country/Region')[metric]
        .sum()
        .reset_index()
        .sort_values(by=metric, ascending=False)
        .head(10)
    )

    fig_bar = px.bar(
        df_metric,
        x='Country/Region', y=metric,
        text=metric,
        color='Country/Region',
        title="📊Top 10 Countries by {metric}"
    )
    
    fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_bar.update_layout(   title=dict(
        text=f"📊 Top 10 Countries by {metric}",
        x=0.5,
        xanchor='center',
        font=dict(size=20, color='white')
    ),
        xaxis_title="Country/Region",
        yaxis_title=metric,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# 3️⃣ Combined Comparison

st.markdown("<h2 style='text-align:center; color:white;'>🌍 Comparison of Top 10 Countries by All Metrics</h2>", unsafe_allow_html=True)

totals = ['TotalTests', 'TotalCases', 'TotalDeaths', 'TotalRecovered']

totals_grouped = (
    world_data.groupby('Country/Region')[totals]
    .sum()
    .reset_index()
    .sort_values(by='TotalDeaths', ascending=False)
    .head(10)
)

totals_melted = totals_grouped.melt(
    id_vars=['Country/Region'],
    value_vars=totals,
    var_name='Metric',
    value_name='Number'
)

fig_melt = px.bar(
    totals_melted,
    x='Country/Region',
    y='Number',
    color='Metric',
    barmode='group',
    title="Top 10 Countries by Deaths, Cases, Tests & Recovery"
)
fig_melt.update_layout(    title=dict(
        text="🌐 Top 10 Countries by Deaths, Cases, Tests & Recovery",
        x=0.5,
        xanchor='center',
        font=dict(size=20, color='white')
    ),plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',height=600)
st.plotly_chart(fig_melt, use_container_width=True)


# LOAD DATA
st.set_page_config(page_title="Grouped Data Analysis", page_icon="📅", layout="wide")

st.markdown("<h2 style='text-align:center; color:white;'>🌍 World COVID-19 Data Analysis</h2>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("full_grouped.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

data = load_data()

st.markdown("<h2 style='text-align:center; color:white;'>Covid-19 Grouped Data </h2>", unsafe_allow_html=True)

st.dataframe(data)

# SIDEBAR FILTERS

st.sidebar.header("🧭 Dashboard Filters")

# --- Region Filter with "Select All" ---
all_regions = sorted(data['WHO Region'].dropna().unique())

select_all_regions = st.sidebar.checkbox("Select All Regions", value=True)

if select_all_regions:
    selected_region = st.sidebar.multiselect(
        "Select Region(s):",
        options=all_regions,
        default=all_regions
    )
else:
    selected_region = st.sidebar.multiselect(
        "Select Region(s):",
        options=all_regions,
        default=[]
    )

# --- Country Filter ---
all_countries = sorted(data['Country/Region'].dropna().unique())
selected_country = st.sidebar.multiselect(
    "Select Country(s):",
    options=all_countries,
    default=[]
)

# --- Date Filter ---
date_range = st.sidebar.date_input(
    "Select Date Range:",
    [data['Date'].min(), data['Date'].max()]
)


# APPLY FILTERS

# Convert sidebar date objects to pandas timestamps
start_date = pd.Timestamp(date_range[0])
end_date = pd.Timestamp(date_range[1])

filtered_data = data[
    (data['WHO Region'].isin(selected_region)) &
    (data['Date'].between(start_date, end_date))
]

if selected_country:
    filtered_data = filtered_data[filtered_data['Country/Region'].isin(selected_country)]


# GLOBAL TRENDS

st.markdown("<h2 style='text-align:center; color:white;'>🌐 Global Trends Over Time</h2>", unsafe_allow_html=True)

global_data = (
    filtered_data.groupby('Date')[['Confirmed', 'Deaths', 'Recovered']]
    .sum()
    .reset_index()
)

fig_global = px.line(
    global_data,
    x='Date', y=['Confirmed', 'Deaths', 'Recovered'],
    title="Global COVID-19 Progression (Filtered)",
    labels={'value': 'Number of Cases', 'variable': 'Metric'},
)
fig_global.update_layout(title=dict(text="🌐 Global COVID-19 Progression (Filtered)",
        x=0.5,
        xanchor='center',
        font=dict(size=20, color='white')
    ),
    template="plotly",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_global, use_container_width=True)


# REGIONAL IMPACT

st.markdown("<h2 style='text-align:center; color:white;'>🗺️ Regional Impact – Deaths per 1M Population", unsafe_allow_html=True)

region_deaths = (
    filtered_data.groupby('WHO Region')
    .agg({'Deaths': 'mean'})
    .reset_index()
    .sort_values('Deaths', ascending=False)
)

fig_region = px.bar(
    region_deaths,
    x='WHO Region', y='Deaths',
    color='WHO Region',
    title='Average Deaths per 1M Population by Region (Filtered)',
)
fig_region.update_layout(title=dict(
        text='🗺️ Average Deaths per 1M Population by Region (Filtered)',
        x=0.5,
        xanchor='center',
        font=dict(size=20, color='white')
    ),
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_region, use_container_width=True)


# TOP 5 AFFECTED COUNTRIES

st.markdown("<h2 style='text-align:center; color:white;'>🖐️ Top 5 Most Affected Countries",unsafe_allow_html=True)

top5 = (
    filtered_data.groupby('Country/Region')
    .agg({'Confirmed': 'max'})
    .sort_values('Confirmed', ascending=False)
    .head(5)
    .index.tolist()
)

cols = st.columns(5)
for i, country in enumerate(top5):
    subset = filtered_data[filtered_data['Country/Region'] == country]
    if subset.empty:
        continue
    last_row = subset.iloc[-1]

    labels = ['Active', 'Recovered', 'Deaths']
    values = [
        last_row.get('Active', 0),
        last_row.get('Recovered', 0),
        last_row.get('Deaths', 0)
    ]
    color_map = ['#1E90FF', '#2ECC71', '#E74C3C'] 

    fig_pie = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=color_map),
            textinfo='label+percent'
        )]
    )

    fig_pie.update_layout(
        title=f"{country} Case Distribution",
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    cols[i].plotly_chart(fig_pie, use_container_width=True)



# KEY FINDINGS

st.markdown("<h2 style='text-align:center; color:white;'>🔎 Key Findings",unsafe_allow_html=True)

st.success("""
**Top 3 Insights:**
1. Global infection waves peaked around Marsh and April.
2. Europe and the Americas show the highest mortality and Infection Rate per million.
3. Countries with higher population density saw faster spread like USA, India.
4- Countries with Smaller population density saw faster Recovery like Luxembourg, Monaco and UAE.
""")


# CONCLUSION

st.markdown("<h2 style='text-align:center; color:white;'>🧭 Conclusion",unsafe_allow_html=True)

st.success("""
- The pandemic’s impact varied widely by region and density.  
- Mortality correlated strongly with health system readiness.  
- **Lesson:** Global preparedness requires early detection, flexible infrastructure, and equitable access to healthcare.  
""")

st.success("End of Analysis — Thank you!")
