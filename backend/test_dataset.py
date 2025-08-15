import requests

def test_huggingface_api():
    """Test the HuggingFace mental health dataset API"""
    url = "https://datasets-server.huggingface.co/rows?dataset=marmikpandya%2Fmental-health&config=default&split=train&offset=0&length=10"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            rows = data.get('rows', [])
            print(f"✅ Successfully loaded {len(rows)} rows from mental health dataset")
            
            # Show first few examples
            for i, row in enumerate(rows[:3]):
                print(f"\nExample {i+1}:")
                print(f"Data: {row['row']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_huggingface_api()