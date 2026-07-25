from aqua_qe_product_manager.models import JobToBeDone, MarketAnalysis, Persona, ProblemStatement
from aqua_qe_product_manager.workflow import generate_problem_discovery as workflow_module


def test_generate_problem_discovery_chama_as_quatro_skills_e_retorna_tupla(monkeypatch):
    problem_statement = ProblemStatement(problem="problema identificado")
    personas = [Persona(name="Ana")]
    jobs = [JobToBeDone(situation="situacao")]
    market_analysis = MarketAnalysis(market_context="contexto de mercado")

    monkeypatch.setattr(
        workflow_module, "identify_problem_statement", lambda texto: problem_statement
    )
    monkeypatch.setattr(workflow_module, "synthesize_personas", lambda texto: personas)
    monkeypatch.setattr(workflow_module, "extract_jobs_to_be_done", lambda texto: jobs)
    monkeypatch.setattr(
        workflow_module, "extract_market_context", lambda texto: market_analysis
    )

    resultado = workflow_module.generate_problem_discovery("texto de entrada")

    assert resultado == (problem_statement, personas, jobs, market_analysis)


def test_generate_problem_discovery_passa_o_mesmo_texto_para_as_quatro_skills(monkeypatch):
    textos_recebidos = {}

    def _fake(chave, retorno):
        def fake(texto):
            textos_recebidos[chave] = texto
            return retorno

        return fake

    monkeypatch.setattr(
        workflow_module, "identify_problem_statement", _fake("problem_statement", ProblemStatement())
    )
    monkeypatch.setattr(workflow_module, "synthesize_personas", _fake("personas", []))
    monkeypatch.setattr(workflow_module, "extract_jobs_to_be_done", _fake("jobs", []))
    monkeypatch.setattr(workflow_module, "extract_market_context", _fake("market", MarketAnalysis()))

    workflow_module.generate_problem_discovery("texto compartilhado")

    assert textos_recebidos == {
        "problem_statement": "texto compartilhado",
        "personas": "texto compartilhado",
        "jobs": "texto compartilhado",
        "market": "texto compartilhado",
    }
