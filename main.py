import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

from src.graph import app

if __name__ == "__main__":
    print("Welcome to the Free Groq-powered RAG system!")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        question = input("Ask a question: ")
        if question.lower() in ['quit', 'exit']:
            break
        
        print("\nThinking...")
        
        # Stream the response chunk by chunk
        for chunk in app.stream(question):
            print(chunk, end="", flush=True)
        print("\n" + "-"*50 + "\n")