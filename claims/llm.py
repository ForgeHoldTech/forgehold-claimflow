import os

import requests


def answer_question(question, letters):
    context = "\n\n".join(
        f"[{letter.claim.claim_number}] {letter.title}: {letter.content}"
        for letter in letters
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant for a healthcare claims team. "
                "Answer only using the denial letters provided. "
                "If the answer is not in the letters, say that you do not know. "
                "Keep the answer short and clear."
            ),
        },
        {
            "role": "user",
            "content": f"Denial letters:\n{context}\n\nQuestion: {question}",
        },
    ]
    base_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
    model = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
    response = requests.post(
        f"{base_url}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]