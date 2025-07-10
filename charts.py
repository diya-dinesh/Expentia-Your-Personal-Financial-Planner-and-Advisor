# charts.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_charts(df: pd.DataFrame):
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "Spending Overview", 
        "Category Analysis", 
        "Trend Analysis",
        "Budget vs Actual"
    ])
    
    with tab1:
        st.subheader("Monthly Spending Overview")
        monthly_spend = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum()
        monthly_spend.index = monthly_spend.index.astype(str)
        
        fig = px.bar(
            monthly_spend,
            title="Monthly Spending Trend",
            labels={'value': 'Amount (₹)', 'index': 'Month'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Category-wise Analysis")
        category_spend = df.groupby('Category')['Amount'].sum().sort_values(ascending=True)
        
        fig = px.pie(
            values=category_spend.values,
            names=category_spend.index,
            title="Spending by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show top 3 categories
        st.write("Top 3 Spending Categories:")
        for category, amount in category_spend.nlargest(3).items():
            st.write(f"- {category}: ₹{amount:,.2f}")
    
    with tab3:
        st.subheader("Daily Spending Trend")
        daily_spend = df.groupby(df['Date'].dt.date)['Amount'].sum()
        
        fig = px.line(
            daily_spend,
            title="Daily Spending Pattern",
            labels={'value': 'Amount (₹)', 'index': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show spending statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Daily Spend", f"₹{daily_spend.mean():,.2f}")
        with col2:
            st.metric("Highest Daily Spend", f"₹{daily_spend.max():,.2f}")
        with col3:
            st.metric("Lowest Daily Spend", f"₹{daily_spend.min():,.2f}")
    
    with tab4:
        st.subheader("Budget vs Actual Spending")
        # Calculate monthly averages for each category
        monthly_category_avg = df.groupby(['Category', df['Date'].dt.to_period('M')])['Amount'].sum().groupby('Category').mean()
        
        # Create a sample budget (you can modify this based on your needs)
        budget = monthly_category_avg * 1.1  # 10% higher than average as budget
        
        # Create comparison chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Actual',
            x=monthly_category_avg.index,
            y=monthly_category_avg.values,
            marker_color='rgb(55, 83, 109)'
        ))
        fig.add_trace(go.Bar(
            name='Budget',
            x=budget.index,
            y=budget.values,
            marker_color='rgb(26, 118, 255)'
        ))
        
        fig.update_layout(
            title="Category-wise Budget vs Actual",
            barmode='group',
            xaxis_title="Category",
            yaxis_title="Amount (₹)"
        )
        st.plotly_chart(fig, use_container_width=True)
