# Life Insurance Premium Forecasting Dashboard

An AI-powered dashboard that forecasts average life insurance premiums over the next 10 years by analyzing mortality trends, longevity data, economic indicators, and customer demographics.

## 🎯 Project Overview

This dashboard helps insurers plan sustainable pricing and helps customers understand what drives cost changes by combining:
- **Longevity & Mortality Trends**: Life expectancy and mortality rate analysis
- **Economic Indicators**: Inflation, interest rates, and GDP growth
- **Demographics**: Age, group (Individual/Family/Corporate), gender, and policy type
- **Scenario Analysis**: Compare base case, optimistic, and pessimistic scenarios

## ✨ Features

- **10-Year Premium Forecasts**: Project average premiums with multiple scenarios
- **Interactive Visualizations**: Plotly charts for trends and comparisons
- **Scenario Comparison**: Base case, optimistic, and pessimistic scenarios
- **Demographic Filtering**: Filter by group, age, gender, policy type
- **AI-Powered Insights**: LangChain + Groq API for generating insights and recommendations
- **Economic Indicators**: Track inflation, interest rates, and GDP growth

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

3. **Generate data files**:
   ```bash
   python create_data_csvs.py
   ```
   This will create realistic CSV data files in the `data/` directory:
   - `mortality_data.csv` - Historical mortality rates and life expectancy
   - `economic_data.csv` - Inflation, interest rates, and GDP growth
   - `base_premiums.csv` - Base premium rates by demographics
   - `demographic_distribution.csv` - Policyholder distribution

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
   - Apply filters (group, gender, policy type, age range)
   - Choose scenario mode (single or compare all)

4. **View results**:
   - Overview metrics
   - Premium forecast charts
   - Economic indicators
   - AI-generated insights
   - Detailed data tables

## 📊 Key Components

### Data Models (`data_models.py`)
- Demographic data structures (Age, Group, Gender, Policy Type)
- Mortality and longevity data (India-specific)
- Economic indicators (India-specific)
- Premium data models with Group factors
- Synthetic data generators

### Forecasting Engine (`forecasting_engine.py`)
- Premium calculation logic
- Mortality projections
- Economic projections
- Scenario modeling
- Weighted average calculations

### AI Insights (`ai_insights.py`)
- LangChain integration with Groq
- Forecast summaries
- Scenario comparisons
- Driver analysis
- Recommendations

### Dashboard (`app.py`)
- Streamlit interface
- Interactive visualizations
- Real-time filtering
- Scenario comparison

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

1. **Mortality Risk**: Higher mortality rates → Higher premiums
2. **Age Multiplier**: Premiums increase exponentially with age
3. **Gender Adjustment**: Typically higher for males
4. **Group Adjustment**: Corporate (0.85x), Family (0.95x), Individual (1.0x)
5. **Economic Factors**:
   - Inflation: Increases premiums
   - Interest Rates: Higher rates → Lower premiums (present value and investment income effects)
6. **Longevity**: Improving longevity increases exposure but reduces annual mortality risk

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
├── data_models.py          # Data structures and generators
├── forecasting_engine.py   # Premium forecasting logic
├── ai_insights.py          # LangChain + Groq integration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
└── PROJECT_PROMPT.md      # Detailed project requirements
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

- This dashboard uses **synthetic data** for demonstration purposes
- Premium calculations are simplified for illustration
- Actual insurance pricing involves more complex actuarial models
- Consult with actuaries for real-world applications

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is a demonstration project. For production use, consult with actuarial and insurance pricing experts.

---

**Pitch Line**: *Our AI dashboard forecasts life insurance premiums for the next decade by combining longevity and mortality trends with economic indicators — helping insurers plan sustainable pricing and helping customers understand what drives cost changes.*
