# app.py
import streamlit as st
import pandas as pd
from chatbot_logic import handle_query
from recommender import generate_recommendations
from charts import show_charts
from data_utils import load_data

st.set_page_config(page_title="Expentia - Smart Expense Tracker", layout="wide")
st.title("Expentia – Your Smart Expense Explainer")

uploaded_file = st.file_uploader("Upload your expense CSV", type="csv")

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### Your Expense Data")
    st.dataframe(df.head())

    st.write("---")
    st.write("### Ask Expentia about your spending")
    user_input = st.text_input("Type your question here")

    if user_input:
        response = handle_query(df, user_input)
        st.write(f"**Answer:** {response}")

    st.write("---")
    st.write("### Your Spending Charts")
    show_charts(df)

    st.write("---")
    st.write("### Smart Recommendations")
    recommendations = generate_recommendations(df)
    for rec in recommendations:
        st.info(rec)
else:
    st.warning("Please upload a CSV file to begin.")
