# Life Insurance Premium Forecasting Dashboard

An AI-powered dashboard that forecasts average life insurance premiums over the next 10 years by analyzing mortality trends, longevity data, economic indicators, and customer demographics.

## 🎯 Project Overview

This dashboard helps insurers plan sustainable pricing and helps customers understand what drives cost changes by combining:
- **Longevity & Mortality Trends**: Life expectancy and mortality rate analysis (by smoking status)
- **Economic Indicators**: Inflation, interest rates, and GDP growth
- **Demographics**: Age, group (Individual/Family/Corporate), gender, policy type, and smoking status
- **Sum Insured**: Premium calculation per ₹1 lakh coverage, with configurable coverage amounts
- **Scenario Analysis**: Compare base case, optimistic, and pessimistic scenarios

## ✨ Features

- **10-Year Premium Forecasts**: Project average premiums with multiple scenarios
- **Interactive Visualizations**: Plotly charts for trends and comparisons
- **Scenario Comparison**: Base case, optimistic, and pessimistic scenarios
- **Demographic Filtering**: Filter by group, age, gender, policy type, smoking status, and sum insured
- **Sum Insured Selection**: Choose coverage amount (₹10L to ₹2Cr) or aggregate across all
- **AI-Powered Insights**: LangChain + Groq API for generating insights and recommendations
- **Chat Interface**: Natural language queries to control the dashboard
- **Economic Indicators**: Track inflation, interest rates, and GDP growth
- **Mortality & Longevity Trends**: Visualize mortality rates and life expectancy by scenario

## 🛠️ Technology Stack

- **Python 3.10**
- **Streamlit**: Interactive web dashboard
- **LangChain 1.0**: AI framework for insights
- **Groq API**: Fast LLM inference
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations

## 📦 Installation

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Data files** (auto-generated on first run):
   - The app will automatically generate data files on first launch
   - Alternatively, you can manually generate them:
     ```bash
     python create_data_csvs.py
     ```
   - This creates realistic CSV data files in the `data/` directory:
     - `mortality_data.csv` - Historical mortality rates and life expectancy (by smoking status)
     - `economic_data.csv` - Inflation, interest rates, and GDP growth
     - `base_premiums.csv` - Premium per ₹1 lakh sum insured by demographics
     - `demographic_distribution.csv` - Policyholder distribution (includes sum insured)

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Groq API key:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```
   - Get your API key from: https://console.groq.com/

## 🚀 Usage

1. **Run the dashboard**:
   ```bash
   streamlit run app.py
   ```

2. **Access the dashboard**:
   - The dashboard will open in your default web browser
   - Typically at `http://localhost:8501`

3. **Configure settings** (sidebar):
   - Country: India (fixed)
   - Set forecast period (start and end year)
   - Apply filters (group, gender, policy type, smoking status, age range)
   - Select sum insured (₹10L, ₹25L, ₹50L, ₹1Cr, ₹2Cr, or All)
   - Choose scenario mode (single or compare all)
   
4. **Use Chat Interface** (optional):
   - Click the chat icon in the bottom-right corner
   - Ask natural language queries like: "forecast for males age 30 years with sum insured 1cr, policy type whole life with non smoker"
   - The dashboard will automatically update filters based on your query

5. **View results**:
   - Overview metrics (with premium per unit and sum insured info)
   - Premium forecast charts (showing total premium for selected sum insured)
   - Economic indicators (Inflation, Interest, GDP, Premium vs Interest)
   - Mortality & Longevity trends by scenario
   - AI-generated insights (with filter context)
   - Comprehensive data tables (downloadable as CSV)

## 📊 Key Components

### Data Models (`data_models.py`)
- Demographic data structures (Age, Group, Gender, Policy Type, Smoking Status)
- Mortality and longevity data (India-specific, by smoking status)
- Economic indicators (India-specific)
- Premium data models (premium per ₹1 lakh sum insured)
- Data loading from CSV files (auto-generated on first run)

### Forecasting Engine (`forecasting_engine.py`)
- Premium calculation logic
- Mortality projections
- Economic projections
- Scenario modeling
- Weighted average calculations

### AI Insights (`ai_insights.py`)
- LangChain integration with Groq
- Forecast summaries
- Scenario comparisons (with filter context)
- Driver analysis (includes smoking status and sum insured impact)
- Recommendations (tailored to selected filters)

### Chat Interface (`chat_interface.py`)
- Natural language query parsing
- Automatic filter updates
- Supports all filters including smoking status and sum insured
- Groq LLM-based parsing with regex fallback

### Dashboard (`app.py`)
- Streamlit interface
- Interactive visualizations (Plotly charts)
- Real-time filtering (all demographics + smoking status + sum insured)
- Scenario comparison
- Chat interface integration
- Comprehensive data tables

## 🔧 Configuration

### Scenarios

The dashboard includes three predefined scenarios (calibrated for India):

1. **Base Case**: Moderate inflation (5.0%), stable interest rates (6.5%), normal mortality improvements (1.5%)
2. **Optimistic**: Low inflation (4.0%), higher interest rates (7.5%), faster mortality improvements (2.0%)
3. **Pessimistic**: High inflation (6.0%), lower interest rates (5.5%), slower mortality improvements (1.0%)

### Country

- **India**: The dashboard is configured for India-specific data including:
  - India-specific mortality and longevity patterns
  - India-specific economic indicators (inflation, interest rates, GDP)
  - India-specific demographic distributions

## 📈 Understanding the Forecasts

### Premium Calculation Factors

1. **Base Premium per Unit**: Premium per ₹1 lakh sum insured
   - Varies by age, gender, policy type, smoking status, and group
   - Smokers pay 2.5-3x more than non-smokers
   
2. **Total Premium**: `Total Premium = Premium per Unit × (Sum Insured / 100000)`

3. **Mortality Risk**: Higher mortality rates → Higher premiums
   - Smokers have 2.5x higher mortality rates

4. **Age Multiplier**: Premiums increase exponentially with age

5. **Gender Adjustment**: Typically higher for males (1.2x)

6. **Group Adjustment**: Corporate (0.80x), Family (0.92x), Individual (1.0x)

7. **Smoking Status**: Smokers pay 2.5-3x more than non-smokers

8. **Economic Factors**:
   - Inflation: Compounding effect increases premiums over time
   - Interest Rates: Higher rates → Lower premiums (present value and investment income effects)
   - GDP Growth: Higher GDP → Economic stability → Lower risk → Slightly lower premiums

9. **Longevity**: 
   - Term Life: Longer life expectancy → Reduces premium (lower annual risk)
   - Whole Life: Longer life expectancy → Increases premium (longer exposure)

### Scenario Impacts

- **Optimistic Scenario**: Lower premiums (due to low inflation and higher interest rates)
- **Pessimistic Scenario**: Higher premiums (due to high inflation and lower interest rates)
- **Base Case**: Moderate premium increases

## 🤖 AI Insights

The AI insights feature uses Groq API (mixtral-8x7b-32768 model by default) to generate:
- Forecast summaries
- Scenario comparisons
- Driver analysis
- Strategic recommendations

Note: AI insights require a valid GROQ_API_KEY in your `.env` file. You can specify a different model by setting `GROQ_MODEL_NAME` in your `.env` file (e.g., `GROQ_MODEL_NAME=llama-3.1-70b-8192`).

## 📝 Project Structure

```
.
├── app.py                  # Streamlit dashboard
├── data_models.py          # Data structures and enums
├── forecasting_engine.py   # Premium forecasting logic
├── ai_insights.py          # LangChain + Groq integration
├── chat_interface.py       # Natural language chat interface
├── create_data_csvs.py     # Data generation script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── data/                  # CSV data files (auto-generated)
│   ├── mortality_data.csv
│   ├── economic_data.csv
│   ├── base_premiums.csv
│   └── demographic_distribution.csv
├── README.md              # This file
├── QUICKSTART.md          # Quick setup guide
├── PROJECT_PROMPT.md      # Detailed project requirements
├── CHAT_INTERFACE_GUIDE.md # Chat interface usage guide
├── PRODUCT_ROADMAP.md     # Product enhancement roadmap
└── IMPLEMENTATION_REVIEW.md # Implementation review
```

## 🔍 Future Enhancements

Potential improvements:
- Real data integration (from insurance databases)
- More sophisticated mortality models (Lee-Carter, etc.)
- Additional demographic factors
- Custom scenario builder
- Export functionality (PDF, Excel)
- Historical data comparison
- More countries and regions

## ⚠️ Important Notes

- This dashboard uses **realistic synthetic data** for demonstration purposes
- Premium calculations follow actuarial principles but are simplified for illustration
- Premiums are calculated as **premium per ₹1 lakh sum insured** and multiplied by coverage amount
- Actual insurance pricing involves more complex actuarial models
- Consult with actuaries for real-world applications
- **Currency**: All amounts are in Indian Rupees (₹)
- **Country**: Dashboard is configured for India only

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is a demonstration project. For production use, consult with actuarial and insurance pricing experts.

---

**Pitch Line**: *Our AI dashboard forecasts life insurance premiums for the next decade by combining longevity and mortality trends with economic indicators — helping insurers plan sustainable pricing and helping customers understand what drives cost changes.*
