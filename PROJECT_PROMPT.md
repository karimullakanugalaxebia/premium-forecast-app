# Life Insurance Premium Forecasting Dashboard - Project Prompt

## Project Overview

Build an AI-powered dashboard that forecasts average life insurance premiums over the next 10 years by analyzing multiple interconnected factors including mortality trends, longevity data, economic indicators, and customer demographics.

## Core Objectives

1. **Forecast Life Insurance Premiums**: Predict average premiums for the next decade (2024-2034)
2. **Multi-Factor Analysis**: Integrate mortality, longevity, economic, and demographic data
3. **Scenario Planning**: Visualize how premiums evolve under different scenarios
4. **Interactive Dashboard**: Provide intuitive visualization and exploration tools

## Key Components

### 1. Data Dimensions

#### Demographic Data
- **Age**: Policyholder age groups (e.g., 20-30, 31-40, 41-50, 51-60, 61-70, 71+)
- **Gender**: Male, Female
- **Group**: Individual, Family, Corporate
- **Smoking Status**: Smoker, Non-Smoker (affects mortality rates and premiums)
- **Country**: India (fixed - with India-specific mortality tables and economic data)

#### Longevity Metrics
- **Life Expectancy**: Average remaining years of life (by age, gender, smoking status, country)
- **Mortality Rate**: Deaths per 1000 population (by age, gender, smoking status, country)
- **Longevity Trends**: Historical and projected improvements in life expectancy
- **Mortality Improvements**: Annual percentage change in mortality rates
- **Smoking Impact**: Smokers have 2.5x higher mortality rates and 8-12 years lower life expectancy

#### Economic Indicators
- **Inflation Rate**: Consumer Price Index (CPI) growth rate (% per year)
- **Interest Rates**: Risk-free rate / discount rate (% per year)
- **GDP Growth**: Gross Domestic Product growth rate (% per year)
- **Economic Scenarios**: Base case, optimistic, pessimistic

#### Insurance Metrics
- **Premium per Unit**: Premium per ₹1 lakh sum insured (varies by age, gender, policy type, smoking status, group)
- **Sum Insured**: Coverage amount (₹10L, ₹25L, ₹50L, ₹1Cr, ₹2Cr, or aggregate)
- **Total Premium**: `Total Premium = Premium per Unit × (Sum Insured / 100000)`
- **Policy Type**: 
  - Term Life Insurance (fixed term, e.g., 10, 20, 30 years)
  - Whole Life Insurance (lifetime coverage)
- **Premium Factors**: 
  - Age-based multipliers (exponential increase)
  - Gender-based adjustments (males pay ~20% more)
  - Smoking status multipliers (smokers pay 2.5-3x more)
  - Group multipliers (Corporate: 0.80x, Family: 0.92x, Individual: 1.0x)
  - Policy type multipliers (Whole Life: ~4x Term Life base rate)

### 2. Key Relationships & Logic

#### Premium Calculation Factors

1. **Mortality Risk Component**
   - Higher mortality rate → Higher premium
   - Age multiplier: Premium increases exponentially with age
   - Gender multiplier: Typically higher for males (higher mortality) - 1.2x
   - Smoking status multiplier: Smokers pay 2.5-3x more (2.5x higher mortality)
   - Country multiplier: Based on country-specific mortality tables (India-specific)

2. **Longevity Component**
   - Increasing life expectancy → Longer policy exposure → Higher cumulative risk
   - However, improvements in mortality reduce annual risk → Complex interaction
   - Net effect: Improved longevity generally increases whole life premiums, may reduce term life premiums for older ages

3. **Economic Impact**
   - **Inflation**: Premiums increase with inflation (insurance costs rise)
   - **Interest Rates**: 
     - Higher rates → Lower present value of future claims → Lower premiums
     - Insurance companies invest premiums; higher returns allow lower premiums
   - **GDP Growth**: Correlates with economic stability and mortality improvements

4. **Demographic Mix**
   - Premiums are weighted average across demographic segments
   - Changes in customer age mix over time affect average premium
   - Gender distribution impacts overall premium level

#### Forecasting Methodology

1. **Mortality Forecasting**
   - Project mortality rates using Lee-Carter model or similar
   - Incorporate longevity improvements (typically 1-2% annual mortality improvement)
   - Country-specific trends

2. **Economic Forecasting**
   - Use historical trends and scenario assumptions
   - Link inflation, interest rates, and GDP growth
   - Create scenarios: base case, optimistic (lower inflation, stable rates), pessimistic (high inflation, volatile rates)

3. **Premium Calculation**
   - Base premium per unit formula: `Premium_per_Unit = Base_Rate × Age_Multiplier × Gender_Multiplier × Smoking_Status_Multiplier × Group_Multiplier × Policy_Type_Multiplier`
   - Total Premium: `Total_Premium = Premium_per_Unit × (Sum_Insured / 100000)`
   - Adjust for projected mortality rates
   - Apply economic adjustments: `Adjusted_Premium = Total_Premium × (1 + Inflation_Adjustment) × Interest_Rate_Adjustment`
   - Apply longevity adjustments (policy-type-specific)
   - Apply GDP growth impact
   - Aggregate across demographics: Weighted average by segment size

4. **Scenario Analysis**
   - **Base Case**: Moderate mortality improvements, moderate inflation, stable interest rates
   - **Optimistic**: Faster mortality improvements, low inflation, higher interest rates → Lower premiums
   - **Pessimistic**: Slower mortality improvements, high inflation, lower interest rates → Higher premiums

### 3. Technical Stack

- **Python 3.10**
- **LangChain 1.0**: For AI-powered analysis and insights
- **Groq API**: Fast LLM inference for generating insights and scenario explanations
- **Streamlit**: Interactive web dashboard
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations

### 4. Dashboard Features

#### Main Dashboard Components

1. **Overview Panel**
   - Current average premium
   - 10-year forecast trend
   - Key drivers summary

2. **Forecast Visualization**
   - Line chart: Premium forecast over 10 years (base case)
   - Scenario comparison: Overlay optimistic and pessimistic scenarios
   - Confidence intervals / uncertainty bands

3. **Factor Analysis**
   - Breakdown by demographic segments (age, gender, country)
   - Impact of economic factors (inflation, interest rates)
   - Mortality vs. longevity trade-offs

4. **Scenario Selector**
   - Dropdown/buttons to switch between scenarios
   - Sliders to adjust economic parameters (inflation, interest rates)
   - Real-time recalculation

5. **Demographic Filters**
   - Filter by age group, gender, group, policy type, smoking status, and sum insured
   - Update forecasts based on selected filters
   - Sum insured filter: Select specific coverage amount or aggregate across all

6. **Insights Panel**
   - AI-generated insights using Groq API
   - Key findings and trends
   - Recommendations

### 5. Data Requirements

#### Input Data Structure

1. **Historical Mortality Data** (or synthetic generation)
   - Age-specific mortality rates by gender and country
   - Historical trends (past 10-20 years)

2. **Base Premiums**
   - Premium per ₹1 lakh sum insured by age, gender, policy type, smoking status, group, country
   - Can be synthetic/representative data
   - Includes smoking status impact (2.5-3x multiplier for smokers)

3. **Economic Data**
   - Historical inflation, interest rates, GDP growth
   - Scenario assumptions for future

4. **Demographic Distribution**
   - Current distribution of policyholders by segment (age, gender, group, policy type, smoking status)
   - Sum insured distribution (coverage amounts: ₹10L, ₹25L, ₹50L, ₹1Cr, ₹2Cr)
   - Projected changes in distribution (optional)

### 6. Implementation Approach

1. **Data Layer**
   - Create data models for all entities
   - Generate synthetic data or load from files
   - Data validation and preprocessing

2. **Forecasting Engine**
   - Mortality projection algorithms
   - Premium calculation logic
   - Scenario modeling functions

3. **AI Integration (LangChain + Groq)**
   - Generate insights from forecast results
   - Explain premium trends
   - Provide recommendations
   - Scenario analysis explanations

4. **Streamlit Dashboard**
   - Multi-page or single-page layout
   - Interactive widgets (sliders, dropdowns, filters)
   - Plotly charts embedded
   - Real-time updates

### 7. Success Criteria

- Accurate premium forecasting with logical relationships
- Clear visualization of trends and scenarios
- Intuitive user interface
- AI-powered insights that add value
- Fast performance (especially with Groq API)
- Scalable architecture

### 8. Key Considerations

- **Model Validation**: Ensure premium changes are logical and explainable
- **Uncertainty**: Acknowledge forecast uncertainty (confidence intervals)
- **Interpretability**: Users should understand why premiums change
- **Performance**: Real-time scenario updates
- **Extensibility**: Easy to add new factors or scenarios

## Pitch Line

"Our AI dashboard forecasts life insurance premiums for the next decade by combining longevity and mortality trends with economic indicators — helping insurers plan sustainable pricing and helping customers understand what drives cost changes."

---

## Next Steps

1. Set up project structure and dependencies
2. Create data models and sample data generators
3. Implement forecasting engine
4. Build LangChain + Groq integration for AI insights
5. Develop Streamlit dashboard with Plotly visualizations
6. Test and refine scenarios
7. Add documentation and examples
