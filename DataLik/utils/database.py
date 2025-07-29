import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    st.error("Database URL not found. Please ensure PostgreSQL is configured.")
    st.stop()

# Create engine and session
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    st.stop()

class DatabaseManager:
    """Database operations manager for DataLink platform"""
    
    def __init__(self):
        self.engine = engine
        self.session = SessionLocal()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    def initialize_database(self):
        """Initialize all database tables"""
        try:
            # Create all tables
            self.create_users_table()
            self.create_finance_tables()
            self.create_sales_tables()
            self.create_logistics_tables()
            self.create_hr_tables()
            self.create_projects_table()
            self.create_audit_log_table()
            
            # Insert sample data if tables are empty
            self.insert_sample_data()
            
            return True
        except Exception as e:
            st.error(f"Database initialization failed: {e}")
            return False
    
    def create_users_table(self):
        """Create users table for authentication"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role VARCHAR(20) DEFAULT 'User',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        """
        self.session.execute(text(query))
        self.session.commit()
    
    def create_finance_tables(self):
        """Create finance-related tables"""
        
        # Chart of Accounts
        accounts_query = """
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            id SERIAL PRIMARY KEY,
            account_code VARCHAR(20) UNIQUE NOT NULL,
            account_name VARCHAR(100) NOT NULL,
            account_type VARCHAR(20) NOT NULL,
            balance DECIMAL(15,2) DEFAULT 0.00,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Invoices
        invoices_query = """
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            invoice_number VARCHAR(20) UNIQUE NOT NULL,
            customer_name VARCHAR(100) NOT NULL,
            customer_email VARCHAR(100),
            amount DECIMAL(15,2) NOT NULL,
            invoice_date DATE NOT NULL,
            due_date DATE NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            description TEXT,
            created_by VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Expenses
        expenses_query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            expense_id VARCHAR(20) UNIQUE NOT NULL,
            category VARCHAR(50) NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            expense_date DATE NOT NULL,
            vendor VARCHAR(100),
            description TEXT,
            receipt_path VARCHAR(255),
            status VARCHAR(20) DEFAULT 'Recorded',
            created_by VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Financial Transactions
        transactions_query = """
        CREATE TABLE IF NOT EXISTS financial_transactions (
            id SERIAL PRIMARY KEY,
            transaction_date DATE NOT NULL,
            description TEXT NOT NULL,
            debit_amount DECIMAL(15,2) DEFAULT 0.00,
            credit_amount DECIMAL(15,2) DEFAULT 0.00,
            account_code VARCHAR(20),
            reference_type VARCHAR(20),
            reference_id INTEGER,
            created_by VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        for query in [accounts_query, invoices_query, expenses_query, transactions_query]:
            self.session.execute(text(query))
        self.session.commit()
    
    def create_sales_tables(self):
        """Create sales-related tables"""
        
        # Customers
        customers_query = """
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            customer_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            company VARCHAR(100),
            industry VARCHAR(50),
            status VARCHAR(20) DEFAULT 'Active',
            source VARCHAR(50),
            total_value DECIMAL(15,2) DEFAULT 0.00,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_contact DATE
        );
        """
        
        # Leads
        leads_query = """
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            lead_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            company VARCHAR(100),
            source VARCHAR(50),
            score INTEGER DEFAULT 0,
            interest_level VARCHAR(20),
            status VARCHAR(20) DEFAULT 'New',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_contact DATE
        );
        """
        
        # Deals/Opportunities
        deals_query = """
        CREATE TABLE IF NOT EXISTS deals (
            id SERIAL PRIMARY KEY,
            deal_name VARCHAR(100) NOT NULL,
            customer_id INTEGER REFERENCES customers(id),
            value DECIMAL(15,2) NOT NULL,
            stage VARCHAR(20) NOT NULL,
            probability INTEGER DEFAULT 0,
            close_date DATE,
            sales_rep VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Sales Activities
        activities_query = """
        CREATE TABLE IF NOT EXISTS sales_activities (
            id SERIAL PRIMARY KEY,
            activity_date DATE NOT NULL,
            activity_type VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            related_to VARCHAR(20),
            related_id INTEGER,
            sales_rep VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        for query in [customers_query, leads_query, deals_query, activities_query]:
            self.session.execute(text(query))
        self.session.commit()
    
    def create_logistics_tables(self):
        """Create logistics-related tables"""
        
        # Inventory
        inventory_query = """
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            sku VARCHAR(50) UNIQUE NOT NULL,
            product_name VARCHAR(100) NOT NULL,
            category VARCHAR(50),
            current_stock INTEGER DEFAULT 0,
            reorder_point INTEGER DEFAULT 0,
            unit_cost DECIMAL(10,2) DEFAULT 0.00,
            unit_price DECIMAL(10,2) DEFAULT 0.00,
            supplier VARCHAR(100),
            location VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Purchase Orders
        purchase_orders_query = """
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id SERIAL PRIMARY KEY,
            po_number VARCHAR(20) UNIQUE NOT NULL,
            supplier VARCHAR(100) NOT NULL,
            order_date DATE NOT NULL,
            expected_date DATE,
            total_amount DECIMAL(15,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            notes TEXT,
            created_by VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Work Orders (Manufacturing)
        work_orders_query = """
        CREATE TABLE IF NOT EXISTS work_orders (
            id SERIAL PRIMARY KEY,
            wo_number VARCHAR(20) UNIQUE NOT NULL,
            product_sku VARCHAR(50),
            quantity INTEGER NOT NULL,
            start_date DATE,
            due_date DATE,
            status VARCHAR(20) DEFAULT 'Planned',
            priority VARCHAR(20) DEFAULT 'Medium',
            assigned_to VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        for query in [inventory_query, purchase_orders_query, work_orders_query]:
            self.session.execute(text(query))
        self.session.commit()
    
    def create_hr_tables(self):
        """Create HR-related tables"""
        
        # Employees
        employees_query = """
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            employee_id VARCHAR(20) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(20),
            department VARCHAR(50),
            position VARCHAR(100),
            hire_date DATE,
            salary DECIMAL(12,2),
            status VARCHAR(20) DEFAULT 'Active',
            manager_id INTEGER REFERENCES employees(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Job Postings
        job_postings_query = """
        CREATE TABLE IF NOT EXISTS job_postings (
            id SERIAL PRIMARY KEY,
            job_title VARCHAR(100) NOT NULL,
            department VARCHAR(50),
            location VARCHAR(100),
            job_type VARCHAR(20) DEFAULT 'Full-time',
            salary_min DECIMAL(12,2),
            salary_max DECIMAL(12,2),
            description TEXT,
            requirements TEXT,
            status VARCHAR(20) DEFAULT 'Open',
            posted_date DATE DEFAULT CURRENT_DATE,
            closing_date DATE,
            created_by VARCHAR(50)
        );
        """
        
        # Leave Requests
        leave_requests_query = """
        CREATE TABLE IF NOT EXISTS leave_requests (
            id SERIAL PRIMARY KEY,
            employee_id INTEGER REFERENCES employees(id),
            leave_type VARCHAR(50) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            days_requested INTEGER NOT NULL,
            reason TEXT,
            status VARCHAR(20) DEFAULT 'Pending',
            approved_by VARCHAR(50),
            approved_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        for query in [employees_query, job_postings_query, leave_requests_query]:
            self.session.execute(text(query))
        self.session.commit()
    
    def create_projects_table(self):
        """Create project management table"""
        projects_query = """
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            project_name VARCHAR(100) NOT NULL,
            description TEXT,
            start_date DATE,
            due_date DATE,
            status VARCHAR(20) DEFAULT 'Planning',
            progress INTEGER DEFAULT 0,
            budget DECIMAL(15,2),
            team_size INTEGER DEFAULT 0,
            project_manager VARCHAR(50),
            client VARCHAR(100),
            priority VARCHAR(20) DEFAULT 'Medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.session.execute(text(projects_query))
        self.session.commit()
    
    def create_audit_log_table(self):
        """Create audit log for tracking changes"""
        audit_query = """
        CREATE TABLE IF NOT EXISTS audit_log (
            id SERIAL PRIMARY KEY,
            table_name VARCHAR(50) NOT NULL,
            record_id INTEGER NOT NULL,
            action VARCHAR(20) NOT NULL,
            old_values JSONB,
            new_values JSONB,
            changed_by VARCHAR(50),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.session.execute(text(audit_query))
        self.session.commit()
    
    def insert_sample_data(self):
        """Insert sample data if tables are empty"""
        try:
            # Check if data already exists
            result = self.session.execute(text("SELECT COUNT(*) FROM customers"))
            if result.scalar() > 0:
                return  # Data already exists
            
            # Insert sample customers
            customers_data = [
                ("CUST-0001", "John Smith", "john@techcorp.com", "+234-801-123-4567", "TechCorp Ltd", "Technology", "Active", "Website", 15000.00, "Key decision maker"),
                ("CUST-0002", "Sarah Johnson", "sarah@financeplus.com", "+234-802-234-5678", "FinancePlus", "Finance", "Active", "Referral", 22000.00, "Long-term partnership potential"),
                ("CUST-0003", "Mike Davis", "mike@healthsolutions.com", "+234-803-345-6789", "Health Solutions", "Healthcare", "Prospect", "Cold Call", 0.00, "Interested in Q2 implementation"),
            ]
            
            for customer in customers_data:
                query = """
                INSERT INTO customers (customer_id, name, email, phone, company, industry, status, source, total_value, notes)
                VALUES (:p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9, :p10)
                """
                params = {f'p{i+1}': customer[i] for i in range(len(customer))}
                self.session.execute(text(query), params)
            
            # Insert sample chart of accounts
            accounts_data = [
                ("1000", "Cash", "Assets", 25000.00),
                ("1100", "Accounts Receivable", "Assets", 15000.00),
                ("1200", "Inventory", "Assets", 30000.00),
                ("2000", "Accounts Payable", "Liabilities", 8000.00),
                ("3000", "Owner Equity", "Equity", 50000.00),
                ("4000", "Sales Revenue", "Revenue", 45000.00),
                ("5000", "Cost of Goods Sold", "Expenses", 18000.00),
                ("5100", "Office Expenses", "Expenses", 3200.00),
            ]
            
            for account in accounts_data:
                query = """
                INSERT INTO chart_of_accounts (account_code, account_name, account_type, balance)
                VALUES (:p1, :p2, :p3, :p4)
                """
                params = {f'p{i+1}': account[i] for i in range(len(account))}
                self.session.execute(text(query), params)
            
            # Insert sample inventory
            inventory_data = [
                ("LAP-001", "Laptop Dell XPS", "Electronics", 25, 10, 800.00, 1200.00, "Dell Supplier", "Warehouse A"),
                ("CHR-002", "Office Chair", "Furniture", 8, 15, 150.00, 250.00, "Furniture Plus", "Warehouse B"),
                ("PRT-003", "Printer HP LaserJet", "Electronics", 45, 20, 300.00, 450.00, "HP Supplier", "Warehouse A"),
            ]
            
            for item in inventory_data:
                query = """
                INSERT INTO inventory (sku, product_name, category, current_stock, reorder_point, unit_cost, unit_price, supplier, location)
                VALUES (:p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9)
                """
                params = {f'p{i+1}': item[i] for i in range(len(item))}
                self.session.execute(text(query), params)
            
            # Insert sample employees
            employees_data = [
                ("EMP-001", "John", "Smith", "john.smith@company.com", "+234-801-111-1111", "Engineering", "Senior Developer", "2023-01-15", 75000.00, "Active"),
                ("EMP-002", "Sarah", "Johnson", "sarah.johnson@company.com", "+234-802-222-2222", "Sales", "Sales Manager", "2023-03-01", 65000.00, "Active"),
                ("EMP-003", "Mike", "Davis", "mike.davis@company.com", "+234-803-333-3333", "Marketing", "Marketing Specialist", "2023-06-10", 55000.00, "Active"),
            ]
            
            for employee in employees_data:
                query = """
                INSERT INTO employees (employee_id, first_name, last_name, email, phone, department, position, hire_date, salary, status)
                VALUES (:p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9, :p10)
                """
                params = {f'p{i+1}': employee[i] for i in range(len(employee))}
                self.session.execute(text(query), params)
            
            # Insert sample projects
            projects_data = [
                ("Website Redesign", "Complete overhaul of company website", "2024-01-01", "2024-02-15", "In Progress", 75, 15000.00, 4, "Project Manager 1", "Internal"),
                ("Mobile App Development", "Native mobile application", "2024-02-01", "2024-04-30", "Planning", 25, 50000.00, 6, "Project Manager 2", "TechCorp Ltd"),
                ("Database Migration", "Migrate legacy database to PostgreSQL", "2023-12-01", "2024-01-20", "Completed", 100, 8000.00, 3, "Project Manager 1", "Internal"),
            ]
            
            for project in projects_data:
                query = """
                INSERT INTO projects (project_name, description, start_date, due_date, status, progress, budget, team_size, project_manager, client)
                VALUES (:p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9, :p10)
                """
                params = {f'p{i+1}': project[i] for i in range(len(project))}
                self.session.execute(text(query), params)
            
            self.session.commit()
            print("Sample data inserted successfully")
            
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting sample data: {e}")
    
    def get_table_data(self, table_name, limit=None):
        """Get data from any table"""
        try:
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit}"
            
            result = self.session.execute(text(query))
            columns = result.keys()
            data = result.fetchall()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=columns)
            return df
        except Exception as e:
            st.error(f"Error fetching data from {table_name}: {e}")
            return pd.DataFrame()
    
    def execute_query(self, query, params=None):
        """Execute custom query"""
        try:
            if params:
                result = self.session.execute(text(query), params)
            else:
                result = self.session.execute(text(query))
            
            self.session.commit()
            return result
        except Exception as e:
            self.session.rollback()
            st.error(f"Query execution error: {e}")
            return None
    
    def get_business_metrics(self):
        """Get key business metrics from database"""
        metrics = {}
        
        try:
            # Customer metrics
            result = self.session.execute(text("SELECT COUNT(*) FROM customers WHERE status = 'Active'"))
            metrics['active_customers'] = result.scalar() or 0
            
            # Revenue metrics
            result = self.session.execute(text("SELECT SUM(amount) FROM invoices WHERE status = 'Paid'"))
            metrics['total_revenue'] = float(result.scalar() or 0)
            
            # Inventory metrics
            result = self.session.execute(text("SELECT COUNT(*) FROM inventory WHERE current_stock <= reorder_point"))
            metrics['low_stock_items'] = result.scalar() or 0
            
            # Employee metrics
            result = self.session.execute(text("SELECT COUNT(*) FROM employees WHERE status = 'Active'"))
            metrics['total_employees'] = result.scalar() or 0
            
            # Project metrics
            result = self.session.execute(text("SELECT COUNT(*) FROM projects WHERE status IN ('Planning', 'In Progress')"))
            metrics['active_projects'] = result.scalar() or 0
            
            return metrics
        except Exception as e:
            st.error(f"Error getting business metrics: {e}")
            return {}

def get_database_connection():
    """Get database connection for use in modules"""
    return DatabaseManager()

def initialize_database():
    """Initialize database tables and sample data"""
    with DatabaseManager() as db:
        return db.initialize_database()