import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import check_authentication
from utils.database import initialize_database, get_database_connection

# Page configuration
st.set_page_config(
    page_title="DataLink - Business Management Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
if 'database_initialized' not in st.session_state:
    with st.spinner("Initializing database..."):
        if initialize_database():
            st.session_state.database_initialized = True
            st.success("Database initialized successfully!")
        else:
            st.error("Failed to initialize database")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'company_data' not in st.session_state:
    st.session_state.company_data = pd.DataFrame()

# Check authentication
if not check_authentication():
    st.stop()

# Business categories and their modules
BUSINESS_CATEGORIES = {
    "🏠 Dashboard": {
        "description": "Overview of your business operations",
        "modules": ["Business Overview", "Quick Stats", "Recent Activity"]
    },
    "📊 Data Analysis": {
        "description": "Analytics, reporting, and business intelligence",
        "modules": ["Dashboard Analytics", "Data Upload", "Advanced Analytics", "Reports", "Collaboration"]
    },
    "💰 Finance": {
        "description": "Financial management and accounting",
        "modules": ["Accounting", "Invoicing", "Expenses Tracking", "Spreadsheets (BI)", "Documents Management"]
    },
    "🛒 Sales": {
        "description": "Customer relationship and sales management",
        "modules": ["CRM Systems", "Sales Processes", "Lead Management", "Deal Tracking", "Customer Analytics"]
    },
    "📦 Logistics": {
        "description": "Inventory, manufacturing, and supply chain",
        "modules": ["Inventory Management", "Manufacturing", "PLM (Product Lifecycle)", "Purchase Orders", "Maintenance"]
    },
    "👥 Human Resources": {
        "description": "Employee management and HR operations",
        "modules": ["Employee Management", "Recruitment", "Referrals", "Fleet Management", "Time Off", "Appraisals"]
    },
    "🔧 Services": {
        "description": "Project management and service delivery",
        "modules": ["Project Management", "Timesheets", "Field Service", "Service Analytics"]
    },
    "⚡ Productivity": {
        "description": "Communication, collaboration, and knowledge management",
        "modules": ["Discuss", "Approvals", "Knowledge Base", "Team Collaboration", "Workflow Automation"]
    },
    "🗄️ Database Admin": {
        "description": "Database management and administration",
        "modules": ["View Tables", "Manage Data", "Backup & Restore", "Query Interface"]
    }
}

# Main application interface
st.title("🏢 DataLink Business Management Platform")
st.markdown(f"### Welcome back, {st.session_state.username}!")

# Sidebar navigation
with st.sidebar:
    st.markdown(f"**User:** {st.session_state.username}")
    st.markdown(f"**Role:** {st.session_state.user_role}")
    st.markdown("---")
    
    st.markdown("### Business Categories")
    
    # Category selection
    selected_category = st.selectbox(
        "Select a category:",
        options=list(BUSINESS_CATEGORIES.keys()),
        index=0 if st.session_state.selected_category is None else list(BUSINESS_CATEGORIES.keys()).index(st.session_state.selected_category) if st.session_state.selected_category in BUSINESS_CATEGORIES else 0
    )
    
    st.session_state.selected_category = selected_category
    
    st.markdown("---")
    
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.session_state.selected_category = None
        st.rerun()

# Main content area based on selected category
if selected_category == "🏠 Dashboard":
    st.subheader("Business Overview")
    
    # Get real metrics from database
    with get_database_connection() as db:
        metrics = db.get_business_metrics()
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Projects", str(metrics.get('active_projects', 0)), "↑ 3")
    with col2:
        st.metric("Total Revenue", f"${metrics.get('total_revenue', 0):,.2f}", "↑ 8.2%")
    with col3:
        st.metric("Active Employees", str(metrics.get('total_employees', 0)), "→ 0")
    with col4:
        if metrics.get('low_stock_items', 0) > 0:
            st.metric("Low Stock Items", str(metrics.get('low_stock_items', 0)), "⚠️ Alert")
        else:
            st.metric("Inventory Status", "Good", "✅ OK")
    
    st.markdown("---")
    
    # Quick access tiles
    st.subheader("Quick Access")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.selected_category = "📊 Data Analysis"
            st.rerun()
        
        if st.button("💰 Check Finances", use_container_width=True):
            st.session_state.selected_category = "💰 Finance"
            st.rerun()
    
    with col2:
        if st.button("🛒 Sales Dashboard", use_container_width=True):
            st.session_state.selected_category = "🛒 Sales"
            st.rerun()
        
        if st.button("📦 Inventory Status", use_container_width=True):
            st.session_state.selected_category = "📦 Logistics"
            st.rerun()
    
    with col3:
        if st.button("👥 HR Overview", use_container_width=True):
            st.session_state.selected_category = "👥 Human Resources"
            st.rerun()
        
        if st.button("🔧 Active Projects", use_container_width=True):
            st.session_state.selected_category = "🔧 Services"
            st.rerun()
    
    # Recent activity feed
    st.subheader("Recent Activity")
    activities = [
        {"time": "2 hours ago", "user": "John Doe", "action": "Updated project status", "category": "Services"},
        {"time": "4 hours ago", "user": "Jane Smith", "action": "Created new invoice", "category": "Finance"},
        {"time": "Yesterday", "user": "Mike Johnson", "action": "Added new customer", "category": "Sales"},
        {"time": "Yesterday", "user": "Sarah Wilson", "action": "Approved purchase order", "category": "Logistics"},
    ]
    
    for activity in activities:
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                st.write(f"**{activity['user']}**")
            with col2:
                st.write(activity['action'])
            with col3:
                st.write(activity['time'])
            st.markdown("---")

else:
    # Display selected category information
    category_info = BUSINESS_CATEGORIES[selected_category]
    st.subheader(selected_category)
    st.markdown(f"*{category_info['description']}*")
    
    # Show available modules
    st.markdown("### Available Modules")
    
    # Create tabs for modules
    if selected_category == "📊 Data Analysis":
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard Analytics", "Data Upload", "Advanced Analytics", "Reports", "Collaboration"])
        
        with tab1:
            # Import and display existing dashboard functionality
            from utils.data_processor import load_sample_data, get_kpi_metrics
            from utils.charts import create_sales_chart, create_revenue_chart, create_customer_chart
            
            if st.session_state.company_data.empty:
                st.session_state.company_data = load_sample_data()
            
            data = st.session_state.company_data
            
            if not data.empty:
                metrics = get_kpi_metrics(data)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Revenue", f"${metrics['total_revenue']:,.2f}", f"{metrics['revenue_growth']:.1f}%")
                with col2:
                    st.metric("Total Orders", f"{metrics['total_orders']:,}", f"{metrics['order_growth']:.1f}%")
                with col3:
                    st.metric("Active Customers", f"{metrics['active_customers']:,}", f"{metrics['customer_growth']:.1f}%")
                with col4:
                    st.metric("Avg Order Value", f"${metrics['avg_order_value']:.2f}", f"{metrics['aov_growth']:.1f}%")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(create_revenue_chart(data), use_container_width=True)
                with col2:
                    st.plotly_chart(create_sales_chart(data), use_container_width=True)
        
        with tab2:
            st.markdown("#### Data Upload and Management")
            st.info("Upload CSV or Excel files to analyze your business data")
            
            uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
            if uploaded_file:
                st.success("File upload functionality - integrate with existing data processor")
        
        with tab3:
            st.markdown("#### Advanced Analytics")
            st.info("Trend analysis, forecasting, and correlation studies")
            
            analysis_type = st.selectbox("Analysis Type", ["Trend Analysis", "Correlation", "Forecasting", "Custom Query"])
            st.write(f"Selected: {analysis_type}")
        
        with tab4:
            st.markdown("#### Reports and Exports")
            st.info("Generate and export business reports")
            
            report_type = st.selectbox("Report Type", ["Financial Summary", "Sales Report", "Customer Analytics", "Custom Report"])
            if st.button("Generate Report"):
                st.success(f"Generating {report_type}...")
        
        with tab5:
            st.markdown("#### Team Collaboration")
            st.info("Share insights and collaborate with team members")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Shared Views", "8")
                st.metric("Team Comments", "24")
            with col2:
                st.metric("Active Collaborators", "5")
                st.metric("Recent Insights", "12")
    
    elif selected_category == "💰 Finance":
        # Import and show Finance modules
        from modules.finance import show_finance_modules
        show_finance_modules()
    
    elif selected_category == "🛒 Sales":
        # Import and show Sales modules
        from modules.sales import show_sales_modules
        show_sales_modules()
    
    elif selected_category == "🗄️ Database Admin":
        # Import and show Database Admin modules
        from modules.database_admin import show_database_admin, show_database_backup
        
        admin_tab1, admin_tab2 = st.tabs(["Database Management", "Backup & Restore"])
        
        with admin_tab1:
            show_database_admin()
        
        with admin_tab2:
            show_database_backup()
    
    else:
        # For other categories, show module placeholders
        cols = st.columns(min(3, len(category_info['modules'])))
        
        for i, module in enumerate(category_info['modules']):
            with cols[i % 3]:
                if st.button(f"📋 {module}", use_container_width=True):
                    st.info(f"Opening {module} module...")
                    st.markdown(f"**{module}** module is ready for implementation.")
                    
                    # Add specific content based on category and module
                    if selected_category == "📦 Logistics":
                        if module == "Inventory Management":
                            st.markdown("#### Inventory Management System")
                            
                            # Sample inventory data
                            inventory_data = [
                                {"Product": "Laptop Dell XPS", "SKU": "LAP-001", "Stock": 25, "Reorder Point": 10, "Unit Cost": "$800", "Total Value": "$20,000"},
                                {"Product": "Office Chair", "SKU": "CHR-002", "Stock": 8, "Reorder Point": 15, "Unit Cost": "$150", "Total Value": "$1,200"},
                                {"Product": "Printer HP LaserJet", "SKU": "PRT-003", "Stock": 45, "Reorder Point": 20, "Unit Cost": "$300", "Total Value": "$13,500"},
                            ]
                            
                            st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Total Items", "78")
                            with col_b:
                                st.metric("Low Stock Alerts", "3")
                            with col_c:
                                st.metric("Total Inventory Value", "$34,700")
                                
                        elif module == "Manufacturing":
                            st.markdown("#### Manufacturing Operations")
                            st.markdown("- Production Planning & Scheduling")
                            st.markdown("- Work Orders & Job Tracking")
                            st.markdown("- Quality Control & Inspections")
                            st.markdown("- Equipment Maintenance")
                            
                            # Production metrics
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Active Work Orders", "12")
                            with col_b:
                                st.metric("Production Efficiency", "94.2%")
                            with col_c:
                                st.metric("Quality Score", "98.1%")
                                
                        elif module == "PLM (Product Lifecycle)":
                            st.markdown("#### Product Lifecycle Management")
                            st.markdown("- Product Development Pipeline")
                            st.markdown("- Design & Engineering Documentation")
                            st.markdown("- Version Control & Change Management")
                            st.markdown("- Compliance & Regulatory Tracking")
                    
                    elif selected_category == "👥 Human Resources":
                        if module == "Employee Management":
                            st.markdown("#### Employee Management System")
                            
                            # Sample employee data
                            employee_data = [
                                {"Name": "John Smith", "ID": "EMP-001", "Department": "Engineering", "Position": "Senior Developer", "Status": "Active", "Start Date": "2023-01-15"},
                                {"Name": "Sarah Johnson", "ID": "EMP-002", "Department": "Sales", "Position": "Sales Manager", "Status": "Active", "Start Date": "2023-03-01"},
                                {"Name": "Mike Davis", "ID": "EMP-003", "Department": "Marketing", "Position": "Marketing Specialist", "Status": "Active", "Start Date": "2023-06-10"},
                            ]
                            
                            st.dataframe(pd.DataFrame(employee_data), use_container_width=True)
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Total Employees", "28")
                            with col_b:
                                st.metric("New Hires (30d)", "2")
                            with col_c:
                                st.metric("Turnover Rate", "3.2%")
                                
                        elif module == "Recruitment":
                            st.markdown("#### Recruitment & Hiring")
                            st.markdown("- Job Posting Management")
                            st.markdown("- Candidate Application Tracking")
                            st.markdown("- Interview Scheduling & Feedback")
                            st.markdown("- Offer Management & Onboarding")
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Open Positions", "5")
                            with col_b:
                                st.metric("Active Candidates", "23")
                            with col_c:
                                st.metric("Interviews Scheduled", "8")
                    
                    elif selected_category == "🔧 Services":
                        if module == "Project Management":
                            st.markdown("#### Project Management Hub")
                            
                            # Sample project data
                            project_data = [
                                {"Project": "Website Redesign", "Status": "In Progress", "Progress": "75%", "Due Date": "2024-02-15", "Team Size": "4", "Budget": "$15,000"},
                                {"Project": "Mobile App Development", "Status": "Planning", "Progress": "25%", "Due Date": "2024-04-30", "Team Size": "6", "Budget": "$50,000"},
                                {"Project": "Database Migration", "Status": "Completed", "Progress": "100%", "Due Date": "2024-01-20", "Team Size": "3", "Budget": "$8,000"},
                            ]
                            
                            st.dataframe(pd.DataFrame(project_data), use_container_width=True)
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Active Projects", "8")
                            with col_b:
                                st.metric("On-Time Delivery", "92%")
                            with col_c:
                                st.metric("Team Utilization", "87%")
                    
                    elif selected_category == "⚡ Productivity":
                        if module == "Discuss":
                            st.markdown("#### Team Communication Hub")
                            st.markdown("- Team Chat & Messaging")
                            st.markdown("- Discussion Channels by Department")
                            st.markdown("- File Sharing & Collaboration")
                            st.markdown("- Announcement Broadcasting")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Active Channels", "12")
                                st.metric("Messages Today", "156")
                            with col_b:
                                st.metric("Online Users", "18")
                                st.metric("Files Shared", "23")
                        
                        elif module == "Knowledge Base":
                            st.markdown("#### Knowledge Management System")
                            st.markdown("- Company Policies & Procedures")
                            st.markdown("- Technical Documentation")
                            st.markdown("- FAQ & Troubleshooting Guides")
                            st.markdown("- Training Materials & Resources")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Articles", "89")
                                st.metric("Views This Month", "342")
                            with col_b:
                                st.metric("Contributors", "15")
                                st.metric("Updates This Week", "7")

# Footer
st.markdown("---")
st.markdown("*DataLink Business Management Platform - Complete business solution for African SMEs*")
