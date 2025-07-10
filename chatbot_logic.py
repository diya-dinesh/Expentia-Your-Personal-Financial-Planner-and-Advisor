import pandas as pd
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv("api.env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in api.env")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash')

# Format currency nicely
def format_currency(amount):
    return f"₹{amount:,.2f}"

# Detect intent using Gemini
def get_intent(query):
    try:
        print(f"\nProcessing query: {query}")
        print("Initializing Gemini model...")
        
        prompt = f"""
Respond only with a JSON object like:
{{"intent": "intent_name", "confidence": 0.0_to_1.0"}}
Available intents: category_spending, monthly_spending, budget_analysis, savings_analysis, investment_advice, general_inquiry
Query: {query}
Do not include markdown or code block formatting.
"""
        print("Sending request to Gemini API...")
        response = model.generate_content(prompt)
        print(f"Raw Gemini response: {response.text}")
        
        raw = response.text.strip()
        print(f"Cleaned response: {raw}")

        # Remove markdown formatting if present
        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            print(f"After removing markdown: {raw}")
        
        result = json.loads(raw)
        print(f"Parsed result: {result}")
        
        return result if "intent" in result else {"intent": "general_inquiry", "confidence": 0.5}
    except Exception as e:
        print(f"Error in intent detection: {str(e)}")
        return {"intent": "general_inquiry", "confidence": 0.5}

# Analyze savings pattern
def get_savings_insights(df):
    total_spent = df['Amount'].sum()
    daily_avg = total_spent / 30
    category_summary = df.groupby("Category")["Amount"].sum()
    breakdown = "\n".join([f"- {k}: {format_currency(v)}" for k, v in category_summary.items()])
    
    return {
        "total_spent": format_currency(total_spent),
        "daily_avg": format_currency(daily_avg),
        "category_breakdown": breakdown
    }

# Get monthly spending
def get_monthly_spending(df, month_name):
    df['Date'] = pd.to_datetime(df['Date'])
    month_data = df[df['Date'].dt.strftime('%B').str.lower() == month_name.lower()]
    
    if month_data.empty:
        return None
        
    total = month_data['Amount'].sum()
    category_summary = month_data.groupby("Category")["Amount"].sum()
    breakdown = "\n".join([f"- {k}: {format_currency(v)}" for k, v in category_summary.items()])
    
    return {
        "total": format_currency(total),
        "category_breakdown": breakdown,
        "daily_avg": format_currency(total / len(month_data['Date'].dt.date.unique()))
    }

# Handle query
def handle_query(df, query):
    intent_result = get_intent(query)
    intent = intent_result['intent']
    
    # Check for month-specific queries
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
             'july', 'august', 'september', 'october', 'november', 'december']
    
    for month in months:
        if month in query.lower():
            monthly_data = get_monthly_spending(df, month)
            if monthly_data:
                return f"""Your spending in {month.capitalize()}:
                
Total Spent: {monthly_data['total']}
Daily Average: {monthly_data['daily_avg']}

Category Breakdown:
{monthly_data['category_breakdown']}"""
            else:
                return f"I don't have any spending data for {month.capitalize()}."

    # Check for spending reduction queries
    if any(word in query.lower() for word in ['reduce', 'cut', 'save', 'spending', 'expenses', 'budget']):
        insights = get_savings_insights(df)
        return f"""Here are specific recommendations to reduce your spending:

1. Current Spending Overview:
Total Spent: {insights['total_spent']}
Daily Average: {insights['daily_avg']}

2. Top Spending Categories:
{insights['category_breakdown']}

3. Actionable Tips:
- Set a daily spending limit of ₹1,500
- Track your expenses throughout the day
- Use cash for discretionary spending
- Review and cancel unused subscriptions
- Plan major purchases in advance
- Use cashback and reward programs
- Consider bulk buying for frequently used items
- Look for discounts and deals

4. Quick Wins:
- Review your top 3 spending categories
- Set up automatic savings transfers
- Use budgeting apps to track expenses
- Cook meals at home instead of eating out
- Use public transportation when possible

Would you like more specific recommendations for any particular category?"""

    # Let Gemini handle investment queries directly
    if any(word in query.lower() for word in ['invest', 'investment', 'stock', 'stocks', 'market', 'trading']):
        try:
            insights = get_savings_insights(df)
            prompt = f"""Based on this user's spending data:
            Total Spent: {insights['total_spent']}
            Daily Average: {insights['daily_avg']}
            Category Breakdown: {insights['category_breakdown']}
            
            Provide personalized investment advice for this query: {query}
            Focus on:
            1. Current financial health assessment
            2. Investment readiness
            3. Specific investment recommendations
            4. Next steps to get started
            
            Format the response in a clear, structured way."""
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in investment advice: {str(e)}")
            return "I apologize, but I'm having trouble generating investment advice right now. Please try again later."

    if intent == "savings_analysis":
        insights = get_savings_insights(df)
        return f"""Here's your savings analysis:

Total Spent: {insights['total_spent']}
Daily Avg: {insights['daily_avg']}

Top Spending Categories:
{insights['category_breakdown']}

Tips:
- Track your top 3 spending areas weekly.
- Set a daily budget and stick to it.
- Consider reviewing monthly subscriptions.
"""

    return "I'm here to help with your expenses. Ask me about your savings, monthly spending, or investment tips!"

