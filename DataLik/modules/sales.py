import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.database import get_database_connection

def show_sales_modules():
    """Display Sales category modules"""
    
    # Initialize sales data in session state
    if 'sales_data' not in st.session_state:
        st.session_state.sales_data = {
            'customers': generate_sample_customers(),
            'leads': generate_sample_leads(),
            'deals': generate_sample_deals(),
            'contacts': generate_sample_contacts(),
            'sales_activities': generate_sample_activities()
        }
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "CRM Systems", "Sales Processes", "Lead Management", "Deal Tracking", "Customer Analytics"
    ])
    
    with tab1:
        show_crm_module()
    
    with tab2:
        show_sales_processes_module()
    
    with tab3:
        show_lead_management_module()
    
    with tab4:
        show_deal_tracking_module()
    
    with tab5:
        show_customer_analytics_module()

def show_crm_module():
    """Customer Relationship Management System"""
    st.markdown("#### 👥 Customer Relationship Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Customer Database")
        customers_df = pd.DataFrame(st.session_state.sales_data['customers'])
        
        # Search and filter
        search_term = st.text_input("🔍 Search customers")
        if search_term:
            customers_df = customers_df[customers_df['name'].str.contains(search_term, case=False, na=False)]
        
        st.dataframe(customers_df, use_container_width=True)
        
        # Add new customer
        with st.expander("Add New Customer"):
            with st.form("new_customer"):
                col_a, col_b = st.columns(2)
                with col_a:
                    customer_name = st.text_input("Customer Name")
                    email = st.text_input("Email")
                    phone = st.text_input("Phone")
                    company = st.text_input("Company")
                
                with col_b:
                    industry = st.selectbox("Industry", 
                        ["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing", "Other"])
                    status = st.selectbox("Status", ["Active", "Prospect", "Inactive"])
                    source = st.selectbox("Source", ["Website", "Referral", "Cold Call", "Social Media", "Event"])
                    notes = st.text_area("Notes")
                
                if st.form_submit_button("Add Customer"):
                    new_customer = {
                        'id': f"CUST-{len(st.session_state.sales_data['customers']) + 1:04d}",
                        'name': customer_name,
                        'email': email,
                        'phone': phone,
                        'company': company,
                        'industry': industry,
                        'status': status,
                        'source': source,
                        'created_date': datetime.now().strftime('%Y-%m-%d'),
                        'last_contact': '-',
                        'total_value': 0.0,
                        'notes': notes
                    }
                    st.session_state.sales_data['customers'].append(new_customer)
                    st.success(f"Customer '{customer_name}' added successfully!")
                    st.rerun()
    
    with col2:
        st.subheader("CRM Statistics")
        
        customers_df = pd.DataFrame(st.session_state.sales_data['customers'])
        
        # Key metrics
        total_customers = len(customers_df)
        active_customers = len(customers_df[customers_df['status'] == 'Active'])
        prospects = len(customers_df[customers_df['status'] == 'Prospect'])
        
        st.metric("Total Customers", total_customers)
        st.metric("Active Customers", active_customers)
        st.metric("Prospects", prospects)
        
        # Customer distribution by industry
        if not customers_df.empty:
            industry_counts = customers_df['industry'].value_counts()
            fig = px.pie(values=industry_counts.values, names=industry_counts.index, 
                        title="Customers by Industry")
            st.plotly_chart(fig, use_container_width=True)
        
        # Customer acquisition sources
        if not customers_df.empty:
            source_counts = customers_df['source'].value_counts()
            fig2 = px.bar(x=source_counts.values, y=source_counts.index, 
                         orientation='h', title="Customer Sources")
            st.plotly_chart(fig2, use_container_width=True)

def show_sales_processes_module():
    """Sales Pipeline and Process Management"""
    st.markdown("#### 🔄 Sales Process Management")
    
    # Sales pipeline stages
    pipeline_stages = ["Lead", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Sales Pipeline")
        
        # Pipeline visualization
        deals_df = pd.DataFrame(st.session_state.sales_data['deals'])
        stage_counts = deals_df['stage'].value_counts().reindex(pipeline_stages, fill_value=0)
        stage_values = deals_df.groupby('stage')['value'].sum().reindex(pipeline_stages, fill_value=0)
        
        # Create pipeline funnel
        pipeline_data = pd.DataFrame({
            'Stage': pipeline_stages,
            'Count': stage_counts.values,
            'Value': stage_values.values
        })
        
        fig = px.funnel(pipeline_data, x='Count', y='Stage', title="Sales Pipeline")
        st.plotly_chart(fig, use_container_width=True)
        
        # Pipeline table
        st.subheader("Pipeline Details")
        st.dataframe(deals_df, use_container_width=True)
    
    with col2:
        st.subheader("Pipeline Metrics")
        
        total_pipeline_value = deals_df['value'].sum()
        active_deals = len(deals_df[~deals_df['stage'].isin(['Closed Won', 'Closed Lost'])])
        won_deals = len(deals_df[deals_df['stage'] == 'Closed Won'])
        
        st.metric("Pipeline Value", f"${total_pipeline_value:,.2f}")
        st.metric("Active Deals", active_deals)
        st.metric("Won Deals", won_deals)
        
        # Win rate calculation
        total_closed = len(deals_df[deals_df['stage'].isin(['Closed Won', 'Closed Lost'])])
        win_rate = (won_deals / total_closed * 100) if total_closed > 0 else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")
        
        # Sales activities
        st.markdown("#### Recent Activities")
        activities = st.session_state.sales_data['sales_activities']
        for activity in activities[-5:]:  # Show last 5 activities
            st.write(f"🔸 {activity['type']}: {activity['description']}")
            st.caption(f"{activity['date']} - {activity['rep']}")

def show_lead_management_module():
    """Lead Generation and Management"""
    st.markdown("#### 🎯 Lead Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Lead Database")
        leads_df = pd.DataFrame(st.session_state.sales_data['leads'])
        
        # Lead status filter
        status_filter = st.selectbox("Filter by Status", 
            ["All", "New", "Contacted", "Qualified", "Unqualified", "Converted"])
        
        if status_filter != "All":
            filtered_leads = leads_df[leads_df['status'] == status_filter]
        else:
            filtered_leads = leads_df
        
        st.dataframe(filtered_leads, use_container_width=True)
        
        # Add new lead
        with st.expander("Add New Lead"):
            with st.form("new_lead"):
                col_a, col_b = st.columns(2)
                with col_a:
                    lead_name = st.text_input("Lead Name")
                    lead_email = st.text_input("Email")
                    lead_phone = st.text_input("Phone")
                    lead_company = st.text_input("Company")
                
                with col_b:
                    lead_source = st.selectbox("Lead Source", 
                        ["Website Form", "Social Media", "Email Campaign", "Cold Call", "Referral", "Event"])
                    lead_score = st.slider("Lead Score", 0, 100, 50)
                    interest_level = st.selectbox("Interest Level", ["High", "Medium", "Low"])
                    lead_notes = st.text_area("Notes")
                
                if st.form_submit_button("Add Lead"):
                    new_lead = {
                        'id': f"LEAD-{len(st.session_state.sales_data['leads']) + 1:04d}",
                        'name': lead_name,
                        'email': lead_email,
                        'phone': lead_phone,
                        'company': lead_company,
                        'source': lead_source,
                        'score': lead_score,
                        'interest': interest_level,
                        'status': 'New',
                        'created_date': datetime.now().strftime('%Y-%m-%d'),
                        'last_contact': '-',
                        'notes': lead_notes
                    }
                    st.session_state.sales_data['leads'].append(new_lead)
                    st.success(f"Lead '{lead_name}' added successfully!")
                    st.rerun()
    
    with col2:
        st.subheader("Lead Analytics")
        
        leads_df = pd.DataFrame(st.session_state.sales_data['leads'])
        
        # Lead metrics
        total_leads = len(leads_df)
        new_leads = len(leads_df[leads_df['status'] == 'New'])
        qualified_leads = len(leads_df[leads_df['status'] == 'Qualified'])
        
        st.metric("Total Leads", total_leads)
        st.metric("New Leads", new_leads)
        st.metric("Qualified", qualified_leads)
        
        # Conversion rate
        converted_leads = len(leads_df[leads_df['status'] == 'Converted'])
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        
        # Lead sources
        if not leads_df.empty:
            source_counts = leads_df['source'].value_counts()
            fig = px.bar(x=source_counts.values, y=source_counts.index, 
                        orientation='h', title="Lead Sources")
            st.plotly_chart(fig, use_container_width=True)
        
        # Lead score distribution
        if not leads_df.empty:
            fig2 = px.histogram(leads_df, x='score', title="Lead Score Distribution")
            st.plotly_chart(fig2, use_container_width=True)

def show_deal_tracking_module():
    """Deal and Opportunity Tracking"""
    st.markdown("#### 💼 Deal Tracking")
    
    deals_df = pd.DataFrame(st.session_state.sales_data['deals'])
    
    # Deal summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_deals = len(deals_df)
        st.metric("Total Deals", total_deals)
    
    with col2:
        pipeline_value = deals_df[~deals_df['stage'].isin(['Closed Won', 'Closed Lost'])]['value'].sum()
        st.metric("Pipeline Value", f"${pipeline_value:,.2f}")
    
    with col3:
        won_value = deals_df[deals_df['stage'] == 'Closed Won']['value'].sum()
        st.metric("Won Value", f"${won_value:,.2f}")
    
    with col4:
        avg_deal_size = deals_df['value'].mean()
        st.metric("Avg Deal Size", f"${avg_deal_size:,.2f}")
    
    # Deal management interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Active Deals")
        
        # Filter deals
        stage_filter = st.selectbox("Filter by Stage", 
            ["All", "Lead", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"])
        
        if stage_filter != "All":
            filtered_deals = deals_df[deals_df['stage'] == stage_filter]
        else:
            filtered_deals = deals_df
        
        st.dataframe(filtered_deals, use_container_width=True)
        
        # Update deal status
        with st.expander("Update Deal"):
            if not deals_df.empty:
                deal_to_update = st.selectbox("Select Deal", deals_df['name'].tolist())
                new_stage = st.selectbox("New Stage", 
                    ["Lead", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"])
                update_notes = st.text_area("Update Notes")
                
                if st.button("Update Deal"):
                    # Update the deal in session state
                    for i, deal in enumerate(st.session_state.sales_data['deals']):
                        if deal['name'] == deal_to_update:
                            st.session_state.sales_data['deals'][i]['stage'] = new_stage
                            st.session_state.sales_data['deals'][i]['last_update'] = datetime.now().strftime('%Y-%m-%d')
                            break
                    
                    # Add activity record
                    activity = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'type': 'Deal Update',
                        'description': f"Updated {deal_to_update} to {new_stage}",
                        'rep': st.session_state.username,
                        'notes': update_notes
                    }
                    st.session_state.sales_data['sales_activities'].append(activity)
                    
                    st.success(f"Deal '{deal_to_update}' updated to {new_stage}")
                    st.rerun()
    
    with col2:
        st.subheader("Deal Analytics")
        
        # Deal stage distribution
        stage_counts = deals_df['stage'].value_counts()
        fig = px.pie(values=stage_counts.values, names=stage_counts.index, 
                    title="Deals by Stage")
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly deal closure trend
        deals_df['month'] = pd.to_datetime(deals_df['close_date']).dt.to_period('M')
        monthly_closures = deals_df[deals_df['stage'] == 'Closed Won'].groupby('month').size().reset_index(name='count')
        monthly_closures['month'] = monthly_closures['month'].astype(str)
        
        if not monthly_closures.empty:
            fig2 = px.line(monthly_closures, x='month', y='count', 
                          title="Monthly Deal Closures")
            st.plotly_chart(fig2, use_container_width=True)

def show_customer_analytics_module():
    """Customer Analytics and Insights"""
    st.markdown("#### 📊 Customer Analytics")
    
    customers_df = pd.DataFrame(st.session_state.sales_data['customers'])
    deals_df = pd.DataFrame(st.session_state.sales_data['deals'])
    
    # Customer analytics dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        customer_lifetime_value = customers_df['total_value'].mean()
        st.metric("Avg Customer LTV", f"${customer_lifetime_value:,.2f}")
    
    with col2:
        retention_rate = len(customers_df[customers_df['status'] == 'Active']) / len(customers_df) * 100
        st.metric("Customer Retention", f"{retention_rate:.1f}%")
    
    with col3:
        new_customers = len(customers_df[customers_df['created_date'] >= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')])
        st.metric("New Customers (30d)", new_customers)
    
    with col4:
        churn_rate = len(customers_df[customers_df['status'] == 'Inactive']) / len(customers_df) * 100
        st.metric("Churn Rate", f"{churn_rate:.1f}%")
    
    # Analytics charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer value distribution
        if not customers_df.empty and customers_df['total_value'].sum() > 0:
            fig = px.histogram(customers_df, x='total_value', title="Customer Value Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No customer value data available")
        
        # Customer acquisition trend
        customers_df['month'] = pd.to_datetime(customers_df['created_date']).dt.to_period('M')
        monthly_customers = customers_df.groupby('month').size().reset_index(name='count')
        monthly_customers['month'] = monthly_customers['month'].astype(str)
        
        if not monthly_customers.empty:
            fig2 = px.line(monthly_customers, x='month', y='count', 
                          title="Customer Acquisition Trend")
            st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Customer segmentation
        if not customers_df.empty:
            # Segment by total value
            customers_df['segment'] = pd.cut(customers_df['total_value'], 
                                           bins=[0, 1000, 5000, float('inf')], 
                                           labels=['Bronze', 'Silver', 'Gold'])
            segment_counts = customers_df['segment'].value_counts()
            
            fig3 = px.pie(values=segment_counts.values, names=segment_counts.index, 
                         title="Customer Segments")
            st.plotly_chart(fig3, use_container_width=True)
        
        # Industry analysis
        if not customers_df.empty:
            industry_value = customers_df.groupby('industry')['total_value'].sum().reset_index()
            fig4 = px.bar(industry_value, x='industry', y='total_value', 
                         title="Revenue by Industry")
            st.plotly_chart(fig4, use_container_width=True)

def generate_sample_customers():
    """Generate sample customer data"""
    return [
        {'id': 'CUST-0001', 'name': 'John Smith', 'email': 'john@techcorp.com', 'phone': '+234-801-123-4567', 'company': 'TechCorp Ltd', 'industry': 'Technology', 'status': 'Active', 'source': 'Website', 'created_date': '2024-01-15', 'last_contact': '2024-01-28', 'total_value': 15000.00, 'notes': 'Key decision maker'},
        {'id': 'CUST-0002', 'name': 'Sarah Johnson', 'email': 'sarah@financeplus.com', 'phone': '+234-802-234-5678', 'company': 'FinancePlus', 'industry': 'Finance', 'status': 'Active', 'source': 'Referral', 'created_date': '2024-01-10', 'last_contact': '2024-01-25', 'total_value': 22000.00, 'notes': 'Long-term partnership potential'},
        {'id': 'CUST-0003', 'name': 'Mike Davis', 'email': 'mike@healthsolutions.com', 'phone': '+234-803-345-6789', 'company': 'Health Solutions', 'industry': 'Healthcare', 'status': 'Prospect', 'source': 'Cold Call', 'created_date': '2024-01-20', 'last_contact': '2024-01-22', 'total_value': 0.00, 'notes': 'Interested in Q2 implementation'},
        {'id': 'CUST-0004', 'name': 'Lisa Brown', 'email': 'lisa@edutech.com', 'phone': '+234-804-456-7890', 'company': 'EduTech Africa', 'industry': 'Education', 'status': 'Active', 'source': 'Event', 'created_date': '2024-01-05', 'last_contact': '2024-01-30', 'total_value': 8500.00, 'notes': 'Requires custom training module'},
    ]

def generate_sample_leads():
    """Generate sample lead data"""
    return [
        {'id': 'LEAD-0001', 'name': 'David Wilson', 'email': 'david@startup.com', 'phone': '+234-805-567-8901', 'company': 'StartupCo', 'source': 'Website Form', 'score': 85, 'interest': 'High', 'status': 'Qualified', 'created_date': '2024-01-25', 'last_contact': '2024-01-26', 'notes': 'Ready for demo'},
        {'id': 'LEAD-0002', 'name': 'Emma Taylor', 'email': 'emma@retailchain.com', 'phone': '+234-806-678-9012', 'company': 'Retail Chain Ltd', 'source': 'Social Media', 'score': 70, 'interest': 'Medium', 'status': 'Contacted', 'created_date': '2024-01-28', 'last_contact': '2024-01-29', 'notes': 'Exploring options'},
        {'id': 'LEAD-0003', 'name': 'James Miller', 'email': 'james@manufacturing.com', 'phone': '+234-807-789-0123', 'company': 'Manufacturing Inc', 'source': 'Email Campaign', 'score': 45, 'interest': 'Low', 'status': 'New', 'created_date': '2024-01-30', 'last_contact': '-', 'notes': 'Budget concerns mentioned'},
    ]

def generate_sample_deals():
    """Generate sample deal data"""
    return [
        {'name': 'TechCorp Implementation', 'customer': 'TechCorp Ltd', 'value': 25000.00, 'stage': 'Proposal', 'probability': 75, 'close_date': '2024-02-15', 'created_date': '2024-01-10', 'last_update': '2024-01-28', 'rep': 'Sales Rep 1'},
        {'name': 'FinancePlus Integration', 'customer': 'FinancePlus', 'value': 35000.00, 'stage': 'Negotiation', 'probability': 80, 'close_date': '2024-02-20', 'created_date': '2024-01-05', 'last_update': '2024-01-30', 'rep': 'Sales Rep 2'},
        {'name': 'Health Solutions Platform', 'customer': 'Health Solutions', 'value': 18000.00, 'stage': 'Qualified', 'probability': 60, 'close_date': '2024-03-01', 'created_date': '2024-01-20', 'last_update': '2024-01-25', 'rep': 'Sales Rep 1'},
        {'name': 'EduTech Training Module', 'customer': 'EduTech Africa', 'value': 12000.00, 'stage': 'Closed Won', 'probability': 100, 'close_date': '2024-01-25', 'created_date': '2024-01-01', 'last_update': '2024-01-25', 'rep': 'Sales Rep 3'},
    ]

def generate_sample_contacts():
    """Generate sample contact data"""
    return [
        {'name': 'John Smith', 'title': 'CTO', 'company': 'TechCorp Ltd', 'email': 'john@techcorp.com', 'phone': '+234-801-123-4567', 'last_contact': '2024-01-28'},
        {'name': 'Sarah Johnson', 'title': 'CFO', 'company': 'FinancePlus', 'email': 'sarah@financeplus.com', 'phone': '+234-802-234-5678', 'last_contact': '2024-01-25'},
        {'name': 'Mike Davis', 'title': 'Operations Manager', 'company': 'Health Solutions', 'email': 'mike@healthsolutions.com', 'phone': '+234-803-345-6789', 'last_contact': '2024-01-22'},
    ]

def generate_sample_activities():
    """Generate sample sales activities"""
    return [
        {'date': '2024-01-30', 'type': 'Call', 'description': 'Follow-up call with TechCorp', 'rep': 'Sales Rep 1', 'notes': 'Discussed implementation timeline'},
        {'date': '2024-01-29', 'type': 'Email', 'description': 'Sent proposal to FinancePlus', 'rep': 'Sales Rep 2', 'notes': 'Waiting for feedback'},
        {'date': '2024-01-28', 'type': 'Meeting', 'description': 'Demo session with Health Solutions', 'rep': 'Sales Rep 1', 'notes': 'Very positive response'},
        {'date': '2024-01-25', 'type': 'Deal Closed', 'description': 'EduTech contract signed', 'rep': 'Sales Rep 3', 'notes': 'Implementation starts Feb 1'},
        {'date': '2024-01-24', 'type': 'Call', 'description': 'Qualification call with new lead', 'rep': 'Sales Rep 2', 'notes': 'High potential opportunity'},
    ]