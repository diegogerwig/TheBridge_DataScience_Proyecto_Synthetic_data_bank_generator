import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from faker import Faker
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.set_page_config(layout="wide", page_title="Banking Data Generator", page_icon="💶")

fake = Faker('es_ES')
geolocator = Nominatim(user_agent="banking_data_generator")

BILBAO_COORDS = geolocator.geocode("Bilbao, Spain").point

def get_random_location(center, max_distance):
    while True:
        random_distance = random.uniform(0, max_distance)
        random_bearing = random.uniform(0, 360)
        random_point = geodesic(kilometers=random_distance).destination(center, random_bearing)
        location = geolocator.reverse(f"{random_point.latitude}, {random_point.longitude}")
        if location:
            return location.address

def generate_iban():
    country_code = "ES"
    bank_code = str(random.randint(1000, 9999))
    branch_code = str(random.randint(1000, 9999))
    account_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return f"{country_code}{bank_code}{branch_code}{account_number}"

def generate_banking_data(days, profile, job_category):
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()
    
    profiles = {
        'SAVER': {'savings_rate': 0.3, 'expense_mult': 0.8},
        'NEUTRAL': {'savings_rate': 0.1, 'expense_mult': 1.0},
        'SPENDER': {'savings_rate': 0.0, 'expense_mult': 1.2},
        'MIXED': {'savings_rate': 0.1, 'expense_mult': 1.0}  # Base values for mixed profile
    }
    
    job_categories = {
        'MANAGER': {'base_salary': 5000, 'salary_range': (4000, 6000)},
        'TECHNICIAN': {'base_salary': 3000, 'salary_range': (2500, 3500)},
        'WORKER': {'base_salary': 1500, 'salary_range': (1200, 1800)}
    }
    
    profile_data = profiles[profile]
    job_data = job_categories[job_category]
    base_salary = job_data['base_salary']
    
    transactions = []
    
    # Generate salary transactions
    current_date = start_date
    while current_date <= end_date:
        if current_date.day == 1:  # Salary day
            salary = np.random.uniform(*job_data['salary_range'])
            transactions.append({
                'Date': current_date + timedelta(hours=random.randint(9, 17), minutes=random.randint(0, 59)),
                'Type': 'Income',
                'Category': 'Salary',
                'Amount': salary,
                'Location': 'Bilbao, Spain'
            })
        current_date += timedelta(days=1)
    
    # Generate expense transactions
    expense_categories = {
        'Mortgage': {'ratio': 0.3, 'frequency': 30, 'location': 'Bilbao, Spain'},
        'Car': {'ratio': 0.15, 'frequency': 30, 'location': 'Bilbao, Spain'},
        'Food': {'ratio': 0.2, 'frequency': 3, 'location': lambda: get_random_location(BILBAO_COORDS, 20)},
        'Leisure': {'ratio': 0.15, 'frequency': 7, 'location': lambda: get_random_location(BILBAO_COORDS, 100)},
        'Utilities': {'ratio': 0.1, 'frequency': 30, 'location': 'Bilbao, Spain'},
        'Other': {'ratio': 0.1, 'frequency': 5, 'location': lambda: get_random_location(BILBAO_COORDS, 100)}
    }
    
    for category, info in expense_categories.items():
        current_date = start_date
        while current_date <= end_date:
            if random.random() < 1/info['frequency']:  # Probability of expense occurring
                if profile == 'MIXED':
                    current_profile = random.choice(['SAVER', 'NEUTRAL', 'SPENDER'])
                    current_profile_data = profiles[current_profile]
                else:
                    current_profile_data = profile_data
                
                expense_amount = base_salary * info['ratio'] * current_profile_data['expense_mult'] * np.random.normal(1, 0.1)
                location = info['location']() if callable(info['location']) else info['location']
                
                transactions.append({
                    'Date': current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                    'Type': 'Expense',
                    'Category': category,
                    'Amount': -abs(expense_amount),  # Ensure negative value for expenses
                    'Location': location
                })
            current_date += timedelta(days=1)
    
    # Generate extra income/expense events
    num_extra_events = int(days / 60)  # Approximately one event every two months
    for _ in range(num_extra_events):
        event_date = start_date + timedelta(days=random.randint(0, days))
        if random.choice([True, False]):  # 50% chance of extra income or expense
            amount = np.random.normal(base_salary * 0.5, base_salary * 0.1)
            category = 'Extra Income'
            location = 'Bilbao, Spain'
        else:
            amount = -np.random.normal(base_salary * 0.3, base_salary * 0.05)
            category = 'Extra Expense'
            location = get_random_location(BILBAO_COORDS, 20)
        
        transactions.append({
            'Date': event_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
            'Type': 'Income' if amount > 0 else 'Expense',
            'Category': category,
            'Amount': amount,
            'Location': location
        })
    
    # Create DataFrame and sort by date
    df = pd.DataFrame(transactions)
    df = df.sort_values('Date')
    
    # Calculate running balance
    df['Balance'] = df['Amount'].cumsum()
    
    return df

def format_euro(value):
    return f"€{value:.2f}"

def main():
    st.sidebar.title('💶 Banking Data Generator')
    
    name = st.sidebar.text_input("Name", value=fake.name())
    iban = st.sidebar.text_input("IBAN", value=generate_iban())
    city = st.sidebar.text_input("City", value="Bilbao")
    
    profile = st.sidebar.radio('Choose a profile:', ['SAVER', 'NEUTRAL', 'SPENDER', 'MIXED'])
    job_category = st.sidebar.radio('Choose a job category:', ['MANAGER', 'TECHNICIAN', 'WORKER'])
    
    years = st.sidebar.slider('Select number of years:', 1, 5, 3)  # Default to 3 years
    days = years * 365
    
    if st.sidebar.button('Generate Data'):
        st.title('Synthetic Banking Data Generator')
        st.subheader(f'Profile: {profile} | Job: {job_category}')
        
        st.write(f"Name: {name}")
        st.write(f"IBAN: {iban}")
        st.write(f"City: {city}")
        
        df = generate_banking_data(days=days, profile=profile, job_category=job_category)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Income", format_euro(df[df['Amount'] > 0]['Amount'].sum()), "💰")
        col2.metric("Total Expenses", format_euro(abs(df[df['Amount'] < 0]['Amount'].sum())), "💸")
        col3.metric("Number of Transactions", len(df), "🧾")
        col4.metric("Final Balance", format_euro(df['Balance'].iloc[-1]), "🏦")
        
        st.markdown("---")
        
        col_balance, col_income_expenses = st.columns(2)
        
        with col_balance:
            fig_balance = px.line(df, x='Date', y='Balance', title='Balance Evolution')
            fig_balance.update_layout(height=400)
            st.plotly_chart(fig_balance, use_container_width=True)
        
        with col_income_expenses:
            income_expense_df = df.groupby('Type')['Amount'].sum().reset_index()
            income_expense_df['Amount'] = income_expense_df['Amount'].abs()
            fig_income_expenses = px.pie(income_expense_df, values='Amount', names='Type', title='Income vs Expenses')
            fig_income_expenses.update_traces(textposition='inside', textinfo='percent+label')
            fig_income_expenses.update_layout(height=400)
            st.plotly_chart(fig_income_expenses, use_container_width=True)
        
        st.markdown("---")
        
        expense_categories = df[df['Amount'] < 0].groupby('Category')['Amount'].sum().abs().sort_values(ascending=True)
        
        col_pie, col_bar = st.columns(2)
        
        with col_pie:
            fig_expenses_pie = px.pie(values=expense_categories.values, names=expense_categories.index, title='Expense Distribution')
            fig_expenses_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_expenses_pie.update_layout(height=400)
            st.plotly_chart(fig_expenses_pie, use_container_width=True)
        
        with col_bar:
            fig_expenses_bar = go.Figure(data=[go.Bar(x=expense_categories.values, y=expense_categories.index, orientation='h')])
            fig_expenses_bar.update_layout(title='Total Expenses by Category', height=400)
            st.plotly_chart(fig_expenses_bar, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader('Detailed Data')
        
        df['Amount'] = df['Amount'].apply(format_euro)
        df['Balance'] = df['Balance'].apply(format_euro)
        
        st.dataframe(df)
        
        # Export data to CSV
        if not os.path.exists('data'):
            os.makedirs('data')
        
        csv_filename = f"data/{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_filename, index=False)
        st.success(f"Data exported to {csv_filename}")

if __name__ == "__main__":
    main()