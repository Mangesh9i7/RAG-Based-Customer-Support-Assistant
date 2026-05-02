import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

from src.graph import app

# Define the exact trigger phrase we set in prompts.py
HITL_TRIGGER = "Let me connect you with a human"

if __name__ == "__main__":
    print("Welcome! How can I help you?")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        question = input("User:-  ")
        if question.lower() in ['quit', 'exit']:
            break
        
        print("\nThinking...")
        
        # 1. Create an empty string to capture the full AI response
        full_response = ""
        
        # 2. Stream the response chunk by chunk as usual
        for chunk in app.stream(question):
            print(chunk, end="", flush=True)
            full_response += chunk 
            
        print("\n" + "-"*50)
        
        # 3. Check if the AI used the trigger phrase
        if HITL_TRIGGER in full_response:
            print("🚨 [SYSTEM ALERT]: Triggering Human-in-the-Loop routing... 🚨")
            print("=> Notification sent to support team for review.\n")