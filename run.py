# run.py
from src.config import settings

def main():
    print("OpenAI Key:", settings.OPENAI_API_KEY[:10], "...")
    print("Weaviate URL:", settings.WEAVIATE_URL)

if __name__ == "__main__":
    main()
