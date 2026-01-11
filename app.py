"""
Streamlit dashboard for Life Insurance Premium Forecasting.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from data_models import Gender, PolicyType
from forecasting_engine import PremiumForecaster
from ai_insights import PremiumInsightsGenerator
from chat_interface import DashboardChatInterface

# Page configuration
st.set_page_config(
    page_title="Life Insurance Premium Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stExpander {
        background-color: #fafafa;
    }
    
    /* Floating Chat Button */
    .chat-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: #1f77b4;
        color: white;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        transition: all 0.3s ease;
    }
    .chat-button:hover {
        background-color: #1565a0;
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
    
    /* Chat Window */
    .chat-window {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 400px;
        height: 600px;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        z-index: 1001;
        display: flex;
        flex-direction: column;
        border: 1px solid #e0e0e0;
    }
    
    .chat-header {
        background-color: #1f77b4;
        color: white;
        padding: 15px;
        border-radius: 12px 12px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-header h3 {
        margin: 0;
        font-size: 18px;
    }
    
    .chat-close {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .chat-close:hover {
        background-color: rgba(255,255,255,0.2);
        border-radius: 50%;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        background-color: #f9f9f9;
    }
    
    .chat-input-container {
        padding: 15px;
        border-top: 1px solid #e0e0e0;
        background-color: white;
        border-radius: 0 0 12px 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'forecaster' not in st.session_state:
    st.session_state.forecaster = None
if 'insights_generator' not in st.session_state:
    st.session_state.insights_generator = None
if 'chat_interface' not in st.session_state:
    st.session_state.chat_interface = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'chat_params' not in st.session_state:
    st.session_state.chat_params = {}
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False


@st.cache_data(ttl=3600)  # Cache for 1 hour, but will refresh if CSV files change
def load_data():
    """Load data from CSV files"""
    try:
        # Define data directory
        data_dir = 'data'
        
        # Check if data directory exists
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Data directory '{data_dir}' not found. Please run 'python create_data_csvs.py' first.")
        
        # Load CSV files
        mortality_df = pd.read_csv(os.path.join(data_dir, 'mortality_data.csv'))
        economic_df = pd.read_csv(os.path.join(data_dir, 'economic_data.csv'))
        base_premium_df = pd.read_csv(os.path.join(data_dir, 'base_premiums.csv'))
        demographic_df = pd.read_csv(os.path.join(data_dir, 'demographic_distribution.csv'))
        
        # Validate data was loaded
        if mortality_df.empty or economic_df.empty or base_premium_df.empty or demographic_df.empty:
            raise ValueError("One or more CSV files are empty. Please regenerate data files.")
        
        # Ensure correct data types
        mortality_df['year'] = mortality_df['year'].astype(int)
        mortality_df['age'] = mortality_df['age'].astype(int)
        economic_df['year'] = economic_df['year'].astype(int)
        base_premium_df['age'] = base_premium_df['age'].astype(int)
        demographic_df['age'] = demographic_df['age'].astype(int)
        demographic_df['policy_count'] = demographic_df['policy_count'].astype(int)
        
        # Ensure smoking_status is string type if it exists (for consistent filtering)
        if 'smoking_status' in mortality_df.columns:
            mortality_df['smoking_status'] = mortality_df['smoking_status'].astype(str)
        if 'smoking_status' in base_premium_df.columns:
            base_premium_df['smoking_status'] = base_premium_df['smoking_status'].astype(str)
        if 'smoking_status' in demographic_df.columns:
            demographic_df['smoking_status'] = demographic_df['smoking_status'].astype(str)
        
        return mortality_df, economic_df, base_premium_df, demographic_df
    except FileNotFoundError as e:
        st.error(f"Error: {str(e)}")
        st.info("Please run 'python create_data_csvs.py' to generate data files.")
        raise
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.exception(e)
        raise


def initialize_forecaster():
    """Initialize the forecaster"""
    if st.session_state.forecaster is None:
        try:
            mortality_df, economic_df, base_premium_df, demographic_df = load_data()
            
            # Validate data before creating forecaster
            if mortality_df.empty:
                st.error("Error: Mortality data is empty. Please refresh the page.")
                return
            if economic_df.empty:
                st.error("Error: Economic data is empty. Please refresh the page.")
                return
            if base_premium_df.empty:
                st.error("Error: Base premium data is empty. Please refresh the page.")
                return
            if demographic_df.empty:
                st.error("Error: Demographic data is empty. Please refresh the page.")
                return
            
            # Check if India data exists
            if 'India' not in mortality_df['country'].unique():
                st.error(f"Error: India not found in mortality data. Available: {list(mortality_df['country'].unique())}")
                return
            
            # Validate smoking_status column exists in all required dataframes
            required_cols = ['smoking_status']
            for col in required_cols:
                if col not in mortality_df.columns:
                    st.warning(f"Warning: {col} not found in mortality data. Some filters may not work.")
                if col not in base_premium_df.columns:
                    st.warning(f"Warning: {col} not found in base premium data. Some filters may not work.")
                if col not in demographic_df.columns:
                    st.warning(f"Warning: {col} not found in demographic data. Some filters may not work.")
            
            st.session_state.forecaster = PremiumForecaster(
                mortality_df, economic_df, base_premium_df, demographic_df
            )
        except Exception as e:
            st.error(f"Error initializing forecaster: {str(e)}")
            st.exception(e)


def initialize_insights():
    """Initialize AI insights generator"""
    if st.session_state.insights_generator is None:
        try:
            st.session_state.insights_generator = PremiumInsightsGenerator()
        except Exception as e:
            st.warning(f"AI insights unavailable: {str(e)}. Please check your GROQ_API_KEY.")


def initialize_chat():
    """Initialize chat interface"""
    if st.session_state.chat_interface is None:
        try:
            st.session_state.chat_interface = DashboardChatInterface()
        except Exception as e:
            # Silently fail - chat is optional
            pass


def prepare_filtered_data_table(mortality_df, economic_df, base_premium_df, demographic_df, 
                                start_year, end_year, filters, country="India", scenario_name=None):
    """
    Combine and filter all CSV data into a comprehensive table.
    Returns a DataFrame with all relevant data columns.
    """
    # Start with demographic distribution as base
    filtered_demo = demographic_df[demographic_df['country'] == country].copy()
    
    # Apply filters
    if 'gender' in filters and filters['gender']:
        filtered_demo = filtered_demo[filtered_demo['gender'] == filters['gender']]
    if 'group' in filters and filters['group']:
        filtered_demo = filtered_demo[filtered_demo['group'] == filters['group']]
    if 'policy_type' in filters and filters['policy_type']:
        filtered_demo = filtered_demo[filtered_demo['policy_type'] == filters['policy_type']]
    if 'smoking_status' in filters and filters['smoking_status']:
        filtered_demo = filtered_demo[filtered_demo['smoking_status'] == filters['smoking_status']]
    if 'sum_insured' in filters and filters['sum_insured']:
        filtered_demo = filtered_demo[filtered_demo['sum_insured'] == filters['sum_insured']]
    if 'age_min' in filters:
        filtered_demo = filtered_demo[filtered_demo['age'] >= filters['age_min']]
    if 'age_max' in filters:
        filtered_demo = filtered_demo[filtered_demo['age'] <= filters['age_max']]
    
    # Merge with base premiums (include smoking_status if available)
    merge_cols = ['country', 'group', 'gender', 'age', 'policy_type']
    if 'smoking_status' in filtered_demo.columns and 'smoking_status' in base_premium_df.columns:
        merge_cols.append('smoking_status')
    
    merged = filtered_demo.merge(
        base_premium_df[base_premium_df['country'] == country],
        on=merge_cols,
        how='inner',
        suffixes=('', '_base')
    )
    
    # Create rows for each year in the forecast range
    result_rows = []
    for year in range(start_year, end_year + 1):
        # Get economic data for this year
        year_economic = economic_df[
            (economic_df['year'] == year) & 
            (economic_df['country'] == country)
        ]
        
        if year_economic.empty:
            # Use most recent economic data if not available
            year_economic = economic_df[
                (economic_df['year'] == economic_df['year'].max()) & 
                (economic_df['country'] == country)
            ]
        
        if year_economic.empty:
            continue
        
        econ_data = year_economic.iloc[0]
        
        # Get mortality data for this year
        year_mortality = mortality_df[
            (mortality_df['year'] == year) & 
            (mortality_df['country'] == country)
        ]
        
        if year_mortality.empty:
            # Use most recent mortality data if not available
            year_mortality = mortality_df[
                (mortality_df['year'] == mortality_df['year'].max()) & 
                (mortality_df['country'] == country)
            ]
        
        # For each demographic combination
        for _, row in merged.iterrows():
            # Find matching mortality data (include smoking_status if available)
            mortality_filter = (year_mortality['age'] == row['age']) & \
                             (year_mortality['gender'] == row['gender'])
            
            if 'smoking_status' in row and 'smoking_status' in year_mortality.columns:
                mortality_filter = mortality_filter & (year_mortality['smoking_status'] == row['smoking_status'])
            
            mortality_match = year_mortality[mortality_filter]
            
            if mortality_match.empty:
                continue
            
            mortality_data = mortality_match.iloc[0]
            
            # Create comprehensive row
            result_row = {
                'year': year,
                'scenario': scenario_name if scenario_name else 'base',
                'country': country,
                'group': row['group'],
                'gender': row['gender'],
                'age': row['age'],
                'policy_type': row['policy_type'],
                'policy_count': row['policy_count'],
                'mortality_rate': mortality_data['mortality_rate'],
                'life_expectancy': mortality_data['life_expectancy'],
                'inflation_rate': econ_data['inflation_rate'],
                'interest_rate': econ_data['interest_rate'],
                'gdp_growth': econ_data['gdp_growth']
            }
            
            # Handle premium: use premium_per_unit if available, otherwise base_premium
            if 'premium_per_unit' in row:
                result_row['premium_per_unit'] = row['premium_per_unit']
                # Calculate actual premium if sum_insured is available
                if 'sum_insured' in row:
                    result_row['sum_insured'] = row['sum_insured']
                    result_row['base_premium'] = row['premium_per_unit'] * (row['sum_insured'] / 100000.0)
                else:
                    result_row['base_premium'] = row['premium_per_unit'] * 10.0  # Default ₹10 lakh
            elif 'base_premium' in row:
                result_row['base_premium'] = row['base_premium']
                # Calculate premium_per_unit from base_premium (assume ₹10 lakh default)
                result_row['premium_per_unit'] = row['base_premium'] / 10.0
            
            # Include smoking_status if available
            if 'smoking_status' in row:
                result_row['smoking_status'] = row['smoking_status']
            
            # Include sum_insured if available
            if 'sum_insured' in row:
                result_row['sum_insured'] = row['sum_insured']
            
            result_rows.append(result_row)
    
    if not result_rows:
        return pd.DataFrame()
    
    return pd.DataFrame(result_rows)


def main():
    # Header
    st.markdown('<p class="main-header">📊 Life Insurance Premium Forecasting Dashboard</p>', 
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Forecasting premiums for the next decade by combining longevity, mortality trends, and economic indicators</p>', 
                unsafe_allow_html=True)
    
    # Initialize chat interface
    initialize_chat()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Country (India only)
        selected_country = "India"
        st.info(f"📍 Country: **{selected_country}**")
        
        # Forecast period
        st.subheader("Forecast Period")
        
        # Use chat params if available
        default_start = st.session_state.chat_params.get('start_year', 2024) if st.session_state.chat_params else 2024
        default_end = st.session_state.chat_params.get('end_year', 2034) if st.session_state.chat_params else 2034
        
        start_year = st.number_input("Start Year", min_value=2024, max_value=2035, value=default_start)
        end_year = st.number_input("End Year", min_value=2024, max_value=2035, value=default_end)
        
        if end_year <= start_year:
            st.error("End year must be greater than start year")
            return
        
        # Filters
        st.subheader("📋 Filters")
        
        # Use chat params if available
        if st.session_state.chat_params:
            cp = st.session_state.chat_params
            default_group = cp.get('group', 'All')
            default_gender = cp.get('gender', 'All')
            default_policy = cp.get('policy_type', 'All')
            default_smoking_status = cp.get('smoking_status', 'All')
            default_age_min = cp.get('age_min', 20)
            default_age_max = cp.get('age_max', 80)
            chat_sum_insured = cp.get('sum_insured')
        else:
            default_group = 'All'
            default_gender = 'All'
            default_policy = 'All'
            default_smoking_status = 'All'
            default_age_min = 20
            default_age_max = 80
            chat_sum_insured = None
        
        group_idx = ["All", "Individual", "Family", "Corporate"].index(default_group) if default_group in ["All", "Individual", "Family", "Corporate"] else 0
        gender_idx = ["All", "Male", "Female"].index(default_gender) if default_gender in ["All", "Male", "Female"] else 0
        policy_idx = ["All", "Term Life", "Whole Life"].index(default_policy) if default_policy in ["All", "Term Life", "Whole Life"] else 0
        smoking_idx = ["All", "Smoker", "Non-Smoker"].index(default_smoking_status) if default_smoking_status in ["All", "Smoker", "Non-Smoker"] else 0
        
        filter_group = st.selectbox("Group", ["All", "Individual", "Family", "Corporate"], index=group_idx)
        filter_gender = st.selectbox("Gender", ["All", "Male", "Female"], index=gender_idx)
        filter_policy_type = st.selectbox("Policy Type", ["All", "Term Life", "Whole Life"], index=policy_idx)
        filter_smoking_status = st.selectbox("Smoking Status", ["All", "Smoker", "Non-Smoker"], index=smoking_idx)
        
        # Sum Insured selector (for display and calculation reference)
        st.subheader("💰 Sum Insured")
        sum_insured_options = {
            "₹10 Lakh": 1000000,
            "₹25 Lakh": 2500000,
            "₹50 Lakh": 5000000,
            "₹1 Crore": 10000000,
            "₹2 Crore": 20000000,
            "All": None
        }
        # Find the index for sum_insured from chat_params
        if chat_sum_insured:
            # Find matching label
            matching_label = None
            for label, value in sum_insured_options.items():
                if value == chat_sum_insured:
                    matching_label = label
                    break
            if matching_label:
                sum_insured_idx = list(sum_insured_options.keys()).index(matching_label)
            else:
                sum_insured_idx = 2  # Default to ₹50 Lakh
        else:
            sum_insured_idx = 2  # Default to ₹50 Lakh
        
        selected_sum_insured_label = st.selectbox(
            "Sum Insured (Coverage Amount)",
            list(sum_insured_options.keys()),
            index=sum_insured_idx,
            help="Select the coverage amount to calculate premiums. Premiums are calculated per ₹1 lakh and multiplied by sum insured."
        )
        selected_sum_insured = sum_insured_options[selected_sum_insured_label]
        
        filter_age_min = st.slider("Minimum Age", 20, 80, default_age_min)
        filter_age_max = st.slider("Maximum Age", 20, 80, default_age_max)
        
        if filter_age_min > filter_age_max:
            st.error("Minimum age must be less than maximum age")
            return
        
        # Build filters dict
        filters = {}
        if filter_group != "All":
            filters['group'] = filter_group
        if filter_gender != "All":
            filters['gender'] = filter_gender
        if filter_policy_type != "All":
            filters['policy_type'] = filter_policy_type
        if filter_smoking_status != "All":
            filters['smoking_status'] = filter_smoking_status
        if selected_sum_insured is not None:
            filters['sum_insured'] = selected_sum_insured
        filters['age_min'] = filter_age_min
        filters['age_max'] = filter_age_max
        filters['_display_sum_insured'] = selected_sum_insured  # For UI display
        
        # Scenario selection
        st.subheader("📈 Scenario")
        
        # Check if chat wants to compare all
        if st.session_state.chat_params and st.session_state.chat_params.get('compare_all'):
            scenario_mode_idx = 1  # Compare All Scenarios
        elif st.session_state.chat_params and st.session_state.chat_params.get('scenario'):
            scenario_mode_idx = 0  # Single Scenario
        else:
            scenario_mode_idx = 1
        
        scenario_mode = st.radio(
            "View Mode",
            ["Single Scenario", "Compare All Scenarios"],
            index=scenario_mode_idx
        )
        
        if scenario_mode == "Single Scenario":
            # Use chat scenario if available
            chat_scenario = st.session_state.chat_params.get('scenario', 'base') if st.session_state.chat_params else 'base'
            scenario_map = {"base": 0, "optimistic": 1, "pessimistic": 2}
            default_scenario_idx = scenario_map.get(chat_scenario, 0)
            
            selected_scenario = st.selectbox(
                "Select Scenario",
                ["base", "optimistic", "pessimistic"],
                format_func=lambda x: {
                    "base": "Base Case",
                    "optimistic": "Optimistic",
                    "pessimistic": "Pessimistic"
                }[x],
                index=default_scenario_idx
            )
        else:
            selected_scenario = None
        
        # Clear chat params after use (optional - comment out if you want them to persist)
        # if not use_chat:
        #     st.session_state.chat_params = {}
    
    # Initialize components
    initialize_forecaster()
    initialize_insights()
    
    if st.session_state.forecaster is None:
        st.error("Failed to initialize forecaster. Please refresh the page.")
        return
    
    # Floating Chat Button and Window
    if st.session_state.chat_interface:
        # Create columns to position chat button on the right
        col1, col2 = st.columns([0.95, 0.05])
        
        with col2:
            # Chat toggle button (positioned on the right)
            if st.button("💬", key="chat_toggle", help="Open Chat Assistant", use_container_width=True):
                st.session_state.chat_open = not st.session_state.chat_open
                st.rerun()
        
        # Chat window (expander style)
        if st.session_state.chat_open:
            with st.expander("💬 Chat Assistant", expanded=True):
                st.info("💡 Try: 'Show forecast for males aged 30-50' or 'Compare all scenarios'")
                
                # Display chat history
                for message in st.session_state.chat_messages[-10:]:  # Show last 10 messages
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                
                # Chat input
                if prompt := st.chat_input("Ask about premium forecasts...", key="chat_input"):
                    # Add user message
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})
                    
                    # Parse query
                    with st.spinner("Processing your query..."):
                        try:
                            parsed_params = st.session_state.chat_interface.parse_query(prompt)
                            
                            # Update sidebar parameters based on chat
                            st.session_state.chat_params = parsed_params
                            
                            # Generate response
                            response = f"✅ I'll show you: "
                            if parsed_params.get('gender') and parsed_params.get('gender') != 'All':
                                response += f"{parsed_params.get('gender')} "
                            if parsed_params.get('group') and parsed_params.get('group') != 'All':
                                response += f"{parsed_params.get('group')} "
                            if parsed_params.get('policy_type') and parsed_params.get('policy_type') != 'All':
                                response += f"{parsed_params.get('policy_type')} "
                            if parsed_params.get('smoking_status') and parsed_params.get('smoking_status') != 'All':
                                response += f"{parsed_params.get('smoking_status')} "
                            if parsed_params.get('sum_insured'):
                                si_value = parsed_params.get('sum_insured')
                                if si_value == 1000000:
                                    response += "₹10 Lakh "
                                elif si_value == 2500000:
                                    response += "₹25 Lakh "
                                elif si_value == 5000000:
                                    response += "₹50 Lakh "
                                elif si_value == 10000000:
                                    response += "₹1 Crore "
                                elif si_value == 20000000:
                                    response += "₹2 Crore "
                                else:
                                    response += f"₹{si_value/100000:.0f} Lakh "
                            if parsed_params.get('age_min') or parsed_params.get('age_max'):
                                min_age = parsed_params.get('age_min', 20)
                                max_age = parsed_params.get('age_max', 80)
                                if min_age != 20 or max_age != 80:
                                    if min_age == max_age:
                                        response += f"age {min_age} "
                                    else:
                                        response += f"ages {min_age}-{max_age} "
                            if parsed_params.get('scenario'):
                                response += f"({parsed_params.get('scenario')} scenario)"
                            if parsed_params.get('compare_all'):
                                response = "✅ I'll compare all scenarios for you."
                            
                            st.session_state.chat_messages.append({"role": "assistant", "content": response})
                            st.rerun()
                            
                        except Exception as e:
                            st.session_state.chat_messages.append({
                                "role": "assistant", 
                                "content": f"❌ I had trouble understanding that. Could you rephrase? (Error: {str(e)})"
                            })
                            st.rerun()
                
                # Close button
                if st.button("Close Chat", key="close_chat"):
                    st.session_state.chat_open = False
                    st.rerun()
    
    # Main content
    if scenario_mode == "Compare All Scenarios":
        # Compare scenarios
        with st.spinner("Generating forecasts for all scenarios..."):
            comparison_df = st.session_state.forecaster.compare_scenarios(
                start_year, end_year, selected_country, filters
            )
        
        # Check if comparison_df is valid
        if comparison_df.empty:
            # Debug information
            st.error("No forecast data available. Please check your filters and data.")
            with st.expander("🔍 Debug Information", expanded=False):
                st.write("**Filters applied:**", filters)
                st.write("**Start Year:**", start_year)
                st.write("**End Year:**", end_year)
                st.write("**Country:**", selected_country)
                
                # Check if forecaster is initialized
                if st.session_state.forecaster is None:
                    st.error("Forecaster is not initialized!")
                else:
                    # Check data availability
                    mortality_df, economic_df, base_premium_df, demographic_df = load_data()
                    
                    # Check smoking_status filter
                    if 'smoking_status' in filters and filters['smoking_status']:
                        st.write(f"**Smoking Status Filter:** {filters['smoking_status']}")
                        st.write(f"**Base Premiums with {filters['smoking_status']}:**", 
                                len(base_premium_df[base_premium_df['smoking_status'] == filters['smoking_status']]) if 'smoking_status' in base_premium_df.columns else "Column not found")
                        st.write(f"**Demographic with {filters['smoking_status']}:**", 
                                len(demographic_df[demographic_df['smoking_status'] == filters['smoking_status']]) if 'smoking_status' in demographic_df.columns else "Column not found")
                        st.write(f"**Mortality with {filters['smoking_status']}:**", 
                                len(mortality_df[mortality_df['smoking_status'] == filters['smoking_status']]) if 'smoking_status' in mortality_df.columns else "Column not found")
            return
        
        if 'scenario' not in comparison_df.columns:
            st.error(f"Invalid data structure. Expected 'scenario' column. Available columns: {list(comparison_df.columns)}")
            return
        
        # Overview metrics
        st.subheader("📊 Overview Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        base_data = comparison_df[comparison_df['scenario'] == 'base']
        if not base_data.empty:
            current_premium = base_data.iloc[0]['average_premium']
            final_premium = base_data.iloc[-1]['average_premium']
            change_pct = ((final_premium - current_premium) / current_premium) * 100
            
            # Get premium per unit and sum insured if available
            current_premium_per_unit = base_data.iloc[0].get('average_premium_per_unit', current_premium / 10.0)
            avg_sum_insured = base_data.iloc[0].get('average_sum_insured', 10000000)  # Default ₹1Cr
            
            col1.metric("Current Premium (Base)", f"₹{current_premium:,.2f}", 
                       help=f"Premium per unit: ₹{current_premium_per_unit:,.2f} per ₹1L | Avg Sum Insured: ₹{avg_sum_insured/100000:.1f}L")
            col2.metric("10-Year Forecast (Base)", f"₹{final_premium:,.2f}",
                       help=f"Premium per unit: ₹{base_data.iloc[-1].get('average_premium_per_unit', final_premium/10.0):,.2f} per ₹1L")
            col3.metric("Change (%)", f"{change_pct:+.1f}%")
            col4.metric("Total Policies", f"{base_data.iloc[0]['total_policies']:,}")
        
        # Scenario comparison chart
        st.subheader("📈 Premium Forecast: Scenario Comparison")
        
        fig = go.Figure()
        
        scenarios = comparison_df['scenario'].unique()
        colors = {'base': '#1f77b4', 'optimistic': '#2ca02c', 'pessimistic': '#d62728'}
        names = {'base': 'Base Case', 'optimistic': 'Optimistic', 'pessimistic': 'Pessimistic'}
        
        for scenario in scenarios:
            scenario_data = comparison_df[comparison_df['scenario'] == scenario]
            fig.add_trace(go.Scatter(
                x=scenario_data['year'],
                y=scenario_data['average_premium'],
                mode='lines+markers',
                name=names[scenario],
                line=dict(color=colors[scenario], width=3),
                marker=dict(size=8)
            ))
        
        # Get sum insured info for subtitle
        sum_insured_info = ""
        if not comparison_df.empty and 'average_sum_insured' in comparison_df.columns:
            avg_si = comparison_df['average_sum_insured'].mean()
            sum_insured_info = f" (Avg Sum Insured: ₹{avg_si/100000:.1f}L)"
        elif filters.get('_display_sum_insured'):
            si = filters['_display_sum_insured']
            sum_insured_info = f" (Sum Insured: ₹{si/100000:.1f}L)"
        
        fig.update_layout(
            title=f"Average Premium Forecast by Scenario{sum_insured_info}",
            xaxis_title="Year",
            yaxis_title="Average Premium (₹)",
            hovermode='x unified',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Economic indicators
        st.subheader("💰 Economic Indicators by Scenario")
        
        # Create individual charts with legends at bottom of each
        scenarios_list = list(scenarios)
        
        # Create 2x2 grid layout
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Inflation Rate Chart
            fig_inflation = go.Figure()
            for scenario in scenarios_list:
                scenario_data = comparison_df[comparison_df['scenario'] == scenario]
                fig_inflation.add_trace(
                    go.Scatter(x=scenario_data['year'], y=scenario_data['inflation_rate'],
                              name=names[scenario], 
                              line=dict(color=colors[scenario], width=2),
                              mode='lines+markers',
                              marker=dict(size=6))
                )
            fig_inflation.update_layout(
                title=dict(text="Inflation Rate", y=0.97, x=0.5, xanchor='center', yanchor='top'),
                xaxis_title="Year",
                yaxis_title="Rate (%)",
                height=420,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.01,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.95)',
                    bordercolor='rgba(0,0,0,0.3)',
                    borderwidth=1,
                    font=dict(size=10)
                ),
                margin=dict(t=80, b=60, l=60, r=50)
            )
            st.plotly_chart(fig_inflation, use_container_width=True)
            
            # GDP Growth Chart
            fig_gdp = go.Figure()
            for scenario in scenarios_list:
                scenario_data = comparison_df[comparison_df['scenario'] == scenario]
                fig_gdp.add_trace(
                    go.Scatter(x=scenario_data['year'], y=scenario_data['gdp_growth'],
                              name=names[scenario], 
                              line=dict(color=colors[scenario], width=2),
                              mode='lines+markers',
                              marker=dict(size=6))
                )
            fig_gdp.update_layout(
                title=dict(text="GDP Growth", y=0.97, x=0.5, xanchor='center', yanchor='top'),
                xaxis_title="Year",
                yaxis_title="Rate (%)",
                height=420,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.01,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.95)',
                    bordercolor='rgba(0,0,0,0.3)',
                    borderwidth=1,
                    font=dict(size=10)
                ),
                margin=dict(t=80, b=60, l=60, r=50)
            )
            st.plotly_chart(fig_gdp, use_container_width=True)
        
        with chart_col2:
            # Interest Rate Chart
            fig_interest = go.Figure()
            for scenario in scenarios_list:
                scenario_data = comparison_df[comparison_df['scenario'] == scenario]
                fig_interest.add_trace(
                    go.Scatter(x=scenario_data['year'], y=scenario_data['interest_rate'],
                              name=names[scenario], 
                              line=dict(color=colors[scenario], width=2),
                              mode='lines+markers',
                              marker=dict(size=6))
                )
            fig_interest.update_layout(
                title=dict(text="Interest Rate", y=0.97, x=0.5, xanchor='center', yanchor='top'),
                xaxis_title="Year",
                yaxis_title="Rate (%)",
                height=420,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.01,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.95)',
                    bordercolor='rgba(0,0,0,0.3)',
                    borderwidth=1,
                    font=dict(size=10)
                ),
                margin=dict(t=80, b=60, l=60, r=50)
            )
            st.plotly_chart(fig_interest, use_container_width=True)
            
            # Premium vs Interest Rate Chart
            fig_premium_interest = go.Figure()
            for scenario in scenarios_list:
                scenario_data = comparison_df[comparison_df['scenario'] == scenario]
                fig_premium_interest.add_trace(
                    go.Scatter(x=scenario_data['interest_rate'], y=scenario_data['average_premium'],
                              name=names[scenario], 
                              mode='markers',
                              marker=dict(color=colors[scenario], size=8))
                )
            fig_premium_interest.update_layout(
                title=dict(text="Premium vs Interest Rate", y=0.97, x=0.5, xanchor='center', yanchor='top'),
                xaxis_title="Interest Rate (%)",
                yaxis_title="Premium (₹)",
                height=420,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.01,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.95)',
                    bordercolor='rgba(0,0,0,0.3)',
                    borderwidth=1,
                    font=dict(size=10)
                ),
                margin=dict(t=80, b=60, l=60, r=50)
            )
            st.plotly_chart(fig_premium_interest, use_container_width=True)
        
        # Mortality & Longevity Trends by Scenario
        if 'average_mortality_rate' in comparison_df.columns and 'average_life_expectancy' in comparison_df.columns:
            st.subheader("📉 Mortality & Longevity Trends by Scenario")
            
            # Create individual charts with legends at top of each
            longevity_col1, longevity_col2 = st.columns(2)
            
            with longevity_col1:
                # Mortality Rate Chart
                fig_mortality = go.Figure()
                for scenario in scenarios_list:
                    scenario_data = comparison_df[comparison_df['scenario'] == scenario]
                    fig_mortality.add_trace(
                        go.Scatter(x=scenario_data['year'], y=scenario_data['average_mortality_rate'],
                                  name=names[scenario], 
                                  line=dict(color=colors[scenario], width=2),
                                  mode='lines+markers',
                                  marker=dict(size=6))
                    )
                fig_mortality.update_layout(
                    title=dict(text="Mortality Rate Trend", y=0.97, x=0.5, xanchor='center', yanchor='top'),
                    xaxis_title="Year",
                    yaxis_title="Mortality Rate (per 1000)",
                    height=470,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.01,
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(255,255,255,0.95)',
                        bordercolor='rgba(0,0,0,0.3)',
                        borderwidth=1,
                        font=dict(size=10)
                    ),
                    margin=dict(t=80, b=60, l=60, r=50)
                )
                st.plotly_chart(fig_mortality, use_container_width=True)
            
            with longevity_col2:
                # Life Expectancy Chart
                fig_life_expectancy = go.Figure()
                for scenario in scenarios_list:
                    scenario_data = comparison_df[comparison_df['scenario'] == scenario]
                    fig_life_expectancy.add_trace(
                        go.Scatter(x=scenario_data['year'], y=scenario_data['average_life_expectancy'],
                                  name=names[scenario], 
                                  line=dict(color=colors[scenario], width=2),
                                  mode='lines+markers',
                                  marker=dict(size=6))
                    )
                fig_life_expectancy.update_layout(
                    title=dict(text="Life Expectancy Trend", y=0.97, x=0.5, xanchor='center', yanchor='top'),
                    xaxis_title="Year",
                    yaxis_title="Life Expectancy (years)",
                    height=470,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.01,
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(255,255,255,0.95)',
                        bordercolor='rgba(0,0,0,0.3)',
                        borderwidth=1,
                        font=dict(size=10)
                    ),
                    margin=dict(t=80, b=60, l=60, r=50)
                )
                st.plotly_chart(fig_life_expectancy, use_container_width=True)
        
        # AI Insights - Enhanced
        if st.session_state.insights_generator:
            st.subheader("🤖 AI-Powered Insights")
            
            # Key Metrics Cards
            with st.expander("📊 Key Metrics", expanded=True):
                comparison_result = st.session_state.insights_generator.generate_scenario_comparison(comparison_df, filters)
                
                if isinstance(comparison_result, dict) and 'premium_range' in comparison_result:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Premium Range",
                            f"₹{comparison_result['premium_range']['min']:,.0f} - ₹{comparison_result['premium_range']['max']:,.0f}",
                            f"₹{comparison_result['premium_range']['spread']:,.0f} spread"
                        )
                    
                    with col2:
                        best_scenario_name = comparison_result.get('best_scenario', 'base').title()
                        st.metric(
                            "Best Scenario",
                            best_scenario_name,
                            f"₹{comparison_result['premium_range']['min']:,.0f}"
                        )
                    
                    with col3:
                        worst_scenario_name = comparison_result.get('worst_scenario', 'base').title()
                        st.metric(
                            "Worst Scenario",
                            worst_scenario_name,
                            f"₹{comparison_result['premium_range']['max']:,.0f}"
                        )
                    
                    with col4:
                        spread_pct = comparison_result['premium_range'].get('spread_pct', 0)
                        st.metric(
                            "Scenario Spread",
                            f"{spread_pct:.1f}%",
                            "Difference between scenarios"
                        )
            
            # Scenario Comparison Analysis
            with st.expander("📝 Detailed Scenario Analysis", expanded=True):
                with st.spinner("Generating comprehensive analysis..."):
                    if isinstance(comparison_result, dict):
                        st.markdown(comparison_result.get('analysis', 'Analysis not available'))
                        
                        # Show scenario details
                        if 'scenarios' in comparison_result:
                            st.markdown("### 📈 Scenario Details")
                            scenario_tabs = st.tabs([s.title() for s in comparison_result['scenarios'].keys()])
                            
                            for idx, (scenario, details) in enumerate(comparison_result['scenarios'].items()):
                                with scenario_tabs[idx]:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Starting Premium", f"₹{details['start_premium']:,.2f}")
                                        st.metric("Ending Premium", f"₹{details['end_premium']:,.2f}")
                                        st.metric("Total Change", f"{details['change_pct']:+.1f}%")
                                    with col2:
                                        st.metric("Avg Inflation", f"{details['avg_inflation']:.2f}%")
                                        st.metric("Avg Interest Rate", f"{details['avg_interest']:.2f}%")
                                        st.metric("Premium Volatility", f"{details.get('volatility', 0):.2f}%")
                    else:
                        st.write(comparison_result)
            
            # Recommendations
            with st.expander("💡 Strategic Recommendations", expanded=True):
                with st.spinner("Generating recommendations..."):
                    recommendations_result = st.session_state.insights_generator.generate_recommendations(comparison_df, filters)
                    
                    if isinstance(recommendations_result, dict):
                        st.markdown(recommendations_result.get('recommendations', 'Recommendations not available'))
                        
                        # Show key metrics
                        if 'metrics' in recommendations_result:
                            st.markdown("### 📊 Recommendation Metrics")
                            metrics = recommendations_result['metrics']
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Avg Premium Increase", f"{metrics['avg_premium_increase']:.1f}%")
                            with col2:
                                st.metric("Premium Spread", f"{metrics['spread_pct']:.1f}%")
                    else:
                        st.write(recommendations_result)
            
            # Driver Impact Analysis
            with st.expander("🔍 Driver Impact Analysis", expanded=False):
                base_data = comparison_df[comparison_df['scenario'] == 'base']
                if not base_data.empty:
                    driver_impact = st.session_state.insights_generator.calculate_driver_impact(base_data)
                    
                    if driver_impact and 'drivers' in driver_impact:
                        st.markdown(f"**Total Premium Change: {driver_impact['total_premium_change_pct']:+.1f}%**")
                        st.markdown("### Factor Impact on Premiums")
                        
                        for driver_name, driver_data in driver_impact['drivers'].items():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.write(f"**{driver_name.replace('_', ' ').title()}**")
                            with col2:
                                corr = driver_data['correlation']
                                st.write(f"Correlation: {corr:+.2f}")
                            with col3:
                                impact_level = driver_data['impact']
                                color = "🔴" if impact_level == "High" else "🟡" if impact_level == "Medium" else "🟢"
                                st.write(f"{color} {impact_level} Impact")
        
        # Comprehensive Data Table
        st.subheader("📊 Comprehensive Data Table")
        st.markdown("**All data from CSVs filtered by your selections**")
        
        # Get raw data
        mortality_df, economic_df, base_premium_df, demographic_df = load_data()
        
        # Prepare filtered data table for each scenario
        all_data_tables = []
        for scenario in ['base', 'optimistic', 'pessimistic']:
            scenario_data = prepare_filtered_data_table(
                mortality_df, economic_df, base_premium_df, demographic_df,
                start_year, end_year, filters, selected_country, scenario
            )
            if not scenario_data.empty:
                all_data_tables.append(scenario_data)
        
        if all_data_tables:
            combined_table = pd.concat(all_data_tables, ignore_index=True)
            
            # Sort by scenario, year, age, gender
            sort_cols = ['scenario', 'year', 'age', 'gender', 'group', 'policy_type']
            if 'smoking_status' in combined_table.columns:
                sort_cols.insert(-1, 'smoking_status')
            combined_table = combined_table.sort_values(sort_cols)
            
            # Format numeric columns for display
            display_table = combined_table.copy()
            
            # Format premium columns
            if 'base_premium' in display_table.columns:
                display_table['base_premium'] = display_table['base_premium'].apply(lambda x: f"₹{x:,.2f}")
            if 'premium_per_unit' in display_table.columns:
                display_table['premium_per_unit'] = display_table['premium_per_unit'].apply(lambda x: f"₹{x:,.2f}")
            if 'sum_insured' in display_table.columns:
                display_table['sum_insured'] = display_table['sum_insured'].apply(lambda x: f"₹{x/100000:.1f}L" if x < 10000000 else f"₹{x/10000000:.1f}Cr")
            
            display_table['mortality_rate'] = display_table['mortality_rate'].apply(lambda x: f"{x:.4f}")
            display_table['life_expectancy'] = display_table['life_expectancy'].apply(lambda x: f"{x:.1f}")
            display_table['inflation_rate'] = display_table['inflation_rate'].apply(lambda x: f"{x:.2f}%")
            display_table['interest_rate'] = display_table['interest_rate'].apply(lambda x: f"{x:.2f}%")
            display_table['gdp_growth'] = display_table['gdp_growth'].apply(lambda x: f"{x:.2f}%")
            
            st.dataframe(display_table, use_container_width=True, height=400)
            
            # Download button
            csv = combined_table.to_csv(index=False)
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"premium_forecast_data_{start_year}_{end_year}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data available for the selected filters.")
        
        # Summary forecast data table (existing)
        with st.expander("📋 Summary Forecast Data (Aggregated)", expanded=False):
            st.dataframe(comparison_df, use_container_width=True)
    
    else:
        # Single scenario view
        with st.spinner(f"Generating forecast for {selected_scenario} scenario..."):
            forecast_df = st.session_state.forecaster.forecast_average_premium(
                start_year, end_year, selected_scenario, selected_country, filters
            )
        
        if forecast_df.empty:
            st.error("No data available for the selected filters. Please adjust your filters.")
            return
        
        # Overview metrics
        st.subheader("📊 Overview Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        current_premium = forecast_df.iloc[0]['average_premium']
        final_premium = forecast_df.iloc[-1]['average_premium']
        change_pct = ((final_premium - current_premium) / current_premium) * 100
        avg_inflation = forecast_df['inflation_rate'].mean()
        
        # Get premium per unit and sum insured if available
        current_premium_per_unit = forecast_df.iloc[0].get('average_premium_per_unit', current_premium / 10.0)
        avg_sum_insured = forecast_df.iloc[0].get('average_sum_insured', filters.get('_display_sum_insured', 10000000))
        
        col1.metric("Current Premium", f"₹{current_premium:,.2f}",
                   help=f"Premium per ₹1L: ₹{current_premium_per_unit:,.2f} | Sum Insured: ₹{avg_sum_insured/100000:.1f}L")
        col2.metric("10-Year Forecast", f"₹{final_premium:,.2f}",
                   help=f"Premium per ₹1L: ₹{forecast_df.iloc[-1].get('average_premium_per_unit', final_premium/10.0):,.2f}")
        col3.metric("Total Change", f"{change_pct:+.1f}%")
        col4.metric("Avg Inflation", f"{avg_inflation:.2f}%")
        
        # Main forecast chart
        st.subheader("📈 Premium Forecast")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast_df['year'],
            y=forecast_df['average_premium'],
            mode='lines+markers',
            name='Average Premium',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        # Get sum insured info for subtitle
        sum_insured_info = ""
        if 'average_sum_insured' in forecast_df.columns:
            avg_si = forecast_df['average_sum_insured'].mean()
            sum_insured_info = f" (Avg Sum Insured: ₹{avg_si/100000:.1f}L)"
        elif filters.get('_display_sum_insured'):
            si = filters['_display_sum_insured']
            sum_insured_info = f" (Sum Insured: ₹{si/100000:.1f}L)"
        
        fig.update_layout(
            title=f"Average Premium Forecast - {selected_scenario.title()} Scenario{sum_insured_info}",
            xaxis_title="Year",
            yaxis_title="Average Premium (₹)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Economic indicators
        st.subheader("💰 Economic Indicators")
        
        fig_econ = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Inflation & Interest Rates', 'GDP Growth', 'Premium Trend', 'Life Expectancy Trend'),
            specs=[[{"secondary_y": True}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Inflation and interest rates
        fig_econ.add_trace(
            go.Scatter(x=forecast_df['year'], y=forecast_df['inflation_rate'],
                      name='Inflation Rate', line=dict(color='#ff7f0e', width=2)),
            row=1, col=1, secondary_y=False
        )
        fig_econ.add_trace(
            go.Scatter(x=forecast_df['year'], y=forecast_df['interest_rate'],
                      name='Interest Rate', line=dict(color='#2ca02c', width=2)),
            row=1, col=1, secondary_y=True
        )
        
        # GDP Growth
        if 'gdp_growth' in forecast_df.columns:
            fig_econ.add_trace(
                go.Scatter(x=forecast_df['year'], y=forecast_df['gdp_growth'],
                          name='GDP Growth', line=dict(color='#9467bd', width=2)),
                row=1, col=2
            )
        
        # Premium trend
        fig_econ.add_trace(
            go.Scatter(x=forecast_df['year'], y=forecast_df['average_premium'],
                      name='Average Premium', line=dict(color='#1f77b4', width=2)),
            row=2, col=1
        )
        
        # Life Expectancy trend
        if 'average_life_expectancy' in forecast_df.columns:
            fig_econ.add_trace(
                go.Scatter(x=forecast_df['year'], y=forecast_df['average_life_expectancy'],
                          name='Avg Life Expectancy', line=dict(color='#8c564b', width=2)),
                row=2, col=2
            )
        else:
            # Fallback if not available
            fig_econ.add_trace(
                go.Scatter(x=forecast_df['year'], y=[0]*len(forecast_df),
                          name='Life Expectancy (N/A)', line=dict(color='#8c564b', width=2),
                          visible='legendonly'),
                row=2, col=2
            )
        
        fig_econ.update_xaxes(title_text="Year", row=1, col=1)
        fig_econ.update_xaxes(title_text="Year", row=1, col=2)
        fig_econ.update_xaxes(title_text="Year", row=2, col=1)
        fig_econ.update_xaxes(title_text="Year", row=2, col=2)
        fig_econ.update_yaxes(title_text="Rate (%)", row=1, col=1, secondary_y=False)
        fig_econ.update_yaxes(title_text="Rate (%)", row=1, col=1, secondary_y=True)
        fig_econ.update_yaxes(title_text="GDP Growth (%)", row=1, col=2)
        fig_econ.update_yaxes(title_text="Premium (₹)", row=2, col=1)
        fig_econ.update_yaxes(title_text="Life Expectancy (years)", row=2, col=2)
        
        fig_econ.update_layout(height=600, showlegend=True, title_text="Economic & Longevity Indicators")
        st.plotly_chart(fig_econ, use_container_width=True)
        
        # Mortality & Longevity Trends
        if 'average_mortality_rate' in forecast_df.columns and 'average_life_expectancy' in forecast_df.columns:
            st.subheader("📉 Mortality & Longevity Trends")
            
            fig_longevity = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Mortality Rate Trend', 'Life Expectancy Trend'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            fig_longevity.add_trace(
                go.Scatter(x=forecast_df['year'], y=forecast_df['average_mortality_rate'],
                          name='Mortality Rate (per 1000)', line=dict(color='#d62728', width=2),
                          mode='lines+markers'),
                row=1, col=1
            )
            
            fig_longevity.add_trace(
                go.Scatter(x=forecast_df['year'], y=forecast_df['average_life_expectancy'],
                          name='Life Expectancy (years)', line=dict(color='#2ca02c', width=2),
                          mode='lines+markers'),
                row=1, col=2
            )
            
            fig_longevity.update_xaxes(title_text="Year", row=1, col=1)
            fig_longevity.update_xaxes(title_text="Year", row=1, col=2)
            fig_longevity.update_yaxes(title_text="Mortality Rate (per 1000)", row=1, col=1)
            fig_longevity.update_yaxes(title_text="Life Expectancy (years)", row=1, col=2)
            
            fig_longevity.update_layout(height=400, showlegend=True, 
                                      title_text="Longevity Improvements: Lower Mortality, Higher Life Expectancy")
            st.plotly_chart(fig_longevity, use_container_width=True)
            
            # Key insight
            mortality_change = ((forecast_df.iloc[-1]['average_mortality_rate'] - 
                               forecast_df.iloc[0]['average_mortality_rate']) / 
                              forecast_df.iloc[0]['average_mortality_rate']) * 100
            life_exp_change = forecast_df.iloc[-1]['average_life_expectancy'] - forecast_df.iloc[0]['average_life_expectancy']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Mortality Rate Change", f"{mortality_change:+.1f}%", 
                         help="Negative means improving mortality (good)")
            with col2:
                st.metric("Life Expectancy Increase", f"+{life_exp_change:.1f} years",
                         help="Increase in average remaining life expectancy")
        
        # AI Insights - Enhanced
        if st.session_state.insights_generator:
            st.subheader("🤖 AI-Powered Insights")
            
            # Key Metrics
            with st.expander("📊 Key Metrics", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Premium", f"₹{current_premium:,.2f}")
                with col2:
                    st.metric("10-Year Forecast", f"₹{final_premium:,.2f}")
                with col3:
                    st.metric("Total Change", f"{change_pct:+.1f}%")
                with col4:
                    st.metric("Avg Inflation", f"{avg_inflation:.2f}%")
            
            # Forecast Summary
            with st.expander("📝 Forecast Summary", expanded=True):
                with st.spinner("Generating forecast analysis..."):
                    summary = st.session_state.insights_generator.generate_forecast_summary(
                        forecast_df, selected_scenario
                    )
                    st.markdown(summary)
            
            # Driver Analysis
            with st.expander("🔍 Driver Impact Analysis", expanded=False):
                driver_impact = st.session_state.insights_generator.calculate_driver_impact(forecast_df)
                
                if driver_impact and 'drivers' in driver_impact:
                    st.markdown(f"**Total Premium Change: {driver_impact['total_premium_change_pct']:+.1f}%**")
                    st.markdown("### Factor Impact on Premiums")
                    
                    for driver_name, driver_data in driver_impact['drivers'].items():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{driver_name.replace('_', ' ').title()}**")
                        with col2:
                            corr = driver_data['correlation']
                            st.write(f"Correlation: {corr:+.2f}")
                        with col3:
                            impact_level = driver_data['impact']
                            color = "🔴" if impact_level == "High" else "🟡" if impact_level == "Medium" else "🟢"
                            st.write(f"{color} {impact_level} Impact")
                
                # Also show detailed driver analysis
                with st.spinner("Analyzing drivers..."):
                    driver_analysis = st.session_state.insights_generator.generate_driver_analysis(
                        forecast_df, selected_scenario, filters
                    )
                    st.markdown(driver_analysis)
            
            # Recommendations
            with st.expander("💡 Recommendations", expanded=False):
                with st.spinner("Generating recommendations..."):
                    # Create a comparison df with just this scenario for recommendations
                    single_scenario_df = forecast_df.copy()
                    recommendations = st.session_state.insights_generator.generate_recommendations(single_scenario_df, filters)
                    
                    if isinstance(recommendations, dict):
                        st.markdown(recommendations.get('recommendations', 'Recommendations not available'))
                    else:
                        st.write(recommendations)
        
        # Comprehensive Data Table
        st.subheader("📊 Comprehensive Data Table")
        st.markdown("**All data from CSVs filtered by your selections**")
        
        # Get raw data
        mortality_df, economic_df, base_premium_df, demographic_df = load_data()
        
        # Prepare filtered data table
        filtered_table = prepare_filtered_data_table(
            mortality_df, economic_df, base_premium_df, demographic_df,
            start_year, end_year, filters, selected_country, selected_scenario
        )
        
        if not filtered_table.empty:
            # Sort by year, age, gender
            sort_cols = ['year', 'age', 'gender', 'group', 'policy_type']
            if 'smoking_status' in filtered_table.columns:
                sort_cols.insert(-1, 'smoking_status')
            filtered_table = filtered_table.sort_values(sort_cols)
            
            # Format numeric columns for display
            display_table = filtered_table.copy()
            
            # Format premium columns
            if 'base_premium' in display_table.columns:
                display_table['base_premium'] = display_table['base_premium'].apply(lambda x: f"₹{x:,.2f}")
            if 'premium_per_unit' in display_table.columns:
                display_table['premium_per_unit'] = display_table['premium_per_unit'].apply(lambda x: f"₹{x:,.2f}")
            if 'sum_insured' in display_table.columns:
                display_table['sum_insured'] = display_table['sum_insured'].apply(lambda x: f"₹{x/100000:.1f}L" if x < 10000000 else f"₹{x/10000000:.1f}Cr")
            
            display_table['mortality_rate'] = display_table['mortality_rate'].apply(lambda x: f"{x:.4f}")
            display_table['life_expectancy'] = display_table['life_expectancy'].apply(lambda x: f"{x:.1f}")
            display_table['inflation_rate'] = display_table['inflation_rate'].apply(lambda x: f"{x:.2f}%")
            display_table['interest_rate'] = display_table['interest_rate'].apply(lambda x: f"{x:.2f}%")
            display_table['gdp_growth'] = display_table['gdp_growth'].apply(lambda x: f"{x:.2f}%")
            
            st.dataframe(display_table, use_container_width=True, height=400)
            
            # Download button
            csv = filtered_table.to_csv(index=False)
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"premium_forecast_data_{selected_scenario}_{start_year}_{end_year}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data available for the selected filters.")
        
        # Summary forecast data table (existing)
        with st.expander("📋 Summary Forecast Data (Aggregated)", expanded=False):
            st.dataframe(forecast_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p><strong>Life Insurance Premium Forecasting Dashboard</strong></p>
            <p>Forecasting premiums by combining longevity, mortality trends, and economic indicators</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
