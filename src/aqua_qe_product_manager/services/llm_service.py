import json
import os

import ollama
from openai import OpenAI

_DEFAULT_MODEL = "mistral"
_DEFAULT_REVIEW_MODEL = "phi4"
_DEFAULT_NVIDIA_MODEL = "deepseek-ai/deepseek-v4-pro"
_DEFAULT_NVIDIA_REVIEW_MODEL = "meta/llama-3.3-70b-instruct"
_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
# Fallback documentado se deepseek-v4-pro também saturar por capacidade (mesma família do
# -flash, que saturou durante o piloto): openai/gpt-oss-120b, confirmado acessível nesta conta.
# Não trocado proativamente porque não houve evidência de problema com o -pro ainda.

# Parâmetros de sampling recomendados pela NVIDIA por modelo NIM (build.nvidia.com/playground)
# — chaveados por nome do modelo, não por papel (gerador/revisor), para continuar corretos se
# um dos dois for trocado via NVIDIA_MODEL/NVIDIA_REVIEW_MODEL. Modelo sem entrada aqui usa a
# chamada sem parâmetros extras (só model/messages/response_format).
# Nota: deepseek-ai/deepseek-v4-flash não é mais o default do gerador (503 "Worker local total
# request limit reached" em duas tentativas ao vivo durante o piloto) — entrada mantida caso o
# usuário selecione esse modelo manualmente via NVIDIA_MODEL.
_NVIDIA_MODEL_PARAMS: dict[str, dict] = {
    "deepseek-ai/deepseek-v4-flash": {
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 16384,
        "extra_body": {"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}},
    },
}


def _nvidia_params(modelo: str) -> dict:
    return dict(_NVIDIA_MODEL_PARAMS.get(modelo, {}))


def _provider() -> str:
    return os.getenv("LLM_PROVIDER", "ollama")


def _ollama_client() -> ollama.Client:
    host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ollama.Client(host=host)


def _nvidia_client() -> OpenAI:
    return OpenAI(base_url=_NVIDIA_BASE_URL, api_key=os.environ["NVIDIA_API_KEY"])


def generator_model() -> str:
    """Resolve o modelo gerador conforme o provedor ativo (LLM_PROVIDER=ollama|nvidia)."""
    if _provider() == "nvidia":
        return os.getenv("NVIDIA_MODEL", _DEFAULT_NVIDIA_MODEL)
    return os.getenv("OLLAMA_MODEL", _DEFAULT_MODEL)


def reviewer_model() -> str:
    """Resolve o modelo revisor conforme o provedor ativo (LLM_PROVIDER=ollama|nvidia)."""
    if _provider() == "nvidia":
        return os.getenv("NVIDIA_REVIEW_MODEL", _DEFAULT_NVIDIA_REVIEW_MODEL)
    return os.getenv("OLLAMA_REVIEW_MODEL", _DEFAULT_REVIEW_MODEL)


def _chat(modelo: str, messages: list[dict], json_mode: bool) -> str:
    if _provider() == "nvidia":
        kwargs = _nvidia_params(modelo)
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resposta = _nvidia_client().chat.completions.create(
            model=modelo, messages=messages, **kwargs
        )
        return resposta.choices[0].message.content

    kwargs = {"format": "json"} if json_mode else {}
    resposta = _ollama_client().chat(model=modelo, messages=messages, **kwargs)
    return resposta["message"]["content"]


def complete(prompt: str, system: str = "", model: str | None = None) -> str:
    """Envia um prompt ao provedor de LLM ativo (Ollama ou NVIDIA NIM) e retorna o texto de resposta."""
    modelo = model or generator_model()
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    return _chat(modelo, messages, json_mode=False)


def complete_json(prompt: str, system: str = "", model: str | None = None) -> dict:
    """Envia um prompt ao provedor de LLM ativo e retorna a resposta já parseada como JSON."""
    modelo = model or generator_model()
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    conteudo = _chat(modelo, messages, json_mode=True)
    try:
        return json.loads(conteudo)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Resposta do LLM não é um JSON válido: {conteudo!r}") from exc
