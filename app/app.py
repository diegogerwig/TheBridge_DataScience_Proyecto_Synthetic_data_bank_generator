import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(layout="wide", page_title="Banking Data Generator", page_icon="💶")

def generate_banking_data(days=365, profile='normal'):
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    profiles = {
        'saver': {'base_salary': 2500, 'savings_rate': 0.3, 'expense_mult': 0.8},
        'normal': {'base_salary': 2500, 'savings_rate': 0.1, 'expense_mult': 1.0},
        'spender': {'base_salary': 2500, 'savings_rate': 0.0, 'expense_mult': 1.2}
    }
    
    profile_data = profiles[profile]
    base_salary = profile_data['base_salary']
    
    income = []
    extra_income = []
    for date in dates:
        if date.day == 1:
            monthly_income = np.random.normal(base_salary, base_salary * 0.1)
        else:
            monthly_income = 0
        income.append(max(0, monthly_income))
        extra_income.append(0)  # Inicializamos extra_income con ceros
    
    expense_categories = {
        'Mortgage': {'ratio': 0.3, 'day': 5},
        'Car': {'ratio': 0.15, 'day': 10},
        'Food': {'ratio': 0.2, 'day': range(1, 29, 7)},  # Weekly
        'Leisure': {'ratio': 0.15, 'day': range(1, 31)},  # Random days
        'Utilities': {'ratio': 0.1, 'day': 15},
        'Other': {'ratio': 0.1, 'day': range(1, 31)}  # Random days
    }
    
    expenses = {category: [] for category in expense_categories}
    total_expenses = []
    extra_expenses = []
    
    # Generar ingresos/gastos extras cada 2-3 meses
    extra_events = []
    current_month = start_date.month
    months_since_last_event = 0
    for date in dates:
        if date.month != current_month:
            current_month = date.month
            months_since_last_event += 1
            if months_since_last_event >= random.randint(2, 3):
                extra_events.append(date)
                months_since_last_event = 0
    
    for date in dates:
        daily_expense = 0
        monthly_expense = base_salary * (1 - profile_data['savings_rate']) * profile_data['expense_mult']
        
        for category, info in expense_categories.items():
            category_expense = 0
            if isinstance(info['day'], int) and date.day == info['day']:
                category_expense = monthly_expense * info['ratio'] * np.random.normal(1, 0.1)
            elif isinstance(info['day'], range) and date.day in info['day']:
                category_expense = (monthly_expense * info['ratio'] / len(info['day'])) * np.random.normal(1, 0.1)
            
            expenses[category].append(max(0, category_expense))
            daily_expense += category_expense
        
        total_expenses.append(daily_expense)
        extra_expenses.append(0)  # Inicializamos extra_expenses con ceros
        
        # Añadir ingreso o gasto extra si es un día de evento extra
        if date in extra_events:
            if random.choice([True, False]):  # 50% de probabilidad de ingreso o gasto extra
                extra_income[dates.index(date)] = np.random.normal(base_salary * 0.5, base_salary * 0.1)
            else:
                extra_expenses[dates.index(date)] = np.random.normal(base_salary * 0.3, base_salary * 0.05)
    
    balance = np.cumsum(np.array(income) + np.array(extra_income) - np.array(total_expenses) - np.array(extra_expenses))
    
    df = pd.DataFrame({
        'Date': dates,
        'Income': income,
        'Extra Income': extra_income,
        'Total Expenses': total_expenses,
        'Extra Expenses': extra_expenses,
        'Balance': balance,
        **expenses
    })
    
    return df

def format_euro(value):
    return f"€{value:.2f}"

def main():
    st.sidebar.title('💶 Banking Data Generator')
    profile = st.sidebar.radio('Choose a profile:', ['saver', 'normal', 'spender'])
    
    st.title('Synthetic Banking Data Generator')
    st.subheader(f'Selected Profile: {profile.capitalize()}')
    
    df = generate_banking_data(profile=profile)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Income", format_euro(df['Income'].sum()), "💰")
    col2.metric("Extra Income", format_euro(df['Extra Income'].sum()), "🎉")
    col3.metric("Total Expenses", format_euro(df['Total Expenses'].sum()), "💸")
    col4.metric("Extra Expenses", format_euro(df['Extra Expenses'].sum()), "😱")
    col5.metric("Final Balance", format_euro(df['Balance'].iloc[-1]), "🏦")
    
    st.markdown("---")
    
    col_balance, col_income_expenses = st.columns(2)
    
    with col_balance:
        fig_balance = px.line(df, x='Date', y='Balance', title='Balance Evolution')
        fig_balance.update_layout(height=400)
        st.plotly_chart(fig_balance, use_container_width=True)
    
    with col_income_expenses:
        fig_income_expenses = px.line(df, x='Date', y=['Income', 'Extra Income', 'Total Expenses', 'Extra Expenses'], title='Income vs Expenses')
        fig_income_expenses.update_layout(height=400)
        st.plotly_chart(fig_income_expenses, use_container_width=True)
    
    st.markdown("---")
    
    expense_categories = ['Mortgage', 'Car', 'Food', 'Leisure', 'Utilities', 'Other', 'Extra Expenses']
    total_by_category = df[expense_categories].sum()
    
    col_pie, col_bar = st.columns(2)
    
    with col_pie:
        fig_expenses_pie = px.pie(values=total_by_category.values, names=total_by_category.index, title='Expense Distribution')
        fig_expenses_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_expenses_pie.update_layout(height=400)
        st.plotly_chart(fig_expenses_pie, use_container_width=True)
    
    with col_bar:
        fig_expenses_bar = go.Figure(data=[go.Bar(x=total_by_category.index, y=total_by_category.values)])
        fig_expenses_bar.update_layout(title='Total Expenses by Category', height=400)
        st.plotly_chart(fig_expenses_bar, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader('Detailed Data')
    
    # Format numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        df[col] = df[col].apply(format_euro)
    
    st.dataframe(df)

if __name__ == "__main__":
    main()