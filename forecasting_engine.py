"""
Forecasting engine for life insurance premiums.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from data_models import Gender, PolicyType


@dataclass
class Scenario:
    """Economic scenario definition"""
    name: str
    inflation_base: float  # Base inflation rate (%)
    interest_base: float  # Base interest rate (%)
    mortality_improvement: float  # Annual mortality improvement (%)
    description: str


class PremiumForecaster:
    """Main forecasting engine for life insurance premiums"""
    
    def __init__(self, mortality_df: pd.DataFrame, economic_df: pd.DataFrame, 
                 base_premium_df: pd.DataFrame, demographic_df: pd.DataFrame):
        self.mortality_df = mortality_df
        self.economic_df = economic_df
        self.base_premium_df = base_premium_df
        self.demographic_df = demographic_df
        
        # Standard scenarios (India-specific)
        self.scenarios = {
            'base': Scenario(
                name='Base Case',
                inflation_base=5.0,  # India: Moderate inflation
                interest_base=6.5,   # India: RBI repo rate range
                mortality_improvement=1.5,
                description='Moderate inflation, stable interest rates, normal mortality improvements'
            ),
            'optimistic': Scenario(
                name='Optimistic',
                inflation_base=4.0,  # India: Lower inflation
                interest_base=7.5,   # India: Higher rates
                mortality_improvement=2.0,
                description='Low inflation, higher interest rates, faster mortality improvements'
            ),
            'pessimistic': Scenario(
                name='Pessimistic',
                inflation_base=6.0,  # India: Higher inflation
                interest_base=5.5,   # India: Lower rates
                mortality_improvement=1.0,
                description='High inflation, lower interest rates, slower mortality improvements'
            )
        }
    
    def project_mortality(self, start_year: int, end_year: int, 
                         scenario: Scenario, country: str = "India") -> pd.DataFrame:
        """Project mortality rates into the future"""
        # Check if mortality_df is empty
        if self.mortality_df.empty:
            raise ValueError("Mortality DataFrame is empty. Please check data initialization.")
        
        # Check available countries
        available_countries = self.mortality_df['country'].unique()
        if country not in available_countries:
            raise ValueError(f"Country '{country}' not found in mortality data. Available countries: {list(available_countries)}")
        
        # Get latest historical data
        latest_year = self.mortality_df['year'].max()
        latest_data_filtered = self.mortality_df[
            (self.mortality_df['year'] == latest_year) & 
            (self.mortality_df['country'] == country)
        ].copy()
        
        if latest_data_filtered.empty:
            # Fallback: use any data for the country
            country_data = self.mortality_df[self.mortality_df['country'] == country]
            if country_data.empty:
                raise ValueError(f"No mortality data available for country: {country}. Available countries: {list(available_countries)}")
            # Use most recent available data for the country
            latest_year_available = country_data['year'].max()
            latest_data = country_data[country_data['year'] == latest_year_available].copy()
            latest_year = latest_year_available
        else:
            latest_data = latest_data_filtered
        
        projections = []
        
        for year in range(start_year, end_year + 1):
            years_ahead = year - latest_year
            
            for _, row in latest_data.iterrows():
                # Apply mortality improvement (annual reduction in mortality rate)
                improvement_factor = ((100 - scenario.mortality_improvement) / 100) ** years_ahead
                projected_mortality = row['mortality_rate'] * improvement_factor
                
                # Update life expectancy (increases with mortality improvement)
                life_expectancy_increase = years_ahead * (scenario.mortality_improvement / 100)
                projected_life_expectancy = row['life_expectancy'] + life_expectancy_increase
                
                projection_record = {
                    'year': year,
                    'country': country,
                    'gender': row['gender'],
                    'age': row['age'],
                    'mortality_rate': round(projected_mortality, 4),
                    'life_expectancy': round(projected_life_expectancy, 2)
                }
                
                # Include smoking_status if available
                if 'smoking_status' in row:
                    projection_record['smoking_status'] = row['smoking_status']
                
                projections.append(projection_record)
        
        return pd.DataFrame(projections)
    
    def project_economics(self, start_year: int, end_year: int, 
                         scenario: Scenario, country: str = "India") -> pd.DataFrame:
        """Project economic indicators into the future"""
        # Get latest historical data
        latest_year = self.economic_df['year'].max()
        latest_data_filtered = self.economic_df[
            (self.economic_df['year'] == latest_year) & 
            (self.economic_df['country'] == country)
        ]
        
        if latest_data_filtered.empty:
            # Fallback: use any data for the country, or create default values
            country_data = self.economic_df[self.economic_df['country'] == country]
            if country_data.empty:
                # No data for country, use default India values
                latest_data = pd.Series({
                    'inflation_rate': 5.0,
                    'interest_rate': 6.5,
                    'gdp_growth': 6.5
                })
            else:
                latest_data = country_data.iloc[-1]  # Use most recent available
        else:
            latest_data = latest_data_filtered.iloc[0]
        
        projections = []
        np.random.seed(42)
        
        for year in range(start_year, end_year + 1):
            years_ahead = year - latest_year
            
            # Converge towards scenario targets with some volatility
            convergence_factor = 1 - np.exp(-years_ahead / 5)  # Gradually converge
            
            inflation = (latest_data['inflation_rate'] * (1 - convergence_factor) + 
                        scenario.inflation_base * convergence_factor)
            inflation += np.random.normal(0, 0.3) * (1 - convergence_factor)
            
            interest = (latest_data['interest_rate'] * (1 - convergence_factor) + 
                       scenario.interest_base * convergence_factor)
            interest += np.random.normal(0, 0.3) * (1 - convergence_factor)
            
            # GDP growth tends to correlate with scenario
            gdp = scenario.inflation_base * 0.8 + np.random.normal(0, 0.5)
            
            projections.append({
                'year': year,
                'country': country,
                'inflation_rate': round(max(0.5, inflation), 2),
                'interest_rate': round(max(0.5, interest), 2),
                'gdp_growth': round(gdp, 2)
            })
        
        return pd.DataFrame(projections)
    
    def calculate_premiums(self, year: int, mortality_proj: pd.DataFrame, 
                          economic_proj: pd.DataFrame, country: str = "India",
                          economic_proj_full: pd.DataFrame = None) -> pd.DataFrame:
        """Calculate premiums for a given year"""
        # Check if mortality_proj is empty or missing 'year' column
        if mortality_proj.empty or 'year' not in mortality_proj.columns:
            raise ValueError(f"Invalid mortality projection data for year {year}")
        
        year_mortality = mortality_proj[mortality_proj['year'] == year]
        year_economic_filtered = economic_proj[economic_proj['year'] == year]
        
        if year_economic_filtered.empty:
            raise ValueError(f"No economic data available for year {year}")
        
        year_economic = year_economic_filtered.iloc[0]
        
        premiums = []
        
        # Filter base premiums by country
        base_premiums_filtered = self.base_premium_df[
            self.base_premium_df['country'] == country
        ].copy()
        
        # Merge with base premiums
        for _, base_row in base_premiums_filtered.iterrows():
            # Get corresponding mortality data (match on age, gender, and smoking_status)
            mortality_filter = (year_mortality['age'] == base_row['age']) & \
                             (year_mortality['gender'] == base_row['gender'])
            
            # Include smoking_status if available in both dataframes
            if 'smoking_status' in base_row and 'smoking_status' in year_mortality.columns:
                mortality_filter = mortality_filter & (year_mortality['smoking_status'] == base_row['smoking_status'])
            
            mortality_row = year_mortality[mortality_filter]
            
            if mortality_row.empty:
                continue
            
            mortality_row = mortality_row.iloc[0]
            
            # Get premium per unit (per ₹1 lakh sum insured)
            # If premium_per_unit exists, use it; otherwise convert base_premium (legacy support)
            if 'premium_per_unit' in base_row:
                premium_per_unit = base_row['premium_per_unit']
            elif 'base_premium' in base_row:
                # Legacy: assume base_premium is for ₹10 lakh coverage (convert to per unit)
                premium_per_unit = base_row['base_premium'] / 10.0
            else:
                continue  # Skip if neither column exists
            
            # Store premium_per_unit - actual premium will be calculated when we have sum_insured
            premium = premium_per_unit  # This is premium per ₹1 lakh
            
            # Get base year economic data for cumulative inflation calculation
            base_year = self.economic_df['year'].max()
            base_year_economic = self.economic_df[
                self.economic_df['year'] == base_year
            ].iloc[0]
            
            # Calculate cumulative inflation from base year to current year
            # This represents the compound effect of inflation over time
            years_from_base = year - base_year
            if years_from_base > 0 and economic_proj_full is not None:
                # Get all economic data from base year to current year
                economic_history = economic_proj_full[
                    (economic_proj_full['year'] >= base_year) & 
                    (economic_proj_full['year'] <= year)
                ].sort_values('year')
                
                # Compound inflation: (1 + i1) * (1 + i2) * ... * (1 + in)
                cumulative_inflation = 1.0
                for _, econ_row in economic_history.iterrows():
                    cumulative_inflation *= (1 + econ_row['inflation_rate'] / 100)
            else:
                cumulative_inflation = 1.0
            
            # Apply cumulative inflation to base premium
            premium *= cumulative_inflation
            
            # Mortality adjustment: higher mortality → higher premium
            # But mortality improvements reduce risk, so this is a smaller effect
            base_mortality_filter = (self.mortality_df['year'] == self.mortality_df['year'].max()) & \
                                   (self.mortality_df['age'] == base_row['age']) & \
                                   (self.mortality_df['gender'] == base_row['gender']) & \
                                   (self.mortality_df['country'] == country)
            
            # Include smoking_status if available
            if 'smoking_status' in base_row and 'smoking_status' in self.mortality_df.columns:
                base_mortality_filter = base_mortality_filter & \
                                       (self.mortality_df['smoking_status'] == base_row['smoking_status'])
            
            base_mortality = self.mortality_df[base_mortality_filter]['mortality_rate'].values
            
            if len(base_mortality) > 0:
                mortality_factor = mortality_row['mortality_rate'] / base_mortality[0]
                # Mortality improvements reduce premiums slightly (0.3 factor, not 0.5)
                # This accounts for improved longevity reducing annual risk
                premium *= (1 + (mortality_factor - 1) * 0.3)
            
            # Longevity impact: People living longer → different effects by policy type
            # Term Life: Longer life expectancy → lower annual risk → reduces premium
            # Whole Life: Longer life expectancy → longer policy exposure → increases premium (net effect)
            base_life_exp_filter = (self.mortality_df['year'] == self.mortality_df['year'].max()) & \
                                  (self.mortality_df['age'] == base_row['age']) & \
                                  (self.mortality_df['gender'] == base_row['gender']) & \
                                  (self.mortality_df['country'] == country)
            
            # Include smoking_status if available
            if 'smoking_status' in base_row and 'smoking_status' in self.mortality_df.columns:
                base_life_exp_filter = base_life_exp_filter & \
                                      (self.mortality_df['smoking_status'] == base_row['smoking_status'])
            
            base_life_expectancy = self.mortality_df[base_life_exp_filter]['life_expectancy'].values
            
            if len(base_life_expectancy) > 0:
                life_expectancy_change = mortality_row['life_expectancy'] - base_life_expectancy[0]
                if base_row['policy_type'] == 'Term Life':
                    # Term Life: Longer life expectancy reduces annual mortality risk
                    # Small positive effect: 1 year increase → ~0.5% premium decrease
                    longevity_adj = -0.005 * life_expectancy_change
                else:  # Whole Life
                    # Whole Life: Longer life expectancy increases policy exposure duration
                    # Net effect: 1 year increase → ~0.3% premium increase (longer exposure outweighs lower annual risk)
                    longevity_adj = 0.003 * life_expectancy_change
                premium *= (1 + longevity_adj)
            
            # Interest rate adjustment: higher rates reduce present value of future claims
            # But this effect is smaller than inflation (typically 0.1-0.15 multiplier)
            # Also, higher rates allow insurers to invest premiums more effectively
            base_interest = base_year_economic['interest_rate']
            interest_change = year_economic['interest_rate'] - base_interest
            # Small adjustment: -0.12 means 1% interest increase → 0.12% premium decrease
            interest_adj = -0.12 * (interest_change / 100)
            premium *= (1 + interest_adj)
            
            # GDP growth adjustment: Higher GDP → economic stability → better mortality improvements
            # Also correlates with overall economic health affecting insurance costs
            # GDP growth above baseline can slightly reduce premiums (economic efficiency)
            base_gdp = base_year_economic.get('gdp_growth', 6.0)
            gdp_change = year_economic.get('gdp_growth', 6.0) - base_gdp
            # Small adjustment: 1% GDP increase above baseline → ~0.05% premium decrease
            gdp_adj = -0.05 * (gdp_change / 100)
            premium *= (1 + gdp_adj)
            
            premium_record = {
                'year': year,
                'country': country,
                'group': base_row.get('group', 'Individual'),  # Include group
                'gender': base_row['gender'],
                'age': base_row['age'],
                'policy_type': base_row['policy_type'],
                'premium_per_unit': round(premium, 2),  # Premium per ₹1 lakh sum insured
                'mortality_rate': mortality_row['mortality_rate'],
                'life_expectancy': mortality_row['life_expectancy'],
                'inflation_rate': year_economic['inflation_rate'],
                'interest_rate': year_economic['interest_rate'],
                'gdp_growth': year_economic.get('gdp_growth', 6.0)
            }
            
            # Include smoking_status if available
            if 'smoking_status' in base_row:
                premium_record['smoking_status'] = base_row['smoking_status']
            
            premiums.append(premium_record)
        
        return pd.DataFrame(premiums)
    
    def forecast_average_premium(self, start_year: int, end_year: int, 
                                 scenario_name: str = 'base',
                                 country: str = "India",
                                 filters: Optional[Dict] = None) -> pd.DataFrame:
        """Forecast average premiums over time"""
        scenario = self.scenarios[scenario_name]
        
        # Project mortality and economics
        mortality_proj = self.project_mortality(start_year, end_year, scenario, country)
        economic_proj = self.project_economics(start_year, end_year, scenario, country)
        
        # Calculate premiums for each year
        # Pass full economic projection for cumulative inflation calculation
        all_premiums = []
        for year in range(start_year, end_year + 1):
            year_premiums = self.calculate_premiums(year, mortality_proj, economic_proj, country, economic_proj)
            all_premiums.append(year_premiums)
        
        premiums_df = pd.concat(all_premiums, ignore_index=True)
        
        # Apply filters if provided
        if filters:
            if 'gender' in filters and filters['gender']:
                premiums_df = premiums_df[premiums_df['gender'] == filters['gender']]
            if 'policy_type' in filters and filters['policy_type']:
                premiums_df = premiums_df[premiums_df['policy_type'] == filters['policy_type']]
            if 'group' in filters and filters['group']:
                premiums_df = premiums_df[premiums_df['group'] == filters['group']]
            if 'smoking_status' in filters and filters['smoking_status']:
                premiums_df = premiums_df[premiums_df['smoking_status'] == filters['smoking_status']]
            if 'age_min' in filters:
                premiums_df = premiums_df[premiums_df['age'] >= filters['age_min']]
            if 'age_max' in filters:
                premiums_df = premiums_df[premiums_df['age'] <= filters['age_max']]
        
        # Calculate weighted average by demographic distribution
        # Merge with demographic data
        demo_filtered = self.demographic_df[
            self.demographic_df['country'] == country
        ].copy()
        
        if filters:
            if 'gender' in filters and filters['gender']:
                demo_filtered = demo_filtered[demo_filtered['gender'] == filters['gender']]
            if 'policy_type' in filters and filters['policy_type']:
                demo_filtered = demo_filtered[demo_filtered['policy_type'] == filters['policy_type']]
            if 'group' in filters and filters['group']:
                demo_filtered = demo_filtered[demo_filtered['group'] == filters['group']]
            if 'smoking_status' in filters and filters['smoking_status']:
                demo_filtered = demo_filtered[demo_filtered['smoking_status'] == filters['smoking_status']]
            if 'age_min' in filters:
                demo_filtered = demo_filtered[demo_filtered['age'] >= filters['age_min']]
            if 'age_max' in filters:
                demo_filtered = demo_filtered[demo_filtered['age'] <= filters['age_max']]
        
        # Aggregate by year
        forecast_results = []
        for year in range(start_year, end_year + 1):
            year_premiums = premiums_df[premiums_df['year'] == year]
            year_demo = demo_filtered.copy()
            
            # Merge premiums with demographics (include group, smoking_status, and sum_insured)
            merge_cols = ['country', 'gender', 'age', 'policy_type']
            if 'group' in year_premiums.columns and 'group' in year_demo.columns:
                merge_cols.append('group')
            if 'smoking_status' in year_premiums.columns and 'smoking_status' in year_demo.columns:
                merge_cols.append('smoking_status')
            # Note: sum_insured is NOT in merge_cols because premium_per_unit doesn't vary by sum_insured
            # We filter by sum_insured in demo_filtered above, so merged will only have the filtered sum_insured
            merged = year_premiums.merge(
                year_demo,
                on=merge_cols,
                how='inner'
            )
            
            # Additional filter: if sum_insured filter was applied, ensure we only have that sum_insured
            if filters and 'sum_insured' in filters and filters['sum_insured']:
                if 'sum_insured' in merged.columns:
                    merged = merged[merged['sum_insured'] == filters['sum_insured']]
            
            if not merged.empty:
                # Calculate actual premium: premium_per_unit × (sum_insured / 100000)
                # Handle both premium_per_unit (new) and premium (legacy) columns
                if 'premium_per_unit' in merged.columns:
                    # New format: multiply by sum_insured
                    if 'sum_insured' in merged.columns:
                        merged['premium'] = merged['premium_per_unit'] * (merged['sum_insured'] / 100000.0)
                    else:
                        # If no sum_insured, use default of ₹10 lakh
                        merged['premium'] = merged['premium_per_unit'] * 10.0
                elif 'premium' not in merged.columns:
                    # Fallback: create premium from premium_per_unit if it exists
                    if 'premium_per_unit' in merged.columns:
                        merged['premium'] = merged['premium_per_unit'] * 10.0  # Default ₹10 lakh
                
                # Weighted average premium (actual premium, not per unit)
                total_premium = (merged['premium'] * merged['policy_count']).sum()
                total_policies = merged['policy_count'].sum()
                avg_premium = total_premium / total_policies if total_policies > 0 else 0
                
                # Also calculate average premium per unit for comparison
                if 'premium_per_unit' in merged.columns:
                    avg_premium_per_unit = (merged['premium_per_unit'] * merged['policy_count']).sum() / total_policies if total_policies > 0 else 0
                else:
                    avg_premium_per_unit = avg_premium / 10.0  # Assume ₹10 lakh if not available
                
                # Also get average economic indicators and longevity metrics
                year_econ_filtered = economic_proj[economic_proj['year'] == year]
                if year_econ_filtered.empty:
                    continue  # Skip this year if no economic data
                year_econ = year_econ_filtered.iloc[0]
                
                # Calculate average life expectancy and mortality rate for the year
                avg_life_expectancy = merged['life_expectancy'].mean() if 'life_expectancy' in merged.columns else 0
                avg_mortality_rate = merged['mortality_rate'].mean() if 'mortality_rate' in merged.columns else 0
                
                result_record = {
                    'year': year,
                    'scenario': scenario_name,
                    'average_premium': round(avg_premium, 2),  # Total premium (weighted by sum_insured)
                    'average_premium_per_unit': round(avg_premium_per_unit, 2),  # Premium per ₹1 lakh
                    'total_policies': int(total_policies),
                    'inflation_rate': year_econ['inflation_rate'],
                    'interest_rate': year_econ['interest_rate'],
                    'gdp_growth': year_econ.get('gdp_growth', 6.0),
                    'average_life_expectancy': round(avg_life_expectancy, 1),
                    'average_mortality_rate': round(avg_mortality_rate, 4)
                }
                
                # Include average sum insured if available
                if 'sum_insured' in merged.columns:
                    result_record['average_sum_insured'] = round((merged['sum_insured'] * merged['policy_count']).sum() / total_policies, 0) if total_policies > 0 else 0
                
                forecast_results.append(result_record)
        
        return pd.DataFrame(forecast_results)
    
    def compare_scenarios(self, start_year: int, end_year: int,
                         country: str = "India",
                         filters: Optional[Dict] = None) -> pd.DataFrame:
        """Compare premiums across different scenarios"""
        all_results = []
        
        for scenario_name in self.scenarios.keys():
            try:
                results = self.forecast_average_premium(
                    start_year, end_year, scenario_name, country, filters
                )
                if not results.empty and 'scenario' in results.columns:
                    all_results.append(results)
            except Exception as e:
                # Log error but continue with other scenarios
                print(f"Warning: Failed to forecast for scenario '{scenario_name}': {str(e)}")
                continue
        
        if not all_results:
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=['year', 'scenario', 'average_premium', 'total_policies',
                                        'inflation_rate', 'interest_rate', 'gdp_growth',
                                        'average_life_expectancy', 'average_mortality_rate'])
        
        return pd.concat(all_results, ignore_index=True)
