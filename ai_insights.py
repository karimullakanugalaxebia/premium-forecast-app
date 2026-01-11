"""
AI-powered insights using LangChain and Groq API.
Enhanced with structured output and better clarity.
"""
import os
import json
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import pandas as pd
import numpy as np

load_dotenv()


class PremiumInsightsGenerator:
    """Generate AI-powered insights about premium forecasts"""
    
    def __init__(self, model_name: str = None):
        """Initialize Groq LLM
        
        Model can be specified via:
        1. model_name parameter
        2. GROQ_MODEL_NAME environment variable
        3. Default: mixtral-8x7b-32768 (commonly available)
        
        Other available models (check Groq console for current list):
        - llama-3.1-70b-8192
        - llama-3.1-8b-8192
        - llama-3.3-70b-versatile (if available)
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Get model name from parameter or environment variable, with fallback
        if model_name is None:
            model_name = os.getenv("GROQ_MODEL_NAME", "mixtral-8x7b-32768")
        
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.7
        )
    
    def generate_forecast_summary(self, forecast_df: pd.DataFrame, 
                                 scenario_name: str = "base") -> str:
        """Generate a summary of the forecast"""
        scenario_data = forecast_df[forecast_df['scenario'] == scenario_name]
        
        if scenario_data.empty:
            return "No forecast data available for analysis."
        
        current_premium = scenario_data.iloc[0]['average_premium']
        final_premium = scenario_data.iloc[-1]['average_premium']
        change_pct = ((final_premium - current_premium) / current_premium) * 100
        
        avg_inflation = scenario_data['inflation_rate'].mean()
        avg_interest = scenario_data['interest_rate'].mean()
        
        prompt = f"""You are an expert actuarial analyst and insurance pricing specialist. 
Analyze the following life insurance premium forecast data and provide a concise, insightful summary.

Forecast Period: {scenario_data['year'].min()} - {scenario_data['year'].max()}
Scenario: {scenario_name}
Starting Premium: ₹{current_premium:,.2f}
Ending Premium: ₹{final_premium:,.2f}
Total Change: {change_pct:.1f}%
Average Inflation Rate: {avg_inflation:.2f}%
Average Interest Rate: {avg_interest:.2f}%

Provide a 3-4 sentence summary highlighting:
1. Key trend in premiums (increasing/decreasing/stable)
2. Main drivers (economic factors, mortality trends)
3. What this means for insurers and policyholders

Be concise and professional."""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def generate_scenario_comparison(self, comparison_df: pd.DataFrame, filters: Dict = None) -> Dict:
        """Generate structured comparison between scenarios with metrics"""
        scenarios = comparison_df['scenario'].unique()
        
        scenario_summaries = []
        scenario_details = {}
        
        for scenario in scenarios:
            scenario_data = comparison_df[comparison_df['scenario'] == scenario]
            start_premium = scenario_data.iloc[0]['average_premium']
            end_premium = scenario_data.iloc[-1]['average_premium']
            change = ((end_premium - start_premium) / start_premium) * 100
            
            # Calculate additional metrics
            avg_inflation = scenario_data['inflation_rate'].mean()
            avg_interest = scenario_data['interest_rate'].mean()
            avg_gdp = scenario_data['gdp_growth'].mean()
            avg_mortality = scenario_data.get('average_mortality_rate', pd.Series([0])).mean()
            avg_life_exp = scenario_data.get('average_life_expectancy', pd.Series([0])).mean()
            
            # Calculate volatility (coefficient of variation)
            premium_volatility = (scenario_data['average_premium'].std() / 
                                 scenario_data['average_premium'].mean()) * 100
            
            scenario_summaries.append({
                'scenario': scenario,
                'start': start_premium,
                'end': end_premium,
                'change': change,
                'avg_inflation': avg_inflation,
                'avg_interest': avg_interest,
                'volatility': premium_volatility
            })
            
            scenario_details[scenario] = {
                'start_premium': start_premium,
                'end_premium': end_premium,
                'change_pct': change,
                'avg_inflation': avg_inflation,
                'avg_interest': avg_interest,
                'avg_gdp': avg_gdp,
                'avg_mortality': avg_mortality,
                'avg_life_expectancy': avg_life_exp,
                'volatility': premium_volatility
            }
        
        # Find best and worst scenarios
        best_scenario = min(scenario_summaries, key=lambda x: x['end'])
        worst_scenario = max(scenario_summaries, key=lambda x: x['end'])
        
        # Build filter context for AI
        filter_context = ""
        if filters:
            filter_parts = []
            if filters.get('gender') and filters['gender'] != 'All':
                filter_parts.append(f"Gender: {filters['gender']}")
            if filters.get('group') and filters['group'] != 'All':
                filter_parts.append(f"Group: {filters['group']}")
            if filters.get('policy_type') and filters['policy_type'] != 'All':
                filter_parts.append(f"Policy Type: {filters['policy_type']}")
            if filters.get('smoking_status') and filters['smoking_status'] != 'All':
                filter_parts.append(f"Smoking Status: {filters['smoking_status']}")
            if filters.get('sum_insured'):
                si_value = filters['sum_insured']
                if si_value == 1000000:
                    si_label = "₹10 Lakh"
                elif si_value == 2500000:
                    si_label = "₹25 Lakh"
                elif si_value == 5000000:
                    si_label = "₹50 Lakh"
                elif si_value == 10000000:
                    si_label = "₹1 Crore"
                elif si_value == 20000000:
                    si_label = "₹2 Crore"
                else:
                    si_label = f"₹{si_value/100000:.0f} Lakh"
                filter_parts.append(f"Sum Insured: {si_label}")
            if filters.get('age_min') or filters.get('age_max'):
                age_min = filters.get('age_min', 20)
                age_max = filters.get('age_max', 80)
                if age_min != 20 or age_max != 80:
                    filter_parts.append(f"Age Range: {age_min}-{age_max} years")
            
            if filter_parts:
                filter_context = f"\n\nFILTER CONTEXT:\nThe analysis is filtered for: {', '.join(filter_parts)}.\n"
        
        # Get sum insured info from comparison_df if available
        sum_insured_info = ""
        if 'average_sum_insured' in comparison_df.columns and comparison_df['average_sum_insured'].mean() > 0:
            avg_si = comparison_df['average_sum_insured'].mean()
            if avg_si == 1000000:
                sum_insured_info = " (for ₹10 Lakh coverage)"
            elif avg_si == 2500000:
                sum_insured_info = " (for ₹25 Lakh coverage)"
            elif avg_si == 5000000:
                sum_insured_info = " (for ₹50 Lakh coverage)"
            elif avg_si == 10000000:
                sum_insured_info = " (for ₹1 Crore coverage)"
            elif avg_si == 20000000:
                sum_insured_info = " (for ₹2 Crore coverage)"
            else:
                sum_insured_info = f" (for ₹{avg_si/100000:.0f} Lakh coverage)"
        
        # Generate AI analysis
        scenario_text = "\n".join([f"""
{s['scenario'].upper()} SCENARIO:
- Starting Premium: ₹{s['start']:,.2f}{sum_insured_info}
- Ending Premium: ₹{s['end']:,.2f}{sum_insured_info}
- Total Change: {s['change']:+.1f}%
- Average Inflation: {s['avg_inflation']:.2f}%
- Average Interest Rate: {s['avg_interest']:.2f}%
- Premium Volatility: {s['volatility']:.2f}%
""" for s in scenario_summaries])
        
        prompt = f"""You are an expert actuarial analyst and insurance pricing specialist. 

Analyze these life insurance premium forecast scenarios for India:{filter_context}

{scenario_text}

Provide a structured analysis in the following format (use clear sections):

## EXECUTIVE SUMMARY
[1-2 sentences: Overall assessment of premium trends across scenarios]

## KEY FINDINGS
[3-4 bullet points highlighting most important insights]

## SCENARIO COMPARISON
[Compare each scenario, explaining why premiums differ]

## RISK ASSESSMENT
[Identify which scenario poses highest/lowest risk for insurers and policyholders]

## RECOMMENDATIONS
[Actionable recommendations for:
1. Insurance companies (pricing strategy)
2. Policyholders (when to buy, what to expect)
3. Planning focus (which scenario to use for strategic planning)]

Be specific, use numbers, and make it actionable. Format with clear headings."""

        try:
            response = self.llm.invoke(prompt)
            ai_analysis = response.content
            
            return {
                'analysis': ai_analysis,
                'scenarios': scenario_details,
                'best_scenario': best_scenario['scenario'],
                'worst_scenario': worst_scenario['scenario'],
                'premium_range': {
                    'min': best_scenario['end'],
                    'max': worst_scenario['end'],
                    'spread': worst_scenario['end'] - best_scenario['end'],
                    'spread_pct': ((worst_scenario['end'] - best_scenario['end']) / best_scenario['end']) * 100
                }
            }
        except Exception as e:
            return {
                'analysis': f"Error generating comparison: {str(e)}",
                'scenarios': scenario_details,
                'best_scenario': best_scenario['scenario'],
                'worst_scenario': worst_scenario['scenario'],
                'premium_range': {
                    'min': best_scenario['end'],
                    'max': worst_scenario['end'],
                    'spread': worst_scenario['end'] - best_scenario['end'],
                    'spread_pct': ((worst_scenario['end'] - best_scenario['end']) / best_scenario['end']) * 100
                }
            }
    
    def generate_driver_analysis(self, forecast_df: pd.DataFrame,
                                scenario_name: str = "base", filters: Dict = None) -> str:
        """Analyze the main drivers of premium changes"""
        scenario_data = forecast_df[forecast_df['scenario'] == scenario_name].copy()
        
        # Calculate correlations and changes
        premium_change = ((scenario_data.iloc[-1]['average_premium'] - 
                          scenario_data.iloc[0]['average_premium']) / 
                         scenario_data.iloc[0]['average_premium']) * 100
        
        inflation_change = scenario_data.iloc[-1]['inflation_rate'] - scenario_data.iloc[0]['inflation_rate']
        interest_change = scenario_data.iloc[-1]['interest_rate'] - scenario_data.iloc[0]['interest_rate']
        
        avg_inflation = scenario_data['inflation_rate'].mean()
        avg_interest = scenario_data['interest_rate'].mean()
        
        # Build filter context
        filter_context = ""
        if filters:
            filter_parts = []
            if filters.get('gender') and filters['gender'] != 'All':
                filter_parts.append(f"Gender: {filters['gender']}")
            if filters.get('smoking_status') and filters['smoking_status'] != 'All':
                filter_parts.append(f"Smoking Status: {filters['smoking_status']}")
            if filters.get('sum_insured'):
                si_value = filters['sum_insured']
                if si_value == 10000000:
                    si_label = "₹1 Crore"
                elif si_value == 1000000:
                    si_label = "₹10 Lakh"
                else:
                    si_label = f"₹{si_value/100000:.0f} Lakh"
                filter_parts.append(f"Sum Insured: {si_label}")
            if filter_parts:
                filter_context = f"\n\nNote: Analysis is filtered for {', '.join(filter_parts)}.\n"
        
        prompt = f"""You are an expert insurance pricing analyst. Analyze the drivers of life insurance premium changes.{filter_context}

Premium Change Over Period: {premium_change:+.1f}%
Average Inflation Rate: {avg_inflation:.2f}%
Average Interest Rate: {avg_interest:.2f}%
Inflation Change: {inflation_change:+.2f} percentage points
Interest Rate Change: {interest_change:+.2f} percentage points

Explain:
1. How inflation affects life insurance premiums
2. How interest rates affect premiums (both present value and investment income effects)
3. The combined impact of these economic factors
4. Other factors that might influence premiums (mortality trends, longevity, smoking status, sum insured)

Be clear and educational (2-3 paragraphs)."""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating driver analysis: {str(e)}"
    
    def generate_recommendations(self, comparison_df: pd.DataFrame, filters: Dict = None) -> Dict:
        """Generate structured, actionable recommendations with priorities"""
        scenarios = comparison_df['scenario'].unique()
        
        scenario_stats = {}
        for scenario in scenarios:
            scenario_data = comparison_df[comparison_df['scenario'] == scenario]
            start_premium = scenario_data.iloc[0]['average_premium']
            end_premium = scenario_data.iloc[-1]['average_premium']
            change_pct = ((end_premium - start_premium) / start_premium) * 100
            
            scenario_stats[scenario] = {
                'start': start_premium,
                'end': end_premium,
                'change_pct': change_pct,
                'avg_inflation': scenario_data['inflation_rate'].mean(),
                'avg_interest': scenario_data['interest_rate'].mean(),
                'avg_gdp': scenario_data['gdp_growth'].mean()
            }
        
        # Calculate key metrics for recommendations
        avg_premium_increase = np.mean([s['change_pct'] for s in scenario_stats.values()])
        max_premium = max([s['end'] for s in scenario_stats.values()])
        min_premium = min([s['end'] for s in scenario_stats.values()])
        
        # Build scenario analysis text separately to avoid f-string issues
        scenario_lines = []
        for s in scenarios:
            start_val = scenario_stats[s]['start']
            end_val = scenario_stats[s]['end']
            change_val = scenario_stats[s]['change_pct']
            inf_val = scenario_stats[s]['avg_inflation']
            int_val = scenario_stats[s]['avg_interest']
            gdp_val = scenario_stats[s]['avg_gdp']
            
            scenario_lines.append(f"""
{s.upper()} SCENARIO:
- Starting Premium: ₹{start_val:,.2f}
- 10-Year Forecast: ₹{end_val:,.2f}
- Change: {change_val:+.1f}%
- Economic Conditions: Inflation {inf_val:.2f}%, Interest {int_val:.2f}%, GDP {gdp_val:.2f}%
""")
        
        scenario_analysis_text = "\n".join(scenario_lines)
        spread = max_premium - min_premium
        spread_pct = (spread / min_premium) * 100
        
        # Build filter context
        filter_context = ""
        if filters:
            filter_parts = []
            if filters.get('gender') and filters['gender'] != 'All':
                filter_parts.append(f"Gender: {filters['gender']}")
            if filters.get('group') and filters['group'] != 'All':
                filter_parts.append(f"Group: {filters['group']}")
            if filters.get('policy_type') and filters['policy_type'] != 'All':
                filter_parts.append(f"Policy Type: {filters['policy_type']}")
            if filters.get('smoking_status') and filters['smoking_status'] != 'All':
                filter_parts.append(f"Smoking Status: {filters['smoking_status']}")
            if filters.get('sum_insured'):
                si_value = filters['sum_insured']
                if si_value == 10000000:
                    si_label = "₹1 Crore"
                elif si_value == 1000000:
                    si_label = "₹10 Lakh"
                else:
                    si_label = f"₹{si_value/100000:.0f} Lakh"
                filter_parts.append(f"Sum Insured: {si_label}")
            if filters.get('age_min') or filters.get('age_max'):
                age_min = filters.get('age_min', 20)
                age_max = filters.get('age_max', 80)
                if age_min != 20 or age_max != 80:
                    filter_parts.append(f"Age: {age_min}-{age_max} years")
            if filter_parts:
                filter_context = f"\n\nFILTER CONTEXT:\nRecommendations are tailored for: {', '.join(filter_parts)}.\n"
        
        prompt = f"""You are an expert insurance consultant and actuarial advisor providing strategic recommendations.{filter_context}

PREMIUM FORECAST ANALYSIS:
{scenario_analysis_text}

KEY METRICS:
- Average Premium Increase Across Scenarios: {avg_premium_increase:.1f}%
- Premium Range: ₹{min_premium:,.2f} - ₹{max_premium:,.2f}
- Spread: ₹{spread:,.2f} ({spread_pct:.1f}%)

Provide structured recommendations in this format:

## FOR INSURANCE COMPANIES

### Pricing Strategy
[2-3 specific recommendations about pricing adjustments]

### Capital Planning
[Recommendations for reserve management and capital allocation]

### Product Development
[Suggestions for new products or modifications]

### Risk Management
[Key risks to monitor and mitigate]

## FOR POLICYHOLDERS

### Best Time to Purchase
[When should customers buy based on forecasts]

### What to Expect
[Expected premium changes and planning considerations]

### Policy Selection
[Recommendations on policy types and terms]

## STRATEGIC PLANNING

### Recommended Scenario for Planning
[Which scenario to use and why]

### Key Assumptions to Monitor
[What economic/mortality factors to watch]

### Action Timeline
[When to take specific actions]

Be specific, use numbers, prioritize actions, and make it immediately actionable."""

        try:
            response = self.llm.invoke(prompt)
            ai_recommendations = response.content
            
            return {
                'recommendations': ai_recommendations,
                'metrics': {
                    'avg_premium_increase': avg_premium_increase,
                    'premium_range': {'min': min_premium, 'max': max_premium},
                    'spread': max_premium - min_premium,
                    'spread_pct': ((max_premium - min_premium) / min_premium) * 100
                },
                'scenario_stats': scenario_stats
            }
        except Exception as e:
            return {
                'recommendations': f"Error generating recommendations: {str(e)}",
                'metrics': {
                    'avg_premium_increase': avg_premium_increase,
                    'premium_range': {'min': min_premium, 'max': max_premium},
                    'spread': max_premium - min_premium,
                    'spread_pct': ((max_premium - min_premium) / min_premium) * 100
                },
                'scenario_stats': scenario_stats
            }
    
    def calculate_driver_impact(self, forecast_df: pd.DataFrame) -> Dict:
        """Calculate the impact of different drivers on premium changes"""
        if forecast_df.empty:
            return {}
        
        # Calculate correlations
        premium_change = forecast_df['average_premium'].pct_change().fillna(0)
        inflation_change = forecast_df['inflation_rate'].diff().fillna(0)
        interest_change = forecast_df['interest_rate'].diff().fillna(0)
        gdp_change = forecast_df.get('gdp_growth', pd.Series([0] * len(forecast_df))).diff().fillna(0)
        
        # Calculate correlation coefficients
        inflation_corr = premium_change.corr(inflation_change) if len(premium_change) > 1 else 0
        interest_corr = premium_change.corr(interest_change) if len(premium_change) > 1 else 0
        gdp_corr = premium_change.corr(gdp_change) if len(gdp_change) > 1 else 0
        
        # Calculate overall impact
        total_premium_change = ((forecast_df.iloc[-1]['average_premium'] - 
                                forecast_df.iloc[0]['average_premium']) / 
                               forecast_df.iloc[0]['average_premium']) * 100
        
        avg_inflation = forecast_df['inflation_rate'].mean()
        avg_interest = forecast_df['interest_rate'].mean()
        avg_gdp = forecast_df.get('gdp_growth', pd.Series([0])).mean()
        
        return {
            'total_premium_change_pct': total_premium_change,
            'drivers': {
                'inflation': {
                    'correlation': inflation_corr,
                    'avg_value': avg_inflation,
                    'impact': 'High' if abs(inflation_corr) > 0.5 else 'Medium' if abs(inflation_corr) > 0.3 else 'Low'
                },
                'interest_rate': {
                    'correlation': interest_corr,
                    'avg_value': avg_interest,
                    'impact': 'High' if abs(interest_corr) > 0.5 else 'Medium' if abs(interest_corr) > 0.3 else 'Low'
                },
                'gdp_growth': {
                    'correlation': gdp_corr,
                    'avg_value': avg_gdp,
                    'impact': 'High' if abs(gdp_corr) > 0.5 else 'Medium' if abs(gdp_corr) > 0.3 else 'Low'
                }
            }
        }
