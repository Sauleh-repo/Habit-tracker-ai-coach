import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def diagnose():
    print(f"--- Deep API Diagnostic ---")
    client = genai.Client(api_key=api_key)
    
    try:
        models = list(client.models.list())
        print(f"Found {len(models)} models available to your key.\n")
        
        print(f"{'MODEL NAME':<40} | {'CAN EMBED?':<10} | {'CAN CHAT?'}")
        print("-" * 70)
        
        for m in models:
            # Check for embedding support
            # The attribute name can vary by SDK version, so we check for methods
            # Use 'embedContent' or 'embed_content'
            methods = str(m) # Look at the raw object string
            can_embed = "embedContent" in methods
            can_chat = "generateContent" in methods
            
            # Print any model that has Flash or Embedding in the name
            if "flash" in m.name.lower() or "embed" in m.name.lower():
                embed_status = "✅ YES" if can_embed else "❌ NO"
                chat_status = "✅ YES" if can_chat else "❌ NO"
                print(f"{m.name:<40} | {embed_status:<10} | {chat_status}")

    except Exception as e:
        print(f"Diagnostic failed: {e}")

if __name__ == "__main__":
    diagnose()