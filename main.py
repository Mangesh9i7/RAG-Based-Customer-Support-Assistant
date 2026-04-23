import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

from src.graph import app

if __name__ == "__main__":
    print("Welcome! How can i help you?")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        question = input("User:-  ")
        if question.lower() in ['quit', 'exit']:
            break
        
        print("\nThinking...")
        
        # Stream the response chunk by chunk
        for chunk in app.stream(question):
            print(chunk, end="", flush=True)
        print("\n" + "-"*50 + "\n")