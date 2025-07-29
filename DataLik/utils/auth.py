import streamlit as st
import yaml
import streamlit_authenticator as stauth
from pathlib import Path

def load_user_config():
    """Load user configuration from YAML file"""
    config_file = Path("data/users.yaml")
    
    if config_file.exists():
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
    else:
        # Default configuration if file doesn't exist
        config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@datalink.com',
                        'name': 'Administrator',
                        'password': '$2b$12$gvmgYK.i2NfJhZ/7YJ1XgO8aIzGYZ5fZY9F7JQV3DgJ8jKNLxJ9m6',  # 'admin123'
                        'role': 'Admin'
                    },
                    'manager': {
                        'email': 'manager@company.com',
                        'name': 'Business Manager',
                        'password': '$2b$12$rJY9vY1UgN1H1K/5X8j6.uF2nXo3VwJgKxMo8TqR2Ij7ZJlK9O8r4',  # 'manager123'
                        'role': 'Manager'
                    },
                    'analyst': {
                        'email': 'analyst@company.com',
                        'name': 'Data Analyst',
                        'password': '$2b$12$tZ4fE8vL9mR2O6p7Y5j1XuK8nFo6VwJgPxTo5TqJ3Ij9ZLlM2O3r1',  # 'analyst123'
                        'role': 'Analyst'
                    },
                    'demo': {
                        'email': 'demo@company.com',
                        'name': 'Demo User',
                        'password': '$2b$12$uA5gK8yP0nS3O7q8Y6j2XvL9oGp7VwJgQyUp6TrK4Ij0ZMmN3O4r2',  # 'demo123'
                        'role': 'User'
                    }
                }
            },
            'cookie': {
                'name': 'datalink_auth',
                'key': 'datalink_secret_key_123',
                'expiry_days': 1
            },
            'preauthorized': {
                'emails': ['admin@datalink.com']
            }
        }
    
    return config

def check_authentication():
    """Main authentication function"""
    
    # Check if already authenticated
    if st.session_state.get('authenticated', False):
        return True
    
    # Load configuration
    config = load_user_config()
    
    # Create authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # Create login widget
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 DataLink Login")
        st.markdown("*Your Business Analytics Platform*")
        
        # Demo credentials info
        with st.expander("🎯 Demo Credentials"):
            st.markdown("""
            **Demo Accounts Available:**
            - **Username:** demo | **Password:** demo123 | **Role:** User
            - **Username:** analyst | **Password:** analyst123 | **Role:** Analyst  
            - **Username:** manager | **Password:** manager123 | **Role:** Manager
            - **Username:** admin | **Password:** admin123 | **Role:** Admin
            """)
        
        # Login form
        login_result = authenticator.login(location='main')
        if login_result is None:
            return False
        name, authentication_status, username = login_result
        
        if authentication_status == False:
            st.error('❌ Username/password is incorrect')
            return False
        elif authentication_status == None:
            st.warning('👆 Please enter your username and password')
            return False
        elif authentication_status:
            # Authentication successful
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.name = name
            
            # Get user role from config
            user_info = config['credentials']['usernames'].get(username, {})
            st.session_state.user_role = user_info.get('role', 'User')
            
            st.success(f'✅ Welcome {name}!')
            st.balloons()
            
            # Add logout button
            if authenticator.logout(location='sidebar'):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_role = None
                st.rerun()
            
            return True
    
    return False

def get_user_role():
    """Get current user's role"""
    return st.session_state.get('user_role', 'User')

def has_permission(required_role):
    """Check if user has required permission level"""
    role_hierarchy = {
        'User': 1,
        'Analyst': 2,
        'Manager': 3,
        'Admin': 4
    }
    
    current_role = get_user_role()
    current_level = role_hierarchy.get(current_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return current_level >= required_level

def require_role(required_role):
    """Decorator to require specific role for a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if has_permission(required_role):
                return func(*args, **kwargs)
            else:
                st.error(f"❌ Access denied. {required_role} role required.")
                return None
        return wrapper
    return decorator
