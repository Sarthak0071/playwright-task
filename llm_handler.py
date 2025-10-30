import google.generativeai as genai
import re

class LLMHandler:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def extract_url_and_intent(self, user_prompt):
        """
        Use Gemini to extract URL and understand intent from user prompt
        """
        
        system_prompt = """You are a helpful assistant that extracts information from user queries.

Your task:
1. Identify if user wants to find career/job pages
2. Extract the website URL from their message
3. Return response in this EXACT format:

INTENT: [find_careers/unknown]
URL: [extracted_url or none]

Examples:
User: "find career pages from google.com"
INTENT: find_careers
URL: google.com

User: "show me jobs at https://netflix.com"
INTENT: find_careers
URL: https://netflix.com

User: "does spotify have job openings?"
INTENT: find_careers
URL: spotify.com

User: "what's the weather today"
INTENT: unknown
URL: none

Only extract URLs. Add https:// if missing. Keep response short and exact format."""

        try:
            full_prompt = f"{system_prompt}\n\nUser: {user_prompt}"
            response = self.model.generate_content(full_prompt)
            result_text = response.text.strip()
            
            # Parse response
            intent = "unknown"
            url = None
            
            for line in result_text.split('\n'):
                if 'INTENT:' in line:
                    intent = line.split('INTENT:')[1].strip()
                elif 'URL:' in line:
                    url_part = line.split('URL:')[1].strip()
                    if url_part.lower() != 'none':
                        url = url_part
            
            # Add https:// if missing
            if url and not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            return {
                'intent': intent,
                'url': url,
                'raw_response': result_text
            }
        
        except Exception as e:
            return {
                'intent': 'error',
                'url': None,
                'error': str(e)
            }