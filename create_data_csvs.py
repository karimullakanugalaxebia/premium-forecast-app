"""
Script to generate realistic CSV data files for India life insurance premium forecasting.
"""
import pandas as pd
import numpy as np
from datetime import datetime

# Set seed for reproducibility
np.random.seed(42)

print("Generating realistic data for India...")

# 1. Generate Mortality Data (2014-2024)
print("1. Generating mortality data...")
mortality_data = []
years = list(range(2014, 2025))
ages = list(range(20, 81, 5))
genders = ['Male', 'Female']
smoking_statuses = ['Smoker', 'Non-Smoker']

# India-specific mortality rates (per 1000) - realistic values
# Base mortality increases with age, higher for males, much higher for smokers
for year in years:
    for gender in genders:
        for age in ages:
            for smoking_status in smoking_statuses:
                # Base mortality rate (higher for males, increases with age)
                if gender == 'Male':
                    base_rate = 0.8 * (1.12 ** ((age - 20) / 10))
                else:
                    base_rate = 0.6 * (1.10 ** ((age - 20) / 10))
                
                # Smoking multiplier: Smokers have 2.5-3x higher mortality
                if smoking_status == 'Smoker':
                    smoking_multiplier = 2.5 + (age - 20) * 0.02  # Higher multiplier for older smokers
                else:
                    smoking_multiplier = 1.0
                
                # India-specific adjustment (higher mortality than developed countries)
                india_multiplier = 1.15
                
                # Mortality improvement over time (1-2% annual reduction)
                years_from_2014 = year - 2014
                improvement = (0.985 ** years_from_2014)
                
                mortality_rate = base_rate * smoking_multiplier * india_multiplier * improvement
                
                # Life expectancy calculation (India-specific)
                # Smokers have 8-12 years lower life expectancy
                if gender == 'Male':
                    base_life_exp = max(68 - age, 0) * 0.95
                else:
                    base_life_exp = max(70 - age, 0) * 0.95
                
                # Smoking reduces life expectancy
                if smoking_status == 'Smoker':
                    life_expectancy_reduction = 10 - (age - 20) * 0.1  # More impact at younger ages
                    base_life_exp = max(0, base_life_exp - life_expectancy_reduction)
                
                # Improving over time
                life_expectancy = base_life_exp + (years_from_2014 * 0.15)
                
                mortality_data.append({
                    'year': year,
                    'country': 'India',
                    'gender': gender,
                    'age': age,
                    'smoking_status': smoking_status,
                    'mortality_rate': round(mortality_rate, 4),
                    'life_expectancy': round(max(life_expectancy, 0), 1)
                })

mortality_df = pd.DataFrame(mortality_data)
mortality_df.to_csv('data/mortality_data.csv', index=False)
print(f"   Created mortality_data.csv with {len(mortality_df)} rows")

# 2. Generate Economic Data (2014-2024) - India-specific
print("2. Generating economic data...")
economic_data = []

# India's historical economic indicators (realistic ranges)
# Inflation: 4-7% (RBI target: 4% with +/- 2%)
# Interest rates: 5-8% (RBI repo rate range)
# GDP growth: 5-8%

base_inflation_2014 = 6.0
base_interest_2014 = 7.0
base_gdp_2014 = 7.0

for year in years:
    years_from_2014 = year - 2014
    
    # Inflation trends (volatile, but generally decreasing)
    inflation = base_inflation_2014 - (years_from_2014 * 0.15) + np.random.normal(0, 0.8)
    inflation = max(3.5, min(7.5, inflation))
    
    # Interest rates (following inflation trends)
    interest = base_interest_2014 - (years_from_2014 * 0.12) + np.random.normal(0, 0.6)
    interest = max(4.5, min(8.5, interest))
    
    # GDP growth (slight decline over time, but still strong)
    gdp = base_gdp_2014 - (years_from_2014 * 0.08) + np.random.normal(0, 0.5)
    gdp = max(5.0, min(8.5, gdp))
    
    economic_data.append({
        'year': year,
        'country': 'India',
        'inflation_rate': round(inflation, 2),
        'interest_rate': round(interest, 2),
        'gdp_growth': round(gdp, 2)
    })

economic_df = pd.DataFrame(economic_data)
economic_df.to_csv('data/economic_data.csv', index=False)
print(f"   Created economic_data.csv with {len(economic_df)} rows")

# 3. Generate Base Premiums (Premium per 1 Lakh Sum Insured)
print("3. Generating base premiums (premium per 1 lakh sum insured)...")
premium_data = []

groups = ['Individual', 'Family', 'Corporate']
policy_types = ['Term Life', 'Whole Life']
smoking_statuses = ['Smoker', 'Non-Smoker']

# Base premium rates per ₹1 lakh sum insured (realistic for India)
# These represent annual premium per ₹1 lakh coverage
base_term_premium_rate = 50  # ₹50 per ₹1 lakh per year for Term Life (age 25, male, non-smoker)
base_whole_premium_rate = 200  # ₹200 per ₹1 lakh per year for Whole Life (age 25, male, non-smoker)

for group in groups:
    for gender in genders:
        for age in ages:
            for policy_type in policy_types:
                for smoking_status in smoking_statuses:
                    # Age factor (exponential increase with age)
                    # Premium increases significantly with age due to higher mortality risk
                    age_factor = 1.08 ** ((age - 25) / 5)  # 8% increase per 5 years
                    
                    # Gender factor (males pay more due to higher mortality)
                    gender_factor = 1.20 if gender == 'Male' else 1.0
                    
                    # Smoking factor: Smokers pay 2.5-3x more (industry standard)
                    if smoking_status == 'Smoker':
                        smoking_factor = 2.5 + (age - 20) * 0.015  # Higher multiplier for older smokers
                    else:
                        smoking_factor = 1.0
                    
                    # Group factor (volume discounts)
                    group_factors = {
                        'Individual': 1.0,
                        'Family': 0.92,  # Family discount (8% off)
                        'Corporate': 0.80  # Corporate volume discount (20% off)
                    }
                    group_factor = group_factors[group]
                    
                    # Policy type base rate
                    if policy_type == 'Term Life':
                        base_rate = base_term_premium_rate
                    else:
                        base_rate = base_whole_premium_rate
                    
                    # Calculate premium per ₹1 lakh sum insured
                    premium_per_unit = base_rate * age_factor * gender_factor * smoking_factor * group_factor
                    
                    premium_data.append({
                        'country': 'India',
                        'group': group,
                        'gender': gender,
                        'age': age,
                        'policy_type': policy_type,
                        'smoking_status': smoking_status,
                        'premium_per_unit': round(premium_per_unit, 2)  # Premium per ₹1 lakh
                    })

premium_df = pd.DataFrame(premium_data)
premium_df.to_csv('data/base_premiums.csv', index=False)
print(f"   Created base_premiums.csv with {len(premium_df)} rows")

# 4. Generate Demographic Distribution
print("4. Generating demographic distribution...")
demographic_data = []

total_policies = 100000

# India-specific distribution
group_distribution = {
    'Individual': 0.62,
    'Family': 0.23,
    'Corporate': 0.15
}

gender_distribution = {
    'Male': 0.58,
    'Female': 0.42
}

# Age groups with realistic distribution (more policies in middle ages)
age_distribution = {
    (20, 30): 0.18,
    (31, 40): 0.25,
    (41, 50): 0.22,
    (51, 60): 0.18,
    (61, 70): 0.12,
    (71, 80): 0.05
}

policy_type_distribution = {
    'Term Life': 0.72,
    'Whole Life': 0.28
}

# Smoking status distribution (India-specific: ~20% smokers)
smoking_distribution = {
    'Smoker': 0.20,
    'Non-Smoker': 0.80
}

# Sum Insured distribution (India-specific: coverage amounts)
# Common sum insured amounts: 10L, 25L, 50L, 1Cr, 2Cr
sum_insured_options = [1000000, 2500000, 5000000, 10000000, 20000000]  # 10L, 25L, 50L, 1Cr, 2Cr
sum_insured_distribution = {
    1000000: 0.25,   # 25% have 10L coverage
    2500000: 0.30,   # 30% have 25L coverage
    5000000: 0.25,   # 25% have 50L coverage
    10000000: 0.15,  # 15% have 1Cr coverage
    20000000: 0.05   # 5% have 2Cr coverage
}

np.random.seed(42)
for group in groups:
    group_policies = int(total_policies * group_distribution[group])
    
    for gender in genders:
        gender_policies = int(group_policies * gender_distribution[gender])
        
        for age_range, age_share in age_distribution.items():
            age_policies = int(gender_policies * age_share)
            
            for policy_type in policy_types:
                policy_count = int(age_policies * policy_type_distribution[policy_type])
                
                # Distribute across ages in the range
                ages_in_range = list(range(age_range[0], min(age_range[1] + 1, 81)))
                if len(ages_in_range) > 0:
                    policies_per_age = max(1, policy_count // len(ages_in_range))
                    
                    for age in ages_in_range:
                        # Distribute between smokers and non-smokers
                        for smoking_status in smoking_statuses:
                            smoking_count = int(policies_per_age * smoking_distribution[smoking_status])
                            
                            # Distribute across sum insured amounts
                            for sum_insured in sum_insured_options:
                                sum_insured_count = int(smoking_count * sum_insured_distribution[sum_insured])
                                
                                # Add some randomness
                                final_count = int(sum_insured_count * np.random.uniform(0.9, 1.1))
                                final_count = max(1, final_count)
                                
                                demographic_data.append({
                                    'country': 'India',
                                    'group': group,
                                    'gender': gender,
                                    'age': age,
                                    'policy_type': policy_type,
                                    'smoking_status': smoking_status,
                                    'sum_insured': sum_insured,
                                    'policy_count': final_count
                                })

demographic_df = pd.DataFrame(demographic_data)

# Normalize to approximately total_policies
scale_factor = total_policies / demographic_df['policy_count'].sum()
demographic_df['policy_count'] = (demographic_df['policy_count'] * scale_factor).astype(int)

demographic_df.to_csv('data/demographic_distribution.csv', index=False)
print(f"   Created demographic_distribution.csv with {len(demographic_df)} rows")
print(f"   Total policies: {demographic_df['policy_count'].sum()}")

print("\nAll CSV files created successfully in 'data/' directory!")
print("\nFiles created:")
print("  - data/mortality_data.csv")
print("  - data/economic_data.csv")
print("  - data/base_premiums.csv")
print("  - data/demographic_distribution.csv")
