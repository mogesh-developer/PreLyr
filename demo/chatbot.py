import requests


PRELYR_API = "http://127.0.0.1:8000"


def send_message(text: str):
    response = requests.post(
        f"{PRELYR_API}/generate",
        json={"text": text},
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def main():
    print("PreLyr Demo Chatbot")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            break

        if not user_input:
            continue

        result = send_message(user_input)

        print(f"\nAssistant: {result['response']}")
        print("\n--- PreLyr ---")
        print(result["optimized_prompt"])
        print("----------------\n")


if __name__ == "__main__":
    main()