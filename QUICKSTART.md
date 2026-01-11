# Quick Start Guide

## Setup Instructions

1. **Install Python 3.10** (if not already installed)

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Data Files** (Optional - auto-generated on first run):
   - The app will automatically generate data files on first launch
   - To manually generate them:
     ```bash
     python create_data_csvs.py
     ```
   - This creates realistic CSV data files in the `data/` directory:
     - Includes mortality data by smoking status
     - Premium per ₹1 lakh sum insured
     - Demographic distribution with sum insured amounts

4. **Set Up Groq API Key**:
   - Get your API key from: https://console.groq.com/
   - Create a `.env` file in the project root
   - Add: `GROQ_API_KEY=your_actual_api_key_here`
   - (Optional) Specify a model: `GROQ_MODEL_NAME=mixtral-8x7b-32768` (default)
     - Other options: `llama-3.1-70b-8192`, `llama-3.1-8b-8192`, etc.
     - Check https://console.groq.com/docs/models for available models

5. **Run the Dashboard**:
   ```bash
   streamlit run app.py
   ```

6. **Access the Dashboard**:
   - Open your browser to: http://localhost:8501
   - Data will be auto-generated on first run (if not already present)
   - Start exploring!

## Key Features to Try

- **Filters**: Try filtering by smoking status (Smoker/Non-Smoker) and sum insured (₹10L to ₹2Cr)
- **Chat Interface**: Click the chat icon (bottom-right) and try: "forecast for males age 30 years with sum insured 1cr, policy type whole life with non smoker"
- **Sum Insured**: Select different coverage amounts to see how premiums change
- **AI Insights**: View AI-generated insights that include context about your selected filters

## Troubleshooting

### Groq API Key Issues
- If you see warnings about missing API key, make sure `.env` file exists and contains `GROQ_API_KEY=your_key`
- The dashboard will work without AI insights if the API key is missing, but insights won't be generated
- If you get a "model decommissioned" error, update `GROQ_MODEL_NAME` in `.env` to a current model (check Groq console)

### Package Installation Issues
- Make sure you're using Python 3.10 or higher
- Try: `pip install --upgrade pip` first
- If langchain-groq fails, try: `pip install langchain-groq --upgrade`

### Port Already in Use
- If port 8501 is busy, Streamlit will automatically use the next available port
- Check the terminal output for the correct URL
