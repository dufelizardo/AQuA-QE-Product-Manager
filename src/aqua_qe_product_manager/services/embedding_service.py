import os

import ollama

_DEFAULT_EMBEDDING_MODEL = "bge-m3"


def _client() -> ollama.Client:
    host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ollama.Client(host=host)


def embed(textos: list[str]) -> list[list[float]]:
    modelo = os.getenv("OLLAMA_EMBEDDING_MODEL", _DEFAULT_EMBEDDING_MODEL)
    resposta = _client().embed(model=modelo, input=textos)
    return resposta["embeddings"]
