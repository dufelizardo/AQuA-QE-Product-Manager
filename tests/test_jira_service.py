import httpx

from aqua_qe_product_manager.services import jira_service


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_get_issue_text_extracts_summary_and_description(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    payload = {
        "fields": {
            "summary": "Titulo do ticket",
            "description": {
                "type": "doc",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "Primeira linha."}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": "Segunda linha."}]},
                ],
            },
        }
    }

    def fake_get(url, auth=None, params=None, timeout=None):
        assert url == "https://example.atlassian.net/rest/api/3/issue/PROJ-123"
        assert auth == ("user@example.com", "token")
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx, "get", fake_get)

    resultado = jira_service.get_issue_text("PROJ-123")

    assert "Titulo do ticket" in resultado
    assert "Primeira linha." in resultado
    assert "Segunda linha." in resultado


def test_get_issue_text_handles_missing_description(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    payload = {"fields": {"summary": "Só resumo", "description": None}}
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _FakeResponse(payload))

    assert jira_service.get_issue_text("PROJ-1") == "Só resumo"


def test_get_issue_text_strips_trailing_slash_from_base_url(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net/")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    captured = {}

    def fake_get(url, auth=None, params=None, timeout=None):
        captured["url"] = url
        return _FakeResponse({"fields": {"summary": "s", "description": None}})

    monkeypatch.setattr(httpx, "get", fake_get)

    jira_service.get_issue_text("PROJ-1")

    assert captured["url"] == "https://example.atlassian.net/rest/api/3/issue/PROJ-1"
