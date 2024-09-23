import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

def generate_banking_data(days=365):
    # Initial date
    start_date = datetime(2023, 1, 1)
    
    # Generate dates
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Generate income (assuming a monthly salary with variations)
    base_salary = 2500  # Base monthly salary
    income = []
    for date in dates:
        if date.day == 1:  # Payday
            daily_income = np.random.normal(base_salary, 100)  # Variation in salary
        else:
            daily_income = 0
        income.append(max(0, daily_income))
    
    # Generate expenses
    fixed_expenses = 1000  # Monthly fixed expenses (rent, utilities, etc.)
    expenses = []
    for date in dates:
        if date.day == 1:  # Fixed expenses at the start of the month
            daily_expense = fixed_expenses + np.random.normal(200, 50)  # Variation in fixed expenses
        else:
            daily_expense = np.random.normal(30, 10)  # Variable daily expenses
        expenses.append(max(0, daily_expense))
    
    # Calculate balance
    balance = np.cumsum(np.array(income) - np.array(expenses))
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Income': income,
        'Expenses': expenses,
        'Balance': balance
    })
    
    return df

def main():
    st.title('Synthetic Banking Data Generator - Saver Profile')
    
    # Generate data
    df = generate_banking_data()
    
    # Display summary
    st.subheader('Financial Summary')
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${df['Income'].sum():.2f}")
    col2.metric("Total Expenses", f"${df['Expenses'].sum():.2f}")
    col3.metric("Final Balance", f"${df['Balance'].iloc[-1]:.2f}")
    
    # Balance over time chart
    fig_balance = px.line(df, x='Date', y='Balance', title='Balance Evolution')
    st.plotly_chart(fig_balance)
    
    # Income vs Expenses chart
    fig_income_expenses = px.line(df, x='Date', y=['Income', 'Expenses'], title='Income vs Expenses')
    st.plotly_chart(fig_income_expenses)
    
    # Display data in table
    st.subheader('Detailed Data')
    st.dataframe(df)

if __name__ == "__main__":
    main()