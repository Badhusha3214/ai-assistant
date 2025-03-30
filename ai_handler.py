import requests
import json
from config import GEMINI_API_KEY
from rag_handler import RAGHandler

class AIHandler:
    def __init__(self):
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.rag_handler = RAGHandler()
        self.persona = """You are a helpful and friendly receptionist at Kristu Jyoti College. 
        Keep your responses polite, clear, and professional. 
        Avoid using special characters or symbols.
        Start responses with a warm greeting when appropriate."""
        
    def get_response(self, input_text):
        try:
            # Get relevant college context
            rag_context = self.rag_handler.generate_rag_prompt(input_text)
            
            # Create a more conversational prompt
            prompt = f"""{self.persona}

I have access to the following college information for reference:
{rag_context}

Please provide a natural, conversational response to this query: {input_text}

Remember to:
- Answer in your own words as a friendly receptionist
- Use the college information only as reference
- Keep the tone warm and professional
- Be concise and clear"""
            
            url = f"{self.api_url}?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{
                    "parts":[{"text": prompt}]
                }]
            }
            
            response = requests.post(url, 
                                  headers=self.headers,
                                  json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return "Sorry, there was an error processing your request."
                
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "Sorry, there was an error processing your request."
