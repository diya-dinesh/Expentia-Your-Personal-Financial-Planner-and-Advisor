# recommender.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_spending_patterns(df: pd.DataFrame) -> dict:
    df['Date'] = pd.to_datetime(df['Date'])
    current_month = df['Date'].dt.to_period('M').max()
    last_month = current_month - 1
    
    current_month_data = df[df['Date'].dt.to_period('M') == current_month]
    last_month_data = df[df['Date'].dt.to_period('M') == last_month]
    
    current_month_spend = current_month_data['Amount'].sum()
    last_month_spend = last_month_data['Amount'].sum()
    
    # Calculate daily average safely
    daily_spends = current_month_data.groupby(current_month_data['Date'].dt.date)['Amount'].sum()
    daily_average = daily_spends.mean() if not daily_spends.empty else 0
    
    return {
        'current_month_spend': current_month_spend,
        'last_month_spend': last_month_spend,
        'category_trends': current_month_data.groupby('Category')['Amount'].sum().to_dict(),
        'daily_average': daily_average
    }

def generate_recommendations(df: pd.DataFrame) -> list:
    recommendations = []
    analysis = analyze_spending_patterns(df)
    
    # Monthly Spending Analysis
    if analysis['last_month_spend'] > 0:  # Only calculate if there was spending last month
        if analysis['current_month_spend'] > analysis['last_month_spend']:
            increase = ((analysis['current_month_spend'] - analysis['last_month_spend']) / 
                       analysis['last_month_spend'] * 100)
            recommendations.append(
                f"Your spending has increased by {increase:.1f}% compared to last month. "
                "Consider reviewing your recent expenses."
            )
        elif analysis['current_month_spend'] < analysis['last_month_spend']:
            decrease = ((analysis['last_month_spend'] - analysis['current_month_spend']) / 
                       analysis['last_month_spend'] * 100)
            recommendations.append(
                f"Great job! Your spending has decreased by {decrease:.1f}% compared to last month."
            )
    else:
        recommendations.append(
            "This is your first month of tracking. Keep monitoring your expenses to get personalized recommendations."
        )
    
    # Category-wise Analysis
    total_spend = analysis['current_month_spend']
    if total_spend > 0: 
        for category, amount in analysis['category_trends'].items():
            percentage = (amount / total_spend) * 100
            
            if percentage > 30:
                recommendations.append(
                    f"Your {category} expenses ({percentage:.1f}% of total) are quite high. "
                    "Consider setting a budget for this category."
                )
    
    # Daily Spending Pattern
    if analysis['daily_average'] > 2000:
        recommendations.append(
            f"Your average daily spending (₹{analysis['daily_average']:.2f}) is high. "
            "Try to reduce non-essential expenses."
        )
    
    # Savings Analysis
    if 'Savings' in df['Category'].unique():
        savings = df[df['Category'] == 'Savings']['Amount'].sum()
        if total_spend > 0:  # Avoid division by zero
            savings_rate = (savings / total_spend) * 100
            if savings_rate < 20:
                recommendations.append(
                    f"Your savings rate is {savings_rate:.1f}% of monthly spending. "
                    "Consider increasing your savings rate for better financial security."
                )
    else:
        recommendations.append(
            "Start tracking your savings! Aim to save at least 20% of your monthly income."
        )
    
    # Irregular Expense Detection
    df['Date'] = pd.to_datetime(df['Date'])
    daily_spend = df.groupby(df['Date'].dt.date)['Amount'].sum()
    if len(daily_spend) > 1 and daily_spend.std() > 2000:
        recommendations.append(
            "Your spending pattern is irregular. Try to maintain consistent daily spending habits."
        )
    
    # Investment Opportunity
    if analysis['last_month_spend'] > 0 and analysis['current_month_spend'] < analysis['last_month_spend']:
        savings = analysis['last_month_spend'] - analysis['current_month_spend']
        recommendations.append(
            f"You saved ₹{savings:.2f} this month compared to last month. "
            "Consider investing this amount in a mutual fund or fixed deposit."
        )
    
    if not recommendations:
        recommendations.append("Your spending pattern looks balanced. Great job managing your finances!")
    
    return recommendations
