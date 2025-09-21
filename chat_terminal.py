import requests

API_URL = "http://127.0.0.1:8000/chat"

print("BundesFAQ Chatbot")
print("Tippe deine Fragen. Mit 'exit' oder 'quit' beenden.\n")

while True:
    question = input("Du: ")
    if question.lower() in ["exit", "quit", "q"]:
        print("Auf Wiedersehen!")
        break

    try:
        response = requests.post(API_URL, json={"question": question})
        if response.status_code == 200:
            data = response.json()
            print(f"Bot: {data['answer']} ({data['sources_count']} Quellen)\n")
        else:
            print(f"Fehler {response.status_code}: {response.text}")
    except Exception as e:
        print(f"API nicht erreichbar: {e}")
        break
