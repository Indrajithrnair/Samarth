# Project Samarth - Government Data Q&A System

An intelligent Q&A system that analyzes agricultural and climate data from the Indian Government's data.gov.in portal.

## Features

- 🤖 Natural language query processing
- 🌾 Agricultural production data analysis
- 🌧️ Climate and rainfall pattern analysis
- 📊 Cross-domain data correlation
- 🔍 Source citation and traceability
- 💬 Simple chat interface

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Open Browser**
   Navigate to `http://localhost:8000`

## Sample Questions

- "Compare rice production in Maharashtra and Punjab for 2023"
- "What is the rainfall pattern in Maharashtra districts?"
- "Show me crop production data for wheat in northern states"
- "Analyze the relationship between rainfall and rice production"

## Architecture

```
Frontend (HTML/JS) → FastAPI Backend → Data Scraper → Government APIs
                                    ↓
                              Query Processor → Response Generator
```

## Current Implementation Status

✅ **Completed:**
- Real data.gov.in API integration with fallback to enhanced mock data
- Intelligent caching system (1 hour for general data, 30 min for prices)
- Multi-source data correlation (Agriculture + Climate + Market Prices)
- Natural language query processing with entity extraction
- Source citation and traceability
- Responsive web interface

🔄 **Current Data Sources:**
- **Agricultural**: Ministry of Agriculture & Farmers Welfare datasets
- **Climate**: India Meteorological Department rainfall/weather data  
- **Market**: Current daily prices from mandis across India
- **Fallback**: Enhanced realistic mock data when APIs are unavailable

## Next Production Enhancements

1. **Enhanced NLP**: Integrate OpenAI/local LLMs for better query understanding
2. **Database**: PostgreSQL for better data management and analytics
3. **Real-time Updates**: Scheduled data refresh from government sources
4. **Advanced Analytics**: Trend analysis, correlation algorithms
5. **Authentication**: User management and API rate limiting

## Configuration

For production use, you'll need to:
1. Set up OpenAI API key in `query_processor.py`
2. Implement real data.gov.in scraping logic
3. Add proper error handling and logging

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: Pandas, BeautifulSoup
- **AI**: OpenAI API (for production)