# AI Career Page Finder

A web application that helps users find career and job pages on company websites using natural language queries.

## Features

- **Natural Language Interface**: Ask in plain English to find career pages on any website
- **Intelligent URL Extraction**: Automatically extracts website URLs from your queries
- **Smart Scraping**: Uses AI to identify and locate career/job pages on websites
- **Interactive Results**: View and explore discovered career pages directly in the app

## Technology Stack

- **Google Gemini 2.5 Flash**: Powers the natural language understanding
- **Playwright**: Handles web scraping and browser automation
- **Streamlit**: Provides the interactive web interface
- **Python**: Core programming language

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```
   playwright install
   ```
4. Create a `.env` file in the project root with your API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the application:
   ```
   streamlit run app.py
   ```
2. Open your browser and navigate to the provided URL (typically http://localhost:8501)
3. Type natural language queries like:
   - "Find career pages from google.com"
   - "Show me jobs at netflix.com"
   - "Does spotify have job openings?"

## Project Structure

- `app.py`: Main Streamlit application
- `scraper.py`: Web scraping functionality using Playwright
- `llm_handler.py`: Integration with Google Gemini API
- `.env`: Environment variables (API keys)

## Requirements

- Python 3.8+
- Playwright
- Streamlit
- Google Gemini API key

## License

This project is for educational and personal use.