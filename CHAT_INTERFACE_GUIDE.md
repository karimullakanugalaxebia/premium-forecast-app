# Chat Interface Guide

## Overview

The dashboard includes a **chat-based interface** that allows you to control the dashboard using natural language queries instead of manually adjusting filters and settings. The chat interface is accessible via a floating button in the bottom-right corner of the dashboard.

## How to Use

### 1. Access Chat Interface

1. Look for the chat icon (💬) in the bottom-right corner of the dashboard
2. Click the icon to open the chat window
3. Type your query in natural language
4. The dashboard will automatically update based on your query

### 2. Example Queries

#### Filter by Demographics
- `"Show me forecast for males aged 30-50"`
- `"What about family policies?"`
- `"Show term life insurance for females"`
- `"Corporate policies aged 40-60"`

#### Smoking Status Filter
- `"Show forecast for non-smokers"`
- `"What about smokers aged 30-50?"`
- `"Non-smoker males with term life"`

#### Sum Insured Filter
- `"Forecast for sum insured 1 crore"`
- `"Show premiums for 50 lakh coverage"`
- `"What about 25 lakh sum insured?"`

#### Combined Queries (Recommended)
- `"forecast for males age 30 years with sum insured 1cr, policy type whole life with non smoker"`
- `"Show me forecast for males aged 30-50 in optimistic scenario"`
- `"Compare all scenarios for family term life policies"`
- `"Non-smoker females with 50 lakh coverage aged 25-45"`

#### Scenario Selection
- `"Show optimistic scenario"`
- `"Compare all scenarios"`
- `"What's the pessimistic case for term life?"`

#### Time Period
- `"Show forecast from 2025 to 2030"`
- `"What's the 10-year forecast for males?"`

## How It Works

1. **Natural Language Processing**: Uses Groq LLM to parse your query
2. **Parameter Extraction**: Identifies filters, scenarios, and time periods
3. **Automatic Updates**: Updates sidebar filters and dashboard automatically
4. **Chat History**: Shows last 5 messages for context

## Technical Details

### Parsed Parameters

The chat interface extracts:
- `start_year` / `end_year`: Forecast period
- `scenario`: "base", "optimistic", or "pessimistic"
- `group`: "Individual", "Family", "Corporate"
- `gender`: "Male", "Female"
- `policy_type`: "Term Life", "Whole Life"
- `smoking_status`: "Smoker", "Non-Smoker"
- `sum_insured`: Numeric value (e.g., 1000000 for ₹10L, 10000000 for ₹1Cr)
- `age_min` / `age_max`: Age range
- `compare_all`: Boolean for scenario comparison

### Sum Insured Parsing

The chat interface recognizes:
- "10 lakh", "10l", "10 l" → ₹10 Lakh (1,000,000)
- "25 lakh", "25l", "25 l" → ₹25 Lakh (2,500,000)
- "50 lakh", "50l", "50 l" → ₹50 Lakh (5,000,000)
- "1 crore", "1cr", "1 cr", "1crore" → ₹1 Crore (10,000,000)
- "2 crore", "2cr", "2 cr", "2crore" → ₹2 Crore (20,000,000)

### Fallback Parsing

If the LLM fails, the system uses regex-based fallback parsing to extract common patterns.

## Requirements

- `GROQ_API_KEY` must be set in `.env` file
- Same API key used for AI insights

## Tips

1. **Be Specific**: More specific queries work better
   - ✅ Good: "Show forecast for males aged 30-50"
   - ❌ Vague: "Show me something"

2. **Combine Filters**: You can combine multiple filters
   - ✅ "Family term life for females aged 25-45"

3. **Scenario Names**: Use clear scenario names
   - ✅ "optimistic scenario"
   - ✅ "compare all scenarios"

4. **Age Ranges**: Specify age ranges clearly
   - ✅ "ages 30 to 50"
   - ✅ "30-50 years old"

## Troubleshooting

**Chat not working?**
- Check that `GROQ_API_KEY` is set in `.env`
- Ensure the checkbox is enabled
- Try rephrasing your query

**Wrong filters applied?**
- The chat uses LLM parsing which may occasionally misinterpret
- You can manually adjust filters in the sidebar
- Try being more explicit in your query

**No response?**
- Check your internet connection
- Verify Groq API key is valid
- Try a simpler query first

## Examples

### Example 1: Simple Demographic Filter
**Query**: `"Show me forecast for males"`

**Result**: 
- Gender filter set to "Male"
- Dashboard updates to show male-only forecasts

### Example 2: Age Range
**Query**: `"What about ages 30-50?"`

**Result**:
- Age min: 30
- Age max: 50
- Dashboard filters to this age range

### Example 3: Scenario Comparison
**Query**: `"Compare all scenarios for term life"`

**Result**:
- Scenario mode: "Compare All Scenarios"
- Policy type: "Term Life"
- Shows comparison chart with all three scenarios

### Example 4: Complex Query with Smoking Status
**Query**: `"Show optimistic forecast for family term life policies for non-smoker females aged 25-45"`

**Result**:
- Scenario: Optimistic
- Group: Family
- Policy Type: Term Life
- Gender: Female
- Smoking Status: Non-Smoker
- Age: 25-45
- All filters applied simultaneously

### Example 5: Complete Query with Sum Insured
**Query**: `"forecast for males age 30 years with sum insured 1cr, policy type whole life with non smoker"`

**Result**:
- Gender: Male
- Age: 30 (expanded to 25-35 range)
- Sum Insured: ₹1 Crore (10,000,000)
- Policy Type: Whole Life
- Smoking Status: Non-Smoker
- All filters applied, premiums calculated for ₹1 Crore coverage

---

**Enjoy the chat interface!** 🎉
