import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from utils.database import get_database_connection

def show_finance_modules():
    """Display Finance category modules"""
    pass  # Data now comes from database
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Accounting", "Invoicing", "Expenses Tracking", "Spreadsheets (BI)", "Documents Management"
    ])
    
    with tab1:
        show_accounting_module()
    
    with tab2:
        show_invoicing_module()
    
    with tab3:
        show_expenses_module()
    
    with tab4:
        show_spreadsheets_module()
    
    with tab5:
        show_documents_module()

def show_accounting_module():
    """Chart of Accounts and Financial Statements"""
    st.markdown("#### 📊 Accounting Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Chart of Accounts")
        
        # Load accounts from database
        with get_database_connection() as db:
            accounts_df = db.get_table_data('chart_of_accounts')
        
        if not accounts_df.empty:
            # Display relevant columns
            display_df = accounts_df[['account_code', 'account_name', 'account_type', 'balance']].copy()
            display_df['balance'] = display_df['balance'].apply(lambda x: f"${float(x):,.2f}")
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No accounts found in database")
        
        # Add new account
        with st.expander("Add New Account"):
            with st.form("new_account"):
                account_name = st.text_input("Account Name")
                account_type = st.selectbox("Account Type", 
                    ["Assets", "Liabilities", "Equity", "Revenue", "Expenses"])
                account_code = st.text_input("Account Code")
                
                if st.form_submit_button("Add Account"):
                    # Insert into database
                    with get_database_connection() as db:
                        query = """
                        INSERT INTO chart_of_accounts (account_code, account_name, account_type, balance)
                        VALUES (%s, %s, %s, %s)
                        """
                        try:
                            db.execute_query(query, (account_code, account_name, account_type, 0.0))
                            st.success(f"Account '{account_name}' added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding account: {e}")
    
    with col2:
        st.subheader("Account Summary")
        
        # Calculate totals by type from database
        with get_database_connection() as db:
            accounts_df = db.get_table_data('chart_of_accounts')
        
        if not accounts_df.empty:
            summary = accounts_df.groupby('account_type')['balance'].sum().reset_index()
            
            for _, row in summary.iterrows():
                st.metric(row['account_type'], f"${float(row['balance']):,.2f}")
        else:
            st.info("No account data available")
        
        # Quick actions
        st.markdown("#### Quick Actions")
        if st.button("📝 Journal Entry", use_container_width=True):
            st.info("Journal Entry form would open here")
        
        if st.button("📋 Trial Balance", use_container_width=True):
            st.info("Trial Balance report would generate here")
        
        if st.button("📊 P&L Statement", use_container_width=True):
            st.info("Profit & Loss statement would generate here")

def show_invoicing_module():
    """Invoice Management System"""
    st.markdown("#### 💳 Invoice Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Recent Invoices")
        invoices_df = pd.DataFrame(st.session_state.finance_data['invoices'])
        st.dataframe(invoices_df, use_container_width=True)
        
        # Create new invoice
        with st.expander("Create New Invoice"):
            with st.form("new_invoice"):
                col_a, col_b = st.columns(2)
                with col_a:
                    customer_name = st.text_input("Customer Name")
                    invoice_date = st.date_input("Invoice Date", datetime.now())
                    due_date = st.date_input("Due Date", datetime.now() + timedelta(days=30))
                
                with col_b:
                    amount = st.number_input("Amount", min_value=0.0, value=0.0)
                    description = st.text_area("Description")
                
                if st.form_submit_button("Create Invoice"):
                    new_invoice = {
                        'invoice_id': f"INV-{len(st.session_state.finance_data['invoices']) + 1:04d}",
                        'customer': customer_name,
                        'amount': amount,
                        'date': invoice_date.strftime('%Y-%m-%d'),
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'status': 'Pending',
                        'description': description
                    }
                    st.session_state.finance_data['invoices'].append(new_invoice)
                    st.success(f"Invoice {new_invoice['invoice_id']} created!")
                    st.rerun()
    
    with col2:
        st.subheader("Invoice Statistics")
        
        invoices_df = pd.DataFrame(st.session_state.finance_data['invoices'])
        
        total_amount = invoices_df['amount'].sum()
        pending_amount = invoices_df[invoices_df['status'] == 'Pending']['amount'].sum()
        paid_amount = invoices_df[invoices_df['status'] == 'Paid']['amount'].sum()
        
        st.metric("Total Invoiced", f"${total_amount:,.2f}")
        st.metric("Pending", f"${pending_amount:,.2f}")
        st.metric("Collected", f"${paid_amount:,.2f}")
        
        # Status distribution chart
        status_counts = invoices_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Invoice Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_expenses_module():
    """Expense Tracking System"""
    st.markdown("#### 💸 Expense Tracking")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Recent Expenses")
        expenses_df = pd.DataFrame(st.session_state.finance_data['expenses'])
        st.dataframe(expenses_df, use_container_width=True)
        
        # Add new expense
        with st.expander("Add New Expense"):
            with st.form("new_expense"):
                col_a, col_b = st.columns(2)
                with col_a:
                    expense_category = st.selectbox("Category", 
                        ["Office Supplies", "Travel", "Marketing", "Utilities", "Equipment", "Other"])
                    amount = st.number_input("Amount", min_value=0.0, value=0.0)
                    date = st.date_input("Date", datetime.now())
                
                with col_b:
                    vendor = st.text_input("Vendor/Supplier")
                    description = st.text_area("Description")
                    receipt = st.file_uploader("Receipt", type=['pdf', 'jpg', 'png'])
                
                if st.form_submit_button("Add Expense"):
                    new_expense = {
                        'id': f"EXP-{len(st.session_state.finance_data['expenses']) + 1:04d}",
                        'category': expense_category,
                        'amount': amount,
                        'date': date.strftime('%Y-%m-%d'),
                        'vendor': vendor,
                        'description': description,
                        'status': 'Recorded'
                    }
                    st.session_state.finance_data['expenses'].append(new_expense)
                    st.success(f"Expense {new_expense['id']} recorded!")
                    st.rerun()
    
    with col2:
        st.subheader("Expense Analytics")
        
        expenses_df = pd.DataFrame(st.session_state.finance_data['expenses'])
        
        # Monthly expenses trend
        expenses_df['month'] = pd.to_datetime(expenses_df['date']).dt.to_period('M')
        monthly_expenses = expenses_df.groupby('month')['amount'].sum().reset_index()
        monthly_expenses['month'] = monthly_expenses['month'].astype(str)
        
        fig = px.line(monthly_expenses, x='month', y='amount', 
                     title="Monthly Expenses Trend")
        st.plotly_chart(fig, use_container_width=True)
        
        # Category breakdown
        category_expenses = expenses_df.groupby('category')['amount'].sum().reset_index()
        fig2 = px.bar(category_expenses, x='category', y='amount', 
                     title="Expenses by Category")
        st.plotly_chart(fig2, use_container_width=True)

def show_spreadsheets_module():
    """Business Intelligence Spreadsheets"""
    st.markdown("#### 📈 Financial Analytics & BI")
    
    # Financial dashboard with key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate financial metrics
    invoices_df = pd.DataFrame(st.session_state.finance_data['invoices'])
    expenses_df = pd.DataFrame(st.session_state.finance_data['expenses'])
    
    total_revenue = invoices_df[invoices_df['status'] == 'Paid']['amount'].sum()
    total_expenses = expenses_df['amount'].sum()
    profit = total_revenue - total_expenses
    
    with col1:
        st.metric("Revenue", f"${total_revenue:,.2f}", "↑ 12.5%")
    with col2:
        st.metric("Expenses", f"${total_expenses:,.2f}", "↑ 8.2%")
    with col3:
        st.metric("Profit", f"${profit:,.2f}", "↑ 15.8%")
    with col4:
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Profit Margin", f"{profit_margin:.1f}%", "↑ 2.1%")
    
    # Financial charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue vs Expenses comparison
        comparison_data = pd.DataFrame({
            'Category': ['Revenue', 'Expenses', 'Profit'],
            'Amount': [total_revenue, total_expenses, profit]
        })
        
        fig = px.bar(comparison_data, x='Category', y='Amount', 
                    title="Financial Overview", color='Category')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cash flow trend (simulated)
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        cash_flow = pd.DataFrame({
            'Date': dates,
            'Cash Flow': [15000 + i*1000 + (i%3)*2000 for i in range(len(dates))]
        })
        
        fig2 = px.line(cash_flow, x='Date', y='Cash Flow', 
                      title="Cash Flow Projection")
        st.plotly_chart(fig2, use_container_width=True)

def show_documents_module():
    """Document Management System"""
    st.markdown("#### 📄 Financial Documents Management")
    
    # Document categories
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Document Library")
        
        # Sample documents
        documents = [
            {"name": "Annual Financial Report 2024.pdf", "type": "Report", "size": "2.3 MB", "date": "2024-01-15"},
            {"name": "Tax Returns Q4 2023.pdf", "type": "Tax", "size": "1.1 MB", "date": "2024-01-10"},
            {"name": "Bank Statements Dec 2023.pdf", "type": "Bank", "size": "890 KB", "date": "2024-01-05"},
            {"name": "Expense Receipts Folder", "type": "Folder", "size": "-", "date": "2024-01-01"},
        ]
        
        for doc in documents:
            with st.container():
                col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                with col_a:
                    st.write(f"📁 {doc['name']}")
                with col_b:
                    st.write(doc['type'])
                with col_c:
                    st.write(doc['size'])
                with col_d:
                    st.write(doc['date'])
                st.markdown("---")
        
        # Upload new document
        with st.expander("Upload New Document"):
            uploaded_file = st.file_uploader("Choose file", type=['pdf', 'xlsx', 'docx', 'jpg', 'png'])
            document_type = st.selectbox("Document Type", 
                ["Invoice", "Receipt", "Bank Statement", "Tax Document", "Report", "Other"])
            description = st.text_area("Description (optional)")
            
            if st.button("Upload Document") and uploaded_file:
                st.success(f"Document '{uploaded_file.name}' uploaded successfully!")
    
    with col2:
        st.subheader("Quick Stats")
        st.metric("Total Documents", "47")
        st.metric("Storage Used", "156 MB")
        st.metric("This Month", "8 new")
        
        st.markdown("#### Document Types")
        doc_types = {"Invoices": 15, "Receipts": 12, "Reports": 8, "Bank Statements": 6, "Other": 6}
        for doc_type, count in doc_types.items():
            st.write(f"**{doc_type}:** {count}")

def generate_sample_accounts():
    """Generate sample chart of accounts"""
    return [
        {'code': '1000', 'name': 'Cash', 'type': 'Assets', 'balance': 25000.00},
        {'code': '1100', 'name': 'Accounts Receivable', 'type': 'Assets', 'balance': 15000.00},
        {'code': '1200', 'name': 'Inventory', 'type': 'Assets', 'balance': 30000.00},
        {'code': '2000', 'name': 'Accounts Payable', 'type': 'Liabilities', 'balance': 8000.00},
        {'code': '3000', 'name': 'Owner Equity', 'type': 'Equity', 'balance': 50000.00},
        {'code': '4000', 'name': 'Sales Revenue', 'type': 'Revenue', 'balance': 45000.00},
        {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'Expenses', 'balance': 18000.00},
        {'code': '5100', 'name': 'Office Expenses', 'type': 'Expenses', 'balance': 3200.00},
    ]

def generate_sample_invoices():
    """Generate sample invoices"""
    return [
        {'invoice_id': 'INV-0001', 'customer': 'ABC Corp', 'amount': 2500.00, 'date': '2024-01-15', 'due_date': '2024-02-15', 'status': 'Paid', 'description': 'Consulting services'},
        {'invoice_id': 'INV-0002', 'customer': 'XYZ Ltd', 'amount': 1800.00, 'date': '2024-01-20', 'due_date': '2024-02-20', 'status': 'Pending', 'description': 'Software development'},
        {'invoice_id': 'INV-0003', 'customer': 'Tech Solutions', 'amount': 3200.00, 'date': '2024-01-25', 'due_date': '2024-02-25', 'status': 'Paid', 'description': 'System integration'},
        {'invoice_id': 'INV-0004', 'customer': 'Global Inc', 'amount': 2100.00, 'date': '2024-01-28', 'due_date': '2024-02-28', 'status': 'Overdue', 'description': 'Project management'},
    ]

def generate_sample_expenses():
    """Generate sample expenses"""
    return [
        {'id': 'EXP-0001', 'category': 'Office Supplies', 'amount': 250.00, 'date': '2024-01-10', 'vendor': 'Office Depot', 'description': 'Stationery and supplies', 'status': 'Recorded'},
        {'id': 'EXP-0002', 'category': 'Travel', 'amount': 800.00, 'date': '2024-01-15', 'vendor': 'Airlines Inc', 'description': 'Business trip to Lagos', 'status': 'Recorded'},
        {'id': 'EXP-0003', 'category': 'Marketing', 'amount': 1200.00, 'date': '2024-01-18', 'vendor': 'Ad Agency', 'description': 'Social media campaign', 'status': 'Recorded'},
        {'id': 'EXP-0004', 'category': 'Utilities', 'amount': 450.00, 'date': '2024-01-20', 'vendor': 'Power Company', 'description': 'Monthly electricity bill', 'status': 'Recorded'},
    ]

def generate_sample_transactions():
    """Generate sample financial transactions"""
    return [
        {'date': '2024-01-15', 'description': 'Client payment received', 'debit': 2500.00, 'credit': 0, 'account': 'Cash'},
        {'date': '2024-01-15', 'description': 'Revenue recognition', 'debit': 0, 'credit': 2500.00, 'account': 'Sales Revenue'},
        {'date': '2024-01-18', 'description': 'Office supplies purchase', 'debit': 250.00, 'credit': 0, 'account': 'Office Expenses'},
        {'date': '2024-01-18', 'description': 'Cash payment', 'debit': 0, 'credit': 250.00, 'account': 'Cash'},
    ]