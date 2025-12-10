import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import base64
import os

# title 
st.title("Customers Churn Prediction")
st.write("this app uses a saved Naive Bayes model to predict customers churn")

# Dataset loading
script_directory = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_directory, 'churn_dataset.xlsx')
churn_df = pd.read_excel(dataset_path)
st.write(churn_df.head())

# loading Gaussian Naive Base 
# Build the path to the model file using the script_directory variable
model_path = os.path.join(script_directory, 'Customer_Churn_prediction.pk1')

# Load the model
model = joblib.load(model_path)

churn_labels = {0:"No",1:"Yes"}

# creating sliders
Age = st.sidebar.slider("Select Age", int(churn_df['Age'].min()), int(churn_df['Age'].max()), int(churn_df['Age'].mean()) )
Tenure =  st.sidebar.slider("Tenure in Years", int(churn_df['Tenure'].min()), int(churn_df['Tenure'].max()), int(churn_df['Tenure'].mean()) )
Sex =  st.sidebar.selectbox("Customer Gender", ('Male','Female') )

if Sex == 'Male':
    Sex = 0
else:
    Sex = 1
    
input_data = np.array([[Age,Tenure,Sex]])
 
prediction = model.predict(input_data)[0]

prediction_probability = model.predict_proba(input_data)[0]

st.subheader("Prediction Result")
st.write(f"Predicted Churn Status {churn_labels[prediction]}")

st.subheader("Prediction Probability")
st.write(f"Customer has Been not Churned **{prediction_probability[0]:.2%}**")
st.write(f"Customer has Been Churned **{prediction_probability[1]:.2%}**")

st.subheader("**Prediction Probability Pie Chart**")
fig, ax = plt.subplots()
fig.patch.set_facecolor('none')
ax.patch.set_facecolor('none')
labels = ['Not Churned' , 'churned']
data = prediction_probability
colors = ['#4FCA50',"#e90909"]
ax.pie(data, labels=labels ,startangle=90,colors=colors,autopct='%1.1f%%',textprops={'color':'white'})
fig.tight_layout()
ax.axis('equal') 
st.pyplot(fig)

# Making a background for the website
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
        background-size: 100% 100%;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: local; /* or fixed */
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Build the path to the image using the script_directory variable
image_path = os.path.join(script_directory, 'abstract-infographic-visualization-financial-chart-600nw-2428087473.webp')

# Load the image
st.image(image_path)
