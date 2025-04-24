import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import re 

#Set the page configuration
st.set_page_config(page_title="Chicken Recipes", layout="wide")

#Create a title and subheader
st.title('Bob''s Watches Luxury Watch Resale App')
st.write("This is an app meant to display trends and analytics for the watches listed on [Bob's Watches](https://www.bobswatches.com/)." )

#Read in and display the data
data = pd.read_csv('chicken_recipes.csv')
st.dataframe(data)