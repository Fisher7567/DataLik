import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sales_chart(data):
    """Create sales performance chart"""
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    if 'date' in data.columns:
        # Daily sales volume
        daily_sales = data.groupby('date').size().reset_index(name='orders')
        fig = px.line(daily_sales, x='date', y='orders', 
                     title='Daily Order Volume',
                     labels={'orders': 'Number of Orders', 'date': 'Date'})
        fig.update_traces(line_color='#FF6B35')
    else:
        # If no date column, show product sales
        if 'product' in data.columns:
            product_sales = data['product'].value_counts().reset_index()
            product_sales.columns = ['product', 'count']
            fig = px.bar(product_sales.head(10), x='product', y='count',
                        title='Top 10 Products by Sales Volume')
        else:
            fig = go.Figure()
            fig.add_annotation(text="Insufficient data for sales chart", x=0.5, y=0.5, showarrow=False)
    
    fig.update_layout(height=400)
    return fig

def create_revenue_chart(data):
    """Create revenue trend chart"""
    if data.empty or 'revenue' not in data.columns:
        fig = go.Figure()
        fig.add_annotation(text="No revenue data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    if 'date' in data.columns:
        # Daily revenue
        daily_revenue = data.groupby('date')['revenue'].sum().reset_index()
        
        fig = px.line(daily_revenue, x='date', y='revenue',
                     title='Daily Revenue Trend',
                     labels={'revenue': 'Revenue ($)', 'date': 'Date'})
        
        # Add moving average
        daily_revenue['ma_7'] = daily_revenue['revenue'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=daily_revenue['date'], y=daily_revenue['ma_7'],
                       mode='lines', name='7-day MA', line=dict(dash='dash'))
        
        fig.update_traces(line_color='#28A745')
    else:
        # Show revenue by category if available
        if 'category' in data.columns:
            category_revenue = data.groupby('category')['revenue'].sum().reset_index()
            fig = px.bar(category_revenue, x='category', y='revenue',
                        title='Revenue by Category')
        else:
            fig = px.histogram(data, x='revenue', title='Revenue Distribution')
    
    fig.update_layout(height=400)
    return fig

def create_customer_chart(data):
    """Create customer analysis chart"""
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No customer data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    if 'customer' in data.columns and 'date' in data.columns:
        # Customer acquisition over time
        customer_first_purchase = data.groupby('customer')['date'].min().reset_index()
        customer_first_purchase['month'] = pd.to_datetime(customer_first_purchase['date']).dt.to_period('M')
        monthly_new_customers = customer_first_purchase.groupby('month').size().reset_index(name='new_customers')
        monthly_new_customers['month'] = monthly_new_customers['month'].dt.to_timestamp()
        
        fig = px.bar(monthly_new_customers, x='month', y='new_customers',
                    title='New Customer Acquisition by Month',
                    labels={'new_customers': 'New Customers', 'month': 'Month'})
        fig.update_traces(marker_color='#17A2B8')
        
    elif 'customer' in data.columns:
        # Customer transaction frequency
        customer_frequency = data['customer'].value_counts().reset_index()
        customer_frequency.columns = ['customer', 'transactions']
        
        fig = px.histogram(customer_frequency, x='transactions',
                          title='Customer Transaction Frequency Distribution',
                          labels={'transactions': 'Number of Transactions', 'count': 'Number of Customers'})
    else:
        fig = go.Figure()
        fig.add_annotation(text="No customer data available", x=0.5, y=0.5, showarrow=False)
    
    fig.update_layout(height=400)
    return fig

def create_correlation_heatmap(data):
    """Create correlation heatmap for numeric columns"""
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Calculate correlation matrix
    corr_matrix = data.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate='%{text}',
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title='Correlation Matrix',
        height=500,
        width=500
    )
    
    return fig

def create_forecast_chart(data, target_column, forecast_days=30):
    """Create simple forecast chart using linear trend"""
    if data.empty or 'date' not in data.columns or target_column not in data.columns:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data for forecasting", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Prepare data
    data['date'] = pd.to_datetime(data['date'])
    daily_data = data.groupby('date')[target_column].sum().reset_index()
    daily_data = daily_data.sort_values('date')
    
    # Fit simple linear trend
    x = np.arange(len(daily_data))
    y = daily_data[target_column].values
    
    if len(daily_data) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Need more data points for forecasting", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Calculate trend
    coeffs = np.polyfit(x, y, 1)
    trend_line = np.poly1d(coeffs)
    
    # Generate forecast
    future_x = np.arange(len(daily_data), len(daily_data) + forecast_days)
    last_date = daily_data['date'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days, freq='D')
    
    forecast_values = trend_line(future_x)
    
    # Create chart
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data[target_column],
        mode='lines+markers',
        name='Historical',
        line=dict(color='#28A745')
    ))
    
    # Trend line
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=trend_line(x),
        mode='lines',
        name='Trend',
        line=dict(color='#FFC107', dash='dash')
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=forecast_values,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#DC3545', dash='dot')
    ))
    
    fig.update_layout(
        title=f'{target_column} Forecast ({forecast_days} days)',
        xaxis_title='Date',
        yaxis_title=target_column,
        height=400,
        hovermode='x'
    )
    
    return fig

def create_kpi_gauge(value, title, max_value=None, target=None):
    """Create a KPI gauge chart"""
    if max_value is None:
        max_value = value * 1.5
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': target} if target else None,
        gauge = {
            'axis': {'range': [None, max_value]},
            'bar': {'color': "#28A745"},
            'steps': [
                {'range': [0, max_value*0.5], 'color': "lightgray"},
                {'range': [max_value*0.5, max_value*0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target if target else max_value*0.9
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_comparison_chart(data, x_col, y_col, group_col=None):
    """Create comparison chart (bar or grouped bar)"""
    if data.empty or x_col not in data.columns or y_col not in data.columns:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data for comparison", x=0.5, y=0.5, showarrow=False)
        return fig
    
    if group_col and group_col in data.columns:
        # Grouped bar chart
        fig = px.bar(data, x=x_col, y=y_col, color=group_col,
                    title=f'{y_col} by {x_col} (grouped by {group_col})')
    else:
        # Simple bar chart
        agg_data = data.groupby(x_col)[y_col].sum().reset_index()
        fig = px.bar(agg_data, x=x_col, y=y_col,
                    title=f'{y_col} by {x_col}')
    
    fig.update_layout(height=400)
    return fig

def create_time_series_decomposition(data, value_col):
    """Create time series decomposition chart"""
    if data.empty or 'date' not in data.columns or value_col not in data.columns:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data for time series analysis", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Prepare daily data
    daily_data = data.groupby('date')[value_col].sum().reset_index()
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    daily_data = daily_data.sort_values('date').set_index('date')
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=['Original', 'Trend (30-day MA)', 'Residual'],
        vertical_spacing=0.08
    )
    
    # Original data
    fig.add_trace(go.Scatter(
        x=daily_data.index,
        y=daily_data[value_col],
        mode='lines',
        name='Original',
        line=dict(color='#28A745')
    ), row=1, col=1)
    
    # Trend (30-day moving average)
    trend = daily_data[value_col].rolling(window=30, center=True).mean()
    fig.add_trace(go.Scatter(
        x=daily_data.index,
        y=trend,
        mode='lines',
        name='Trend',
        line=dict(color='#FFC107')
    ), row=2, col=1)
    
    # Residual
    residual = daily_data[value_col] - trend
    fig.add_trace(go.Scatter(
        x=daily_data.index,
        y=residual,
        mode='lines',
        name='Residual',
        line=dict(color='#DC3545')
    ), row=3, col=1)
    
    fig.update_layout(height=600, title_text="Time Series Decomposition")
    return fig
