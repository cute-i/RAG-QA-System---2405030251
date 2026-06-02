import ollama


def test_ollama_connection():
    print("Testing Ollama connection...")
    try:
        models = ollama.list()
        print("✅ Ollama API is working!")
        print(f"Available models: {[model['name'] for model in models.get('models', [])]}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        print("Please make sure Ollama is running (run 'ollama serve' in terminal)")
        return False


def test_model_response(model_name: str = "deepseek-r1:7b"):
    print(f"\nTesting model: {model_name}")
    try:
        response = ollama.generate(
            model=model_name,
            prompt="Hello! How are you?",
            options={"temperature": 0.7}
        )
        print(f"✅ Model response received!")
        print(f"Response: {response['response']}")
        return True
    except Exception as e:
        print(f"❌ Failed to get response from model: {e}")
        print(f"Please make sure the model is downloaded: ollama pull {model_name}")
        return False


def test_embedding_model(model_name: str = "nomic-embed-text"):
    print(f"\nTesting embedding model: {model_name}")
    try:
        response = ollama.embeddings(model=model_name, prompt="Hello world")
        print(f"✅ Embedding model is working!")
        print(f"Embedding length: {len(response['embedding'])}")
        return True
    except Exception as e:
        print(f"❌ Failed to get embedding: {e}")
        print(f"Please make sure the embedding model is downloaded: ollama pull {model_name}")
        return False


def main():
    print("="*60)
    print("Ollama API Test Script")
    print("="*60)
    
    success_count = 0
    total_tests = 3
    
    success_count += 1 if test_ollama_connection() else 0
    success_count += 1 if test_model_response() else 0
    success_count += 1 if test_embedding_model() else 0
    
    print("\n" + "="*60)
    print(f"Test Summary: {success_count}/{total_tests} tests passed")
    print("="*60)
    
    if success_count == total_tests:
        print("\n🎉 All tests passed! You're ready to use the RAG system.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before using the RAG system.")


if __name__ == "__main__":
    main()
