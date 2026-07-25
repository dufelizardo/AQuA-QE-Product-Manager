from aqua_qe_product_manager.models import PRDDraft
from aqua_qe_product_manager.skills import generate_prd_clarifying_questions as module


def test_returns_empty_list_without_review_notes():
    assert module.generate_prd_clarifying_questions(PRDDraft()) == []


def test_maps_json_response_to_question_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"perguntas": ["Qual o publico-alvo?"]},
    )

    draft = PRDDraft(objective="o", scope="e", review_notes=["publico-alvo indefinido"])
    resultado = module.generate_prd_clarifying_questions(draft)

    assert resultado == ["Qual o publico-alvo?"]


def test_normalizes_questions_returned_as_objects(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "perguntas": [{"texto": "Qual o publico-alvo?"}, {"pergunta": "Qual o escopo?"}]
        },
    )

    draft = PRDDraft(objective="o", scope="e", review_notes=["publico-alvo indefinido"])
    resultado = module.generate_prd_clarifying_questions(draft)

    assert resultado == ["Qual o publico-alvo?", "Qual o escopo?"]


def test_normalizes_questions_with_capitalized_keys(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "perguntas": [{"Pergunta": "Qual o publico-alvo?", "Razão": "porque sim"}]
        },
    )

    draft = PRDDraft(objective="o", scope="e", review_notes=["publico-alvo indefinido"])
    resultado = module.generate_prd_clarifying_questions(draft)

    assert resultado == ["Qual o publico-alvo?"]
