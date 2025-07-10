# data_utils.py

import pandas as pd

def load_data(uploaded_file) -> pd.DataFrame:
    df = pd.read_csv(uploaded_file)

    # Normalize column names
    df.columns = [col.strip().capitalize() for col in df.columns]

    # Check required columns
    required = {'Date', 'Category', 'Amount'}
    if not required.issubset(set(df.columns)):
        raise ValueError("CSV must contain 'Date', 'Category', and 'Amount' columns.")

    # Convert types
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    # Drop invalid entries
    df = df.dropna(subset=['Date', 'Amount', 'Category'])

    return df
