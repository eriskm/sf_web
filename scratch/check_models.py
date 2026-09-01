import google.generativeai as genai
import sys

def check_models():
    api_key = 'REDACTED_GOOGLE_API_KEY'
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models()]
        print("MODELS_FOUND:" + ",".join(models))
    except Exception as e:
        print("ERROR_CHECKING:" + str(e))

if __name__ == "__main__":
    check_models()
