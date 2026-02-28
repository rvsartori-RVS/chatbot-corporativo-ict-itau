import requests
import time

URL = "http://127.0.0.1:8000/chat"

payload = {
    "question": "Como solicitar férias?"
}

def run_test(n=5):
    print(f"Executando {n} requisições...")

    start = time.time()
    for _ in range(n):
        response = requests.post(URL, json=payload)
        print(response.json())

    end = time.time()
    print(f"Tempo total: {end - start:.2f}s")


if __name__ == "__main__":
    run_test(5)
