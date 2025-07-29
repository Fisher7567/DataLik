# DataLink Business Management Platform - Replit Development Guide

## Overview

DataLink is a comprehensive business management platform built with Streamlit designed for African SMEs. It provides a complete suite of business tools organized into six main categories: Data Analysis, Finance, Sales, Logistics, Human Resources, Services, and Productivity. The platform features centralized authentication, role-based access control, and integrated business operations management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit with multi-page application structure
- **Layout**: Wide layout with expandable sidebar navigation
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts
- **State Management**: Streamlit session state for user authentication and data persistence
- **UI Components**: Native Streamlit components with custom styling

### Backend Architecture
- **Application Structure**: Modular Python application with utility modules
- **Authentication**: Custom authentication system using streamlit-authenticator with YAML configuration
- **Data Processing**: Pandas-based data manipulation and analysis
- **File Handling**: Support for CSV and Excel file uploads with multiple encoding support

### Data Storage Solutions
- **Session Storage**: Streamlit session state for temporary data storage
- **User Configuration**: YAML file-based user management (data/users.yaml)
- **File Storage**: In-memory processing of uploaded files
- **Export Formats**: CSV, Excel, and PDF export capabilities

## Key Components

### Authentication System (`utils/auth.py`)
- Role-based access control with predefined user roles (Admin, Manager, Analyst, User)
- Session-based authentication with cookie management
- YAML-based user configuration with hashed passwords
- Automatic authentication checking across all pages

### Data Processing (`utils/data_processor.py`)
- Multi-format file upload support (CSV, Excel)
- Data validation and quality assessment
- Sample data generation for demonstration purposes
- KPI metrics calculation and data filtering

### Visualization (`utils/charts.py`)
- Sales performance charts with date-based filtering
- Revenue trend analysis
- Customer analytics visualization
- Interactive Plotly-based charts with customization

### Export System (`utils/exports.py`)
- CSV export functionality
- Excel export with auto-adjusted column widths
- PDF report generation using ReportLab
- Multiple download formats for data and reports

### Page Structure
- **Main Dashboard** (`app.py`): Landing page with authentication and overview
- **Dashboard** (`pages/1_📊_Dashboard.py`): Comprehensive business metrics visualization
- **Data Upload** (`pages/2_📁_Data_Upload.py`): File upload and data management
- **Analytics** (`pages/3_📈_Analytics.py`): Advanced analytics and insights
- **Collaboration** (`pages/4_👥_Collaboration.py`): Team collaboration features
- **Settings** (`pages/5_⚙️_Settings.py`): User and platform configuration

## Data Flow

1. **Authentication Flow**: User credentials → YAML validation → Session state initialization
2. **Data Upload Flow**: File upload → Format detection → Pandas processing → Session storage
3. **Visualization Flow**: Session data → Data processing → Chart generation → Plotly rendering
4. **Export Flow**: Processed data → Format conversion → Download buffer creation
5. **Collaboration Flow**: User inputs → Session state updates → Shared view management

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization library
- **numpy**: Numerical computing support
- **streamlit-authenticator**: Authentication system
- **PyYAML**: YAML configuration parsing

### File Processing
- **openpyxl**: Excel file handling
- **io**: Buffer management for file operations

### Export Capabilities
- **reportlab**: PDF generation and formatting

### Data Analysis
- **datetime**: Date and time manipulation
- **json**: JSON data handling

## Deployment Strategy

### Development Environment
- **Runtime**: Python 3.x with Streamlit server
- **Configuration**: Environment-based settings through Streamlit config
- **File Structure**: Organized utility modules with clear separation of concerns

### Production Considerations
- **Authentication**: Currently uses local YAML storage (should be upgraded to database for production)
- **Data Persistence**: Session-based storage (requires database integration for production)
- **Scalability**: Single-user session model (needs multi-user database architecture)
- **Security**: Basic authentication system (should implement proper SSO integration)

### Recommended Production Upgrades
- **Database Integration**: Implement PostgreSQL with Drizzle ORM for data persistence
- **SSO Integration**: Add WorkOS or Auth0 for enterprise authentication
- **Real-time Features**: Implement WebSocket support for live updates
- **API Layer**: Add REST API endpoints for data operations
- **Container Deployment**: Docker containerization for scalable deployment

### Current Limitations
- No persistent data storage beyond session state
- Limited multi-user collaboration capabilities
- File-based user management not suitable for production scale
- No real-time data synchronization between users
- Basic export functionality without advanced formatting options

The application is currently designed as a proof-of-concept with room for significant architectural improvements for production deployment, particularly in data persistence, user management, and real-time collaboration features.