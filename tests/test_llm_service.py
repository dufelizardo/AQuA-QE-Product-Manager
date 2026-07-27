import pytest

from aqua_qe_product_manager.services import llm_service


def test_generator_model_default_is_ollama(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    assert llm_service.generator_model() == "mistral"


def test_reviewer_model_default_is_ollama(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OLLAMA_REVIEW_MODEL", raising=False)

    assert llm_service.reviewer_model() == "phi4"


def test_generator_model_uses_nvidia_default_when_provider_is_nvidia(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.delenv("NVIDIA_MODEL", raising=False)

    assert llm_service.generator_model() == "deepseek-ai/deepseek-v4-pro"


def test_reviewer_model_uses_nvidia_default_when_provider_is_nvidia(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.delenv("NVIDIA_REVIEW_MODEL", raising=False)

    assert llm_service.reviewer_model() == "meta/llama-3.3-70b-instruct"


def test_generator_model_respects_explicit_nvidia_model_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.setenv("NVIDIA_MODEL", "meu-modelo-customizado")

    assert llm_service.generator_model() == "meu-modelo-customizado"


def test_complete_json_dispatches_to_ollama_by_default(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    captured = {}

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            captured["model"] = model
            captured["messages"] = messages
            captured["kwargs"] = kwargs
            return {"message": {"content": '{"ok": true}'}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    resultado = llm_service.complete_json("pergunta", system="sistema")

    assert resultado == {"ok": True}
    assert captured["model"] == "mistral"
    assert captured["kwargs"] == {"format": "json"}
    assert captured["messages"] == [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pergunta"},
    ]


def test_complete_dispatches_to_ollama_without_json_format(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    captured = {}

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            captured["kwargs"] = kwargs
            return {"message": {"content": "resposta em texto"}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    resultado = llm_service.complete("pergunta")

    assert resultado == "resposta em texto"
    assert captured["kwargs"] == {}


def test_complete_json_dispatches_to_nvidia_when_provider_is_nvidia(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    captured = {}

    class FakeMessage:
        content = '{"ok": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["model"] = model
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeNvidiaClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_nvidia_client", lambda: FakeNvidiaClient())

    resultado = llm_service.complete_json("pergunta")

    assert resultado == {"ok": True}
    assert captured["model"] == "deepseek-ai/deepseek-v4-pro"
    assert captured["kwargs"] == {"response_format": {"type": "json_object"}}


def test_complete_json_uses_deepseek_reasoning_params_when_explicitly_selected(monkeypatch):
    """deepseek-ai/deepseek-v4-flash não é mais o default (503 de capacidade em teste ao vivo),
    mas continua com params dedicados em _NVIDIA_MODEL_PARAMS caso seja selecionado manualmente."""
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    captured = {}

    class FakeMessage:
        content = '{"ok": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["model"] = model
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeNvidiaClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_nvidia_client", lambda: FakeNvidiaClient())

    resultado = llm_service.complete_json("pergunta", model="deepseek-ai/deepseek-v4-flash")

    assert resultado == {"ok": True}
    assert captured["model"] == "deepseek-ai/deepseek-v4-flash"
    assert captured["kwargs"] == {
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 16384,
        "extra_body": {"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}},
        "response_format": {"type": "json_object"},
    }


def test_complete_json_uses_reviewer_model_without_dedicated_params_on_nvidia(monkeypatch):
    """meta/llama-3.3-70b-instruct não tem entrada em _NVIDIA_MODEL_PARAMS — só response_format."""
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    captured = {}

    class FakeMessage:
        content = '{"aprovado": true}'

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["model"] = model
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeNvidiaClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_nvidia_client", lambda: FakeNvidiaClient())

    llm_service.complete_json("pergunta", model=llm_service.reviewer_model())

    assert captured["model"] == "meta/llama-3.3-70b-instruct"
    assert captured["kwargs"] == {"response_format": {"type": "json_object"}}


def test_nvidia_unrecognized_model_falls_back_to_no_extra_params(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    captured = {}

    class FakeMessage:
        content = "resposta em texto"

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            captured["kwargs"] = kwargs

            class FakeResponse:
                choices = [FakeChoice()]

            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeNvidiaClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_service, "_nvidia_client", lambda: FakeNvidiaClient())

    llm_service.complete("pergunta", model="algum/modelo-desconhecido")

    assert captured["kwargs"] == {}


def test_complete_json_raises_on_invalid_json_regardless_of_provider(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            return {"message": {"content": "isto não é json"}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    with pytest.raises(ValueError):
        llm_service.complete_json("pergunta")


def test_explicit_model_argument_overrides_generator_model(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    captured = {}

    class FakeOllamaClient:
        def chat(self, model, messages, **kwargs):
            captured["model"] = model
            return {"message": {"content": '{"ok": true}'}}

    monkeypatch.setattr(llm_service, "_ollama_client", lambda: FakeOllamaClient())

    llm_service.complete_json("pergunta", model="modelo-especifico")

    assert captured["model"] == "modelo-especifico"
