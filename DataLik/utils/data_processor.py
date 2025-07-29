import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import openpyxl
import streamlit as st

def process_uploaded_file(uploaded_file):
    """Process uploaded CSV or Excel file"""
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            # Try different encodings for CSV
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)  # Reset file pointer
                df = pd.read_csv(uploaded_file, encoding='latin1')
        
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        else:
            return None
        
        # Basic data cleaning
        df.columns = df.columns.str.strip()  # Remove whitespace from column names
        
        return df
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def validate_data(df):
    """Validate data quality and return validation results"""
    results = {
        'missing_values': 0,
        'duplicates': 0,
        'quality_score': 100.0,
        'issues': []
    }
    
    # Check for missing values
    missing_count = df.isnull().sum().sum()
    results['missing_values'] = missing_count
    
    if missing_count > 0:
        missing_percentage = (missing_count / (len(df) * len(df.columns))) * 100
        results['quality_score'] -= missing_percentage
        results['issues'].append(f"Found {missing_count} missing values ({missing_percentage:.1f}% of data)")
    
    # Check for duplicates
    duplicate_count = df.duplicated().sum()
    results['duplicates'] = duplicate_count
    
    if duplicate_count > 0:
        duplicate_percentage = (duplicate_count / len(df)) * 100
        results['quality_score'] -= duplicate_percentage
        results['issues'].append(f"Found {duplicate_count} duplicate rows ({duplicate_percentage:.1f}%)")
    
    # Check for data type consistency
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if numeric column is stored as text
            try:
                pd.to_numeric(df[col], errors='raise')
                results['issues'].append(f"Column '{col}' appears to be numeric but stored as text")
            except:
                pass
    
    # Ensure quality score doesn't go below 0
    results['quality_score'] = max(0, results['quality_score'])
    
    return results

def clean_data(df, remove_duplicates=True, handle_missing="Keep as is", standardize_dates=True):
    """Clean data based on user preferences"""
    try:
        cleaned_df = df.copy()
        
        # Remove duplicates
        if remove_duplicates:
            cleaned_df = cleaned_df.drop_duplicates()
        
        # Handle missing values
        if handle_missing == "Remove rows":
            cleaned_df = cleaned_df.dropna()
        elif handle_missing == "Fill with 0":
            cleaned_df = cleaned_df.fillna(0)
        elif handle_missing == "Fill with mean":
            numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
        
        # Standardize date formats
        if standardize_dates:
            for col in cleaned_df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                    except:
                        pass
        
        return cleaned_df
        
    except Exception as e:
        st.error(f"Error cleaning data: {str(e)}")
        return None

def load_sample_data():
    """Load sample business data for demonstration"""
    # Generate sample business data
    np.random.seed(42)  # For reproducible results
    
    # Date range for the last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Sample data generation
    data = []
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
    customers = [f'Customer_{i:03d}' for i in range(1, 101)]
    
    for date in date_range:
        # Generate 1-10 transactions per day
        num_transactions = np.random.randint(1, 11)
        
        for _ in range(num_transactions):
            product = np.random.choice(products)
            category = np.random.choice(categories)
            customer = np.random.choice(customers)
            
            # Generate realistic business metrics
            quantity = np.random.randint(1, 6)
            base_price = np.random.uniform(10, 100)
            price = round(base_price, 2)
            revenue = round(quantity * price, 2)
            cost = round(revenue * np.random.uniform(0.4, 0.8), 2)
            profit = round(revenue - cost, 2)
            
            # Add some seasonality
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * date.dayofyear / 365)
            revenue *= seasonal_factor
            profit *= seasonal_factor
            
            data.append({
                'date': date,
                'product': product,
                'category': category,
                'customer': customer,
                'quantity': quantity,
                'price': price,
                'revenue': round(revenue, 2),
                'cost': round(cost, 2),
                'profit': round(profit, 2)
            })
    
    return pd.DataFrame(data)

def get_kpi_metrics(data):
    """Calculate key performance indicators from data"""
    metrics = {}
    
    if data.empty:
        return {
            'total_revenue': 0,
            'total_orders': 0,
            'active_customers': 0,
            'avg_order_value': 0,
            'revenue_growth': 0,
            'order_growth': 0,
            'customer_growth': 0,
            'aov_growth': 0
        }
    
    # Current period metrics
    if 'revenue' in data.columns:
        metrics['total_revenue'] = data['revenue'].sum()
    else:
        metrics['total_revenue'] = 0
    
    metrics['total_orders'] = len(data)
    
    if 'customer' in data.columns:
        metrics['active_customers'] = data['customer'].nunique()
    else:
        metrics['active_customers'] = 0
    
    metrics['avg_order_value'] = metrics['total_revenue'] / metrics['total_orders'] if metrics['total_orders'] > 0 else 0
    
    # Calculate growth rates (compare last 30 days to previous 30 days)
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'])
        latest_date = data['date'].max()
        
        # Current period (last 30 days)
        current_start = latest_date - timedelta(days=30)
        current_data = data[data['date'] >= current_start]
        
        # Previous period (30 days before that)
        previous_start = current_start - timedelta(days=30)
        previous_data = data[(data['date'] >= previous_start) & (data['date'] < current_start)]
        
        if not previous_data.empty and not current_data.empty:
            # Revenue growth
            current_revenue = current_data['revenue'].sum() if 'revenue' in current_data.columns else 0
            previous_revenue = previous_data['revenue'].sum() if 'revenue' in previous_data.columns else 0
            metrics['revenue_growth'] = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            # Order growth
            current_orders = len(current_data)
            previous_orders = len(previous_data)
            metrics['order_growth'] = ((current_orders - previous_orders) / previous_orders * 100) if previous_orders > 0 else 0
            
            # Customer growth
            if 'customer' in data.columns:
                current_customers = current_data['customer'].nunique()
                previous_customers = previous_data['customer'].nunique()
                metrics['customer_growth'] = ((current_customers - previous_customers) / previous_customers * 100) if previous_customers > 0 else 0
            else:
                metrics['customer_growth'] = 0
            
            # AOV growth
            current_aov = current_revenue / current_orders if current_orders > 0 else 0
            previous_aov = previous_revenue / previous_orders if previous_orders > 0 else 0
            metrics['aov_growth'] = ((current_aov - previous_aov) / previous_aov * 100) if previous_aov > 0 else 0
        else:
            metrics['revenue_growth'] = 0
            metrics['order_growth'] = 0
            metrics['customer_growth'] = 0
            metrics['aov_growth'] = 0
    else:
        metrics['revenue_growth'] = 0
        metrics['order_growth'] = 0
        metrics['customer_growth'] = 0
        metrics['aov_growth'] = 0
    
    return metrics

def filter_data_by_date(data, start_date, end_date):
    """Filter data by date range"""
    if 'date' not in data.columns:
        return data
    
    data['date'] = pd.to_datetime(data['date'])
    return data[(data['date'] >= pd.to_datetime(start_date)) & (data['date'] <= pd.to_datetime(end_date))]

def get_analytics_insights(data):
    """Generate analytical insights from data"""
    insights = {
        'key_insights': [],
        'performance_metrics': {}
    }
    
    if data.empty:
        insights['key_insights'] = ["No data available for analysis"]
        return insights
    
    # Revenue insights
    if 'revenue' in data.columns:
        total_revenue = data['revenue'].sum()
        avg_revenue = data['revenue'].mean()
        insights['performance_metrics']['total_revenue'] = f"${total_revenue:,.2f}"
        insights['performance_metrics']['average_transaction'] = f"${avg_revenue:.2f}"
        
        if total_revenue > 100000:
            insights['key_insights'].append("Strong revenue performance with total exceeding $100K")
        
        # Revenue trend
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            recent_data = data.tail(30)['revenue'].sum()
            earlier_data = data.head(30)['revenue'].sum()
            
            if recent_data > earlier_data:
                insights['key_insights'].append("Revenue trending upward over time")
            else:
                insights['key_insights'].append("Revenue may need attention - showing decline")
    
    # Customer insights
    if 'customer' in data.columns:
        unique_customers = data['customer'].nunique()
        insights['performance_metrics']['unique_customers'] = unique_customers
        
        if unique_customers > 50:
            insights['key_insights'].append("Good customer diversity with 50+ unique customers")
    
    # Product insights
    if 'product' in data.columns:
        top_product = data['product'].value_counts().index[0]
        insights['key_insights'].append(f"Top selling product: {top_product}")
    
    return insights

def calculate_trends(data, metric_column):
    """Calculate trends for a specific metric"""
    if 'date' not in data.columns or metric_column not in data.columns:
        return data
    
    # Ensure date column is datetime
    data['date'] = pd.to_datetime(data['date'])
    
    # Group by date and calculate daily aggregates
    daily_data = data.groupby('date')[metric_column].sum().reset_index()
    
    # Calculate rolling averages and trends
    daily_data['rolling_7'] = daily_data[metric_column].rolling(window=7, min_periods=1).mean()
    daily_data['rolling_30'] = daily_data[metric_column].rolling(window=30, min_periods=1).mean()
    
    # Calculate trend slope (simple linear regression)
    if len(daily_data) > 1:
        x = np.arange(len(daily_data))
        y = daily_data[metric_column].values
        trend_slope = np.polyfit(x, y, 1)[0]
        daily_data['trend_slope'] = trend_slope
    
    return daily_data
