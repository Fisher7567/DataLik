import streamlit as st
import pandas as pd
from utils.database import get_database_connection
from datetime import datetime

def show_database_admin():
    """Database administration interface"""
    
    st.markdown("#### 🗄️ Database Administration")
    
    # Database overview
    st.subheader("Database Overview")
    
    with get_database_connection() as db:
        # Get table information
        tables_query = """
        SELECT table_name, 
               (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        try:
            result = db.session.execute(db.engine.text(tables_query))
            tables_info = result.fetchall()
            
            # Display table summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tables", len(tables_info))
            with col2:
                # Get total records across all tables
                total_records = 0
                for table_name, _ in tables_info:
                    try:
                        count_result = db.session.execute(db.engine.text(f"SELECT COUNT(*) FROM {table_name}"))
                        total_records += count_result.scalar()
                    except:
                        pass
                st.metric("Total Records", total_records)
            with col3:
                st.metric("Database Status", "✅ Connected")
            
            st.markdown("---")
            
            # Table management interface
            st.subheader("Table Management")
            
            # Table selector
            table_names = [table[0] for table in tables_info]
            selected_table = st.selectbox("Select table to view/manage:", table_names)
            
            if selected_table:
                # Table details tabs
                tab1, tab2, tab3, tab4 = st.tabs(["View Data", "Table Info", "Add Record", "Custom Query"])
                
                with tab1:
                    # Display table data
                    st.markdown(f"#### Data from `{selected_table}`")
                    
                    # Pagination controls
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        page_size = st.selectbox("Records per page:", [10, 25, 50, 100], index=1)
                    with col2:
                        # Get total count
                        count_result = db.session.execute(db.engine.text(f"SELECT COUNT(*) FROM {selected_table}"))
                        total_count = count_result.scalar()
                        total_pages = (total_count + page_size - 1) // page_size
                        page_num = st.number_input("Page:", min_value=1, max_value=max(1, total_pages), value=1)
                    with col3:
                        st.write(f"Total records: {total_count}")
                    
                    # Load and display data
                    offset = (page_num - 1) * page_size
                    data_df = db.get_table_data(selected_table, limit=f"{page_size} OFFSET {offset}")
                    
                    if not data_df.empty:
                        st.dataframe(data_df, use_container_width=True)
                        
                        # Export options
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📥 Export to CSV"):
                                csv = data_df.to_csv(index=False)
                                st.download_button(
                                    label="Download CSV",
                                    data=csv,
                                    file_name=f"{selected_table}_export.csv",
                                    mime="text/csv"
                                )
                        with col2:
                            if st.button("🔄 Refresh Data"):
                                st.rerun()
                    else:
                        st.info(f"No data found in {selected_table}")
                
                with tab2:
                    # Table structure information
                    st.markdown(f"#### Structure of `{selected_table}`")
                    
                    # Get column information
                    columns_query = f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{selected_table}'
                    ORDER BY ordinal_position;
                    """
                    
                    columns_result = db.session.execute(db.engine.text(columns_query))
                    columns_data = columns_result.fetchall()
                    
                    if columns_data:
                        columns_df = pd.DataFrame(columns_data, columns=['Column', 'Type', 'Nullable', 'Default'])
                        st.dataframe(columns_df, use_container_width=True)
                    
                    # Table statistics
                    st.markdown("#### Table Statistics")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Columns", len(columns_data))
                    with col2:
                        st.metric("Total Rows", total_count)
                
                with tab3:
                    # Add new record form
                    st.markdown(f"#### Add New Record to `{selected_table}`")
                    
                    # Dynamic form based on table structure
                    if selected_table == "customers":
                        with st.form("add_customer"):
                            col1, col2 = st.columns(2)
                            with col1:
                                customer_id = st.text_input("Customer ID")
                                name = st.text_input("Name")
                                email = st.text_input("Email")
                                phone = st.text_input("Phone")
                            with col2:
                                company = st.text_input("Company")
                                industry = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing", "Other"])
                                status = st.selectbox("Status", ["Active", "Prospect", "Inactive"])
                                source = st.selectbox("Source", ["Website", "Referral", "Cold Call", "Social Media", "Event"])
                            
                            notes = st.text_area("Notes")
                            
                            if st.form_submit_button("Add Customer"):
                                insert_query = """
                                INSERT INTO customers (customer_id, name, email, phone, company, industry, status, source, notes)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                                try:
                                    db.execute_query(insert_query, (customer_id, name, email, phone, company, industry, status, source, notes))
                                    st.success("Customer added successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error adding customer: {e}")
                    
                    elif selected_table == "inventory":
                        with st.form("add_inventory"):
                            col1, col2 = st.columns(2)
                            with col1:
                                sku = st.text_input("SKU")
                                product_name = st.text_input("Product Name")
                                category = st.text_input("Category")
                                current_stock = st.number_input("Current Stock", min_value=0, value=0)
                            with col2:
                                reorder_point = st.number_input("Reorder Point", min_value=0, value=10)
                                unit_cost = st.number_input("Unit Cost", min_value=0.0, value=0.0, format="%.2f")
                                unit_price = st.number_input("Unit Price", min_value=0.0, value=0.0, format="%.2f")
                                supplier = st.text_input("Supplier")
                            
                            location = st.text_input("Location")
                            
                            if st.form_submit_button("Add Inventory Item"):
                                insert_query = """
                                INSERT INTO inventory (sku, product_name, category, current_stock, reorder_point, unit_cost, unit_price, supplier, location)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                                try:
                                    db.execute_query(insert_query, (sku, product_name, category, current_stock, reorder_point, unit_cost, unit_price, supplier, location))
                                    st.success("Inventory item added successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error adding inventory item: {e}")
                    
                    elif selected_table == "employees":
                        with st.form("add_employee"):
                            col1, col2 = st.columns(2)
                            with col1:
                                employee_id = st.text_input("Employee ID")
                                first_name = st.text_input("First Name")
                                last_name = st.text_input("Last Name")
                                email = st.text_input("Email")
                            with col2:
                                phone = st.text_input("Phone")
                                department = st.text_input("Department")
                                position = st.text_input("Position")
                                salary = st.number_input("Salary", min_value=0.0, value=50000.0, format="%.2f")
                            
                            hire_date = st.date_input("Hire Date", datetime.now())
                            
                            if st.form_submit_button("Add Employee"):
                                insert_query = """
                                INSERT INTO employees (employee_id, first_name, last_name, email, phone, department, position, hire_date, salary)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                                try:
                                    db.execute_query(insert_query, (employee_id, first_name, last_name, email, phone, department, position, hire_date, salary))
                                    st.success("Employee added successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error adding employee: {e}")
                    
                    else:
                        st.info(f"Custom form for {selected_table} not implemented. Use the Custom Query tab to insert data.")
                
                with tab4:
                    # Custom SQL query interface
                    st.markdown("#### Custom SQL Query")
                    st.warning("⚠️ Be careful with SQL queries. Always test with SELECT statements first.")
                    
                    query_type = st.selectbox("Query Type:", ["SELECT (Read)", "INSERT (Create)", "UPDATE (Modify)", "DELETE (Remove)"])
                    
                    # Sample queries
                    sample_queries = {
                        "SELECT (Read)": f"SELECT * FROM {selected_table} LIMIT 10;",
                        "INSERT (Create)": f"-- INSERT INTO {selected_table} (column1, column2) VALUES ('value1', 'value2');",
                        "UPDATE (Modify)": f"-- UPDATE {selected_table} SET column1 = 'new_value' WHERE id = 1;",
                        "DELETE (Remove)": f"-- DELETE FROM {selected_table} WHERE id = 1;"
                    }
                    
                    custom_query = st.text_area("SQL Query:", value=sample_queries[query_type], height=100)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔍 Execute Query"):
                            if custom_query.strip():
                                try:
                                    result = db.execute_query(custom_query)
                                    
                                    if query_type == "SELECT (Read)":
                                        # Display results for SELECT queries
                                        if result:
                                            data = result.fetchall()
                                            if data:
                                                columns = result.keys()
                                                result_df = pd.DataFrame(data, columns=columns)
                                                st.dataframe(result_df, use_container_width=True)
                                            else:
                                                st.info("Query executed successfully. No results returned.")
                                        else:
                                            st.info("Query executed successfully.")
                                    else:
                                        st.success("Query executed successfully!")
                                        if query_type in ["INSERT (Create)", "UPDATE (Modify)", "DELETE (Remove)"]:
                                            st.info("Data modified. Refresh the View Data tab to see changes.")
                                            
                                except Exception as e:
                                    st.error(f"Query error: {e}")
                            else:
                                st.warning("Please enter a SQL query.")
                    
                    with col2:
                        if st.button("📋 Copy Sample Query"):
                            st.code(sample_queries[query_type])
                
        except Exception as e:
            st.error(f"Database connection error: {e}")
            st.info("Please check your database configuration and try again.")

def show_database_backup():
    """Database backup and restore functionality"""
    st.markdown("#### 💾 Database Backup & Restore")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Backup Database")
        
        backup_tables = st.multiselect(
            "Select tables to backup:",
            ["customers", "chart_of_accounts", "invoices", "expenses", "inventory", "employees", "projects"],
            default=["customers", "chart_of_accounts", "invoices"]
        )
        
        if st.button("📦 Create Backup"):
            if backup_tables:
                with get_database_connection() as db:
                    backup_data = {}
                    for table in backup_tables:
                        try:
                            df = db.get_table_data(table)
                            backup_data[table] = df.to_dict('records')
                        except Exception as e:
                            st.error(f"Error backing up {table}: {e}")
                
                if backup_data:
                    import json
                    backup_json = json.dumps(backup_data, indent=2, default=str)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    st.download_button(
                        label="💾 Download Backup File",
                        data=backup_json,
                        file_name=f"datalink_backup_{timestamp}.json",
                        mime="application/json"
                    )
                    st.success("Backup created successfully!")
            else:
                st.warning("Please select at least one table to backup.")
    
    with col2:
        st.subheader("Restore Database")
        st.warning("⚠️ Restore will overwrite existing data!")
        
        uploaded_backup = st.file_uploader("Upload backup file:", type=['json'])
        
        if uploaded_backup and st.button("🔄 Restore from Backup"):
            try:
                backup_data = json.loads(uploaded_backup.read())
                
                with get_database_connection() as db:
                    restored_tables = []
                    for table_name, records in backup_data.items():
                        try:
                            # Clear existing data
                            db.execute_query(f"DELETE FROM {table_name}")
                            
                            # Insert backup data
                            for record in records:
                                columns = list(record.keys())
                                values = list(record.values())
                                placeholders = ', '.join(['%s'] * len(values))
                                
                                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                                db.execute_query(query, values)
                            
                            restored_tables.append(table_name)
                            
                        except Exception as e:
                            st.error(f"Error restoring {table_name}: {e}")
                
                if restored_tables:
                    st.success(f"Successfully restored tables: {', '.join(restored_tables)}")
                else:
                    st.error("No tables were restored successfully.")
                    
            except Exception as e:
                st.error(f"Error reading backup file: {e}")