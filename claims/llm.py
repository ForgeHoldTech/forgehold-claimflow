import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

SYSTEM_PROMPT = (
    "You are an assistant for a healthcare claims team. "
    "Answer only using the denial letters provided. "
    "If the answer is not in the letters, say that you do not know. "
    "Keep the answer short and clear."
)

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "Denial letters:\n{context}\n\nQuestion: {question}"),
    ]
)


class LLMUnavailableError(Exception):
    pass


def build_chain():
    model = ChatOllama(
        model=os.environ.get("OLLAMA_MODEL", "llama3.2:3b"),
        base_url=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434"),
        temperature=0,
    )
    return PROMPT | model | StrOutputParser()


def answer_question(question, letters):
    context = "\n\n".join(
        f"[{letter.claim.claim_number}] {letter.title}: {letter.content}"
        for letter in letters
    )
    try:
        return build_chain().invoke({"context": context, "question": question})
    except Exception as error:
        raise LLMUnavailableError(str(error)) from error