"""
Chat-based interface for natural language queries to the dashboard.
"""
import os
import re
import json
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


class DashboardChatInterface:
    """Process natural language queries and extract dashboard parameters"""
    
    def __init__(self, model_name: str = None):
        """Initialize Groq LLM for chat interface"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        if model_name is None:
            model_name = os.getenv("GROQ_MODEL_NAME", "mixtral-8x7b-32768")
        
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.3  # Lower temperature for more consistent parsing
        )
    
    def parse_query(self, user_query: str) -> Dict:
        """
        Parse natural language query and extract dashboard parameters.
        Returns a dictionary with extracted parameters.
        """
        system_prompt = """You are a helpful assistant that extracts parameters from user queries about life insurance premium forecasting.

Available parameters:
- start_year: Year to start forecast (default: 2024)
- end_year: Year to end forecast (default: 2034)
- scenario: "base", "optimistic", or "pessimistic" (default: "base")
- group: "Individual", "Family", "Corporate", or "All" (default: "All")
- gender: "Male", "Female", or "All" (default: "All")
- policy_type: "Term Life", "Whole Life", or "All" (default: "All")
- smoking_status: "Smoker", "Non-Smoker", or "All" (default: "All")
- sum_insured: Numeric value in rupees (e.g., 1000000 for ₹10 Lakh, 10000000 for ₹1 Crore) or null for "All"
- age_min: Minimum age (default: 20)
- age_max: Maximum age (default: 80)

Extract only the parameters mentioned in the query. Return a JSON object with only the parameters that are explicitly mentioned or can be inferred.

Sum Insured mapping:
- "10 lakh", "10l", "10 l" → 1000000
- "25 lakh", "25l", "25 l" → 2500000
- "50 lakh", "50l", "50 l" → 5000000
- "1 crore", "1cr", "1 cr", "1crore" → 10000000
- "2 crore", "2cr", "2 cr", "2crore" → 20000000

Smoking Status:
- "smoker", "smoking" → "Smoker"
- "non-smoker", "non smoker", "non-smoking", "non smoking" → "Non-Smoker"

Examples:
- "Show me forecast for males aged 30-50" → {"gender": "Male", "age_min": 30, "age_max": 50}
- "Compare all scenarios for term life insurance" → {"scenario": null, "policy_type": "Term Life", "compare_all": true}
- "What about family policies?" → {"group": "Family"}
- "Show optimistic scenario" → {"scenario": "optimistic"}
- "forecast for males age 30 years with sum insured 1cr, policy type whole life with non smoker" → {"gender": "Male", "age_min": 30, "age_max": 30, "sum_insured": 10000000, "policy_type": "Whole Life", "smoking_status": "Non-Smoker"}

Return ONLY valid JSON, no other text."""

        prompt = f"""Extract parameters from this query: "{user_query}"

Return JSON with only mentioned parameters. Use null for scenario if user wants to compare all scenarios."""

        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            
            # Extract JSON from response
            content = response.content.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                import json
                params = json.loads(json_match.group())
                return params
            else:
                # Fallback: try to parse the entire response as JSON
                import json
                params = json.loads(content)
                return params
                
        except Exception as e:
            # Fallback parsing with regex
            return self._fallback_parse(user_query)
    
    def _fallback_parse(self, query: str) -> Dict:
        """Fallback parsing using regex patterns"""
        params = {}
        query_lower = query.lower()
        
        # Extract scenario
        if 'optimistic' in query_lower:
            params['scenario'] = 'optimistic'
        elif 'pessimistic' in query_lower:
            params['scenario'] = 'pessimistic'
        elif 'base' in query_lower and 'case' in query_lower:
            params['scenario'] = 'base'
        elif 'compare' in query_lower or 'all scenario' in query_lower:
            params['compare_all'] = True
        
        # Extract gender
        if 'male' in query_lower and 'female' not in query_lower:
            params['gender'] = 'Male'
        elif 'female' in query_lower:
            params['gender'] = 'Female'
        
        # Extract group
        if 'individual' in query_lower:
            params['group'] = 'Individual'
        elif 'family' in query_lower:
            params['group'] = 'Family'
        elif 'corporate' in query_lower:
            params['group'] = 'Corporate'
        
        # Extract policy type
        if 'term' in query_lower and 'whole' not in query_lower:
            params['policy_type'] = 'Term Life'
        elif 'whole life' in query_lower or ('whole' in query_lower and 'life' in query_lower):
            params['policy_type'] = 'Whole Life'
        
        # Extract smoking status
        if 'non-smoker' in query_lower or 'non smoker' in query_lower or ('non' in query_lower and 'smoker' in query_lower):
            params['smoking_status'] = 'Non-Smoker'
        elif 'smoker' in query_lower and 'non' not in query_lower:
            params['smoking_status'] = 'Smoker'
        
        # Extract sum insured
        # Check for crore first (larger amounts)
        crore_match = re.search(r'(\d+)\s*(?:crore|cr|crores)', query_lower)
        if crore_match:
            crore_value = int(crore_match.group(1))
            params['sum_insured'] = crore_value * 10000000
        else:
            # Check for lakh
            lakh_match = re.search(r'(\d+)\s*(?:lakh|l|lakhs)', query_lower)
            if lakh_match:
                lakh_value = int(lakh_match.group(1))
                params['sum_insured'] = lakh_value * 100000
        
        # Extract age range
        age_pattern = r'age[ds]?\s*(\d+)[\s-]+(\d+)'
        age_match = re.search(age_pattern, query_lower)
        if age_match:
            params['age_min'] = int(age_match.group(1))
            params['age_max'] = int(age_match.group(2))
        else:
            # Single age
            age_single = re.search(r'age[ds]?\s*(\d+)', query_lower)
            if age_single:
                age = int(age_single.group(1))
                params['age_min'] = max(20, age - 5)
                params['age_max'] = min(80, age + 5)
        
        # Extract years
        year_pattern = r'(\d{4})[-\s]+(\d{4})'
        year_match = re.search(year_pattern, query)
        if year_match:
            params['start_year'] = int(year_match.group(1))
            params['end_year'] = int(year_match.group(2))
        
        return params
    
    def generate_response(self, user_query: str, forecast_data: Optional[Dict] = None) -> str:
        """Generate a natural language response about the forecast"""
        if forecast_data is None:
            return "I can help you explore the premium forecasts. Try asking about specific scenarios, demographics, or time periods."
        
        prompt = f"""Based on the following premium forecast data, provide a concise summary:

{forecast_data}

User query: "{user_query}"

Provide a helpful 2-3 sentence response about the forecast."""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"I understand your query. The forecast shows the requested information."
