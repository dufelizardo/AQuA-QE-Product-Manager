from aqua_qe_product_manager.models import ArtifactStatus, GlossaryTerm, PRDDraft, Persona
from aqua_qe_product_manager.workflow import generate_prd as workflow_module


def _draft_valido() -> PRDDraft:
    return PRDDraft(
        context_problem="contexto",
        objective="objetivo",
        scope="escopo",
        functional_requirements=["requisito 1"],
        success_criteria=["criterio 1"],
    )


def _mock_enriquecimento(monkeypatch):
    """Mocka as 10 skills de profundidade chamadas por _enriquecer_prd, para os testes de workflow não dependerem delas."""
    monkeypatch.setattr(workflow_module, "synthesize_personas", lambda texto: [])
    monkeypatch.setattr(workflow_module, "identify_user_journeys", lambda texto: [])
    monkeypatch.setattr(
        workflow_module, "identify_business_objectives", lambda objetivo, criterios: []
    )
    monkeypatch.setattr(workflow_module, "identify_use_cases", lambda texto: [])
    monkeypatch.setattr(workflow_module, "identify_external_dependencies", lambda texto: [])
    monkeypatch.setattr(workflow_module, "identify_technical_assumptions", lambda texto: [])
    monkeypatch.setattr(workflow_module, "identify_constraints", lambda texto: [])
    monkeypatch.setattr(workflow_module, "identify_prd_glossary", lambda texto: [])
    monkeypatch.setattr(workflow_module, "identify_candidate_product_metrics", lambda texto: [])
    monkeypatch.setattr(
        workflow_module, "identify_mvp_scope", lambda requisitos, texto: ([], [])
    )


def _mock_enriquecimento_com_contadores(monkeypatch) -> dict[str, int]:
    """Como _mock_enriquecimento, mas retorna um dict de contadores de chamada por skill,
    para os testes de refino seletivo afirmarem quais skills rodaram e quais não."""
    contadores = {
        "synthesize_personas": 0,
        "identify_user_journeys": 0,
        "identify_business_objectives": 0,
        "identify_use_cases": 0,
        "identify_external_dependencies": 0,
        "identify_technical_assumptions": 0,
        "identify_constraints": 0,
        "identify_prd_glossary": 0,
        "identify_candidate_product_metrics": 0,
        "identify_mvp_scope": 0,
    }

    def _contar(nome, retorno):
        def fake(*args, **kwargs):
            contadores[nome] += 1
            return retorno

        return fake

    monkeypatch.setattr(
        workflow_module, "synthesize_personas", _contar("synthesize_personas", [])
    )
    monkeypatch.setattr(
        workflow_module, "identify_user_journeys", _contar("identify_user_journeys", [])
    )
    monkeypatch.setattr(
        workflow_module,
        "identify_business_objectives",
        _contar("identify_business_objectives", []),
    )
    monkeypatch.setattr(
        workflow_module, "identify_use_cases", _contar("identify_use_cases", [])
    )
    monkeypatch.setattr(
        workflow_module,
        "identify_external_dependencies",
        _contar("identify_external_dependencies", []),
    )
    monkeypatch.setattr(
        workflow_module,
        "identify_technical_assumptions",
        _contar("identify_technical_assumptions", []),
    )
    monkeypatch.setattr(
        workflow_module, "identify_constraints", _contar("identify_constraints", [])
    )
    monkeypatch.setattr(
        workflow_module, "identify_prd_glossary", _contar("identify_prd_glossary", [])
    )
    monkeypatch.setattr(
        workflow_module,
        "identify_candidate_product_metrics",
        _contar("identify_candidate_product_metrics", []),
    )
    monkeypatch.setattr(
        workflow_module, "identify_mvp_scope", _contar("identify_mvp_scope", ([], []))
    )
    return contadores


def _draft_completo() -> PRDDraft:
    """Draft com todos os 9 campos centrais preenchidos com valores distintos, para os testes
    de refino seletivo poderem afirmar 'campo X não mudou' de forma significativa."""
    return PRDDraft(
        context_problem="contexto original",
        objective="objetivo original",
        target_audience="publico original",
        scope="escopo original",
        out_of_scope="fora de escopo original",
        functional_requirements=["rf original"],
        non_functional_requirements=["rnf original"],
        success_criteria=["criterio original"],
        risks_assumptions=["risco original"],
    )


def test_finalize_prd_marca_pending_clarification_quando_validate_falha(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: False)

    resultado = workflow_module.finalize_prd(PRDDraft())

    assert resultado.status == ArtifactStatus.PENDING_CLARIFICATION


def test_finalize_prd_marca_pending_clarification_quando_review_reprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module,
        "review_prd",
        lambda draft: {"aprovado": False, "problemas": ["escopo confuso"]},
    )

    resultado = workflow_module.finalize_prd(_draft_valido())

    assert resultado.status == ArtifactStatus.PENDING_CLARIFICATION
    assert resultado.review_notes == ["escopo confuso"]


def test_finalize_prd_marca_draft_validated_quando_review_aprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    resultado = workflow_module.finalize_prd(_draft_valido())

    assert resultado.status == ArtifactStatus.DRAFT_VALIDATED


def test_generate_prd_draft_gera_e_finaliza(monkeypatch):
    _mock_enriquecimento(monkeypatch)
    monkeypatch.setattr(
        workflow_module, "generate_prd", lambda ideia, contexto=None: _draft_valido()
    )
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    draft = workflow_module.generate_prd_draft("uma ideia qualquer")

    assert draft.status == ArtifactStatus.DRAFT_VALIDATED
    assert draft.objective == "objetivo"


def test_generate_prd_draft_aceita_contexto_opcional(monkeypatch):
    _mock_enriquecimento(monkeypatch)
    capturado = {}

    def fake_generate_prd(ideia, contexto=None):
        capturado["contexto"] = contexto
        return _draft_valido()

    monkeypatch.setattr(workflow_module, "generate_prd", fake_generate_prd)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    workflow_module.generate_prd_draft("uma ideia qualquer", {"vision_statement": "s"})

    assert capturado["contexto"] == {"vision_statement": "s"}


def test_generate_prd_draft_reaproveita_personas_da_descoberta(monkeypatch):
    """Se contexto ja tem personas (da fase de descoberta), nao chama synthesize_personas de novo."""
    chamou_synthesize = {"valor": False}

    def fake_synthesize(texto):
        chamou_synthesize["valor"] = True
        return []

    _mock_enriquecimento(monkeypatch)
    monkeypatch.setattr(workflow_module, "synthesize_personas", fake_synthesize)
    monkeypatch.setattr(
        workflow_module, "generate_prd", lambda ideia, contexto=None: _draft_valido()
    )
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    draft = workflow_module.generate_prd_draft(
        "uma ideia qualquer", {"personas": ["persona da descoberta"]}
    )

    assert chamou_synthesize["valor"] is False
    assert draft.personas == ["persona da descoberta"]


def test_refine_prd_draft_refina_e_finaliza(monkeypatch):
    _mock_enriquecimento(monkeypatch)

    def fake_refine_prd(draft, respostas):
        draft.objective = "objetivo refinado"
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    draft = workflow_module.refine_prd_draft(
        _draft_valido(), [{"pergunta": "qual objetivo?", "resposta": "objetivo refinado"}]
    )

    assert draft.objective == "objetivo refinado"
    assert draft.status == ArtifactStatus.DRAFT_VALIDATED


# --- _campos_centrais_alterados -------------------------------------------


def test_campos_centrais_alterados_sem_diferenca():
    draft = _draft_completo()
    antes = workflow_module._capturar_campos_centrais(draft)

    assert workflow_module._campos_centrais_alterados(antes, draft) == set()


def test_campos_centrais_alterados_string_diferente():
    draft = _draft_completo()
    antes = workflow_module._capturar_campos_centrais(draft)
    draft.risks_assumptions = ["risco novo"]

    assert workflow_module._campos_centrais_alterados(antes, draft) == {"risks_assumptions"}


def test_campos_centrais_alterados_lista_reordenada_conta_como_alterado():
    """Escolha deliberadamente conservadora: reordenar uma lista já conta como mudança,
    mesmo com o mesmo conteúdo — nunca subestimar o que pode ter mudado."""
    draft = PRDDraft(functional_requirements=["a", "b"])
    antes = workflow_module._capturar_campos_centrais(draft)
    draft.functional_requirements = ["b", "a"]

    assert "functional_requirements" in workflow_module._campos_centrais_alterados(antes, draft)


def test_campos_centrais_alterados_vazio_para_populado():
    draft = PRDDraft()
    antes = workflow_module._capturar_campos_centrais(draft)
    draft.success_criteria = ["novo criterio"]

    assert "success_criteria" in workflow_module._campos_centrais_alterados(antes, draft)


# --- Refino seletivo dos campos de profundidade ---------------------------


def test_refine_prd_draft_mudanca_estreita_so_roda_skills_mapeadas(monkeypatch):
    """Só risks_assumptions muda -> só as skills mapeadas para esse campo
    (technical_assumptions, constraints) rodam; as outras 8 não."""
    contadores = _mock_enriquecimento_com_contadores(monkeypatch)

    def fake_refine_prd(draft, respostas):
        draft.risks_assumptions = ["risco novo, esclarecido pela resposta"]
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    draft_entrada = _draft_completo()
    draft_entrada.personas = [Persona(name="Persona preexistente")]
    draft_entrada.glossary = [GlossaryTerm(term="Termo preexistente")]

    draft = workflow_module.refine_prd_draft(draft_entrada, [{"pergunta": "p", "resposta": "r"}])

    assert contadores["identify_technical_assumptions"] == 1
    assert contadores["identify_constraints"] == 1
    assert contadores["synthesize_personas"] == 0
    assert contadores["identify_user_journeys"] == 0
    assert contadores["identify_business_objectives"] == 0
    assert contadores["identify_use_cases"] == 0
    assert contadores["identify_external_dependencies"] == 0
    assert contadores["identify_prd_glossary"] == 0
    assert contadores["identify_candidate_product_metrics"] == 0
    assert contadores["identify_mvp_scope"] == 0
    # campos não tocados mantêm o valor de entrada, não são limpos
    assert draft.personas == [Persona(name="Persona preexistente")]
    assert draft.glossary == [GlossaryTerm(term="Termo preexistente")]


def test_refine_prd_draft_business_objectives_escopo_exato(monkeypatch):
    contadores = _mock_enriquecimento_com_contadores(monkeypatch)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    def fake_refine_prd_sem_tocar_objective(draft, respostas):
        draft.risks_assumptions = ["risco novo"]
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd_sem_tocar_objective)
    workflow_module.refine_prd_draft(_draft_completo(), [{"pergunta": "p", "resposta": "r"}])
    assert contadores["identify_business_objectives"] == 0

    contadores2 = _mock_enriquecimento_com_contadores(monkeypatch)

    def fake_refine_prd_muda_objective(draft, respostas):
        draft.objective = "objetivo novo"
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd_muda_objective)
    workflow_module.refine_prd_draft(_draft_completo(), [{"pergunta": "p", "resposta": "r"}])
    assert contadores2["identify_business_objectives"] == 1


def test_refine_prd_draft_mvp_scope_escopo_misto(monkeypatch):
    contadores = _mock_enriquecimento_com_contadores(monkeypatch)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    def fake_refine_prd_sem_tocar_fr(draft, respostas):
        draft.risks_assumptions = ["risco novo"]
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd_sem_tocar_fr)
    workflow_module.refine_prd_draft(_draft_completo(), [{"pergunta": "p", "resposta": "r"}])
    assert contadores["identify_mvp_scope"] == 0

    contadores2 = _mock_enriquecimento_com_contadores(monkeypatch)

    def fake_refine_prd_muda_fr(draft, respostas):
        draft.functional_requirements = ["rf novo"]
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd_muda_fr)
    workflow_module.refine_prd_draft(_draft_completo(), [{"pergunta": "p", "resposta": "r"}])
    assert contadores2["identify_mvp_scope"] == 1


def test_refine_prd_draft_snapshot_e_capturado_antes_da_mutacao(monkeypatch):
    """Regressão crítica: refine_prd muta o mesmo objeto que recebe (não retorna uma cópia).
    Se o snapshot fosse capturado depois da chamada, nenhuma mudança jamais seria detectada."""
    contadores = _mock_enriquecimento_com_contadores(monkeypatch)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    def fake_refine_prd_muta_em_lugar(draft, respostas):
        draft.context_problem = "contexto novo"  # muta o mesmo objeto, não retorna cópia
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd_muta_em_lugar)
    workflow_module.refine_prd_draft(_draft_completo(), [{"pergunta": "p", "resposta": "r"}])

    # personas e glossary estão mapeados para context_problem -> devem rodar
    assert contadores["synthesize_personas"] == 1
    assert contadores["identify_prd_glossary"] == 1


def test_refine_prd_draft_tudo_mudou_roda_todas_as_10_skills(monkeypatch):
    """Guarda de regressão do fix de obsolescência original: se todos os 9 campos centrais
    mudarem, as 10 skills de profundidade devem continuar rodando, igual ao comportamento
    de antes desta otimização."""
    contadores = _mock_enriquecimento_com_contadores(monkeypatch)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    def fake_refine_prd_muda_tudo(draft, respostas):
        draft.context_problem = "novo"
        draft.objective = "novo"
        draft.target_audience = "novo"
        draft.scope = "novo"
        draft.out_of_scope = "novo"
        draft.functional_requirements = ["novo"]
        draft.non_functional_requirements = ["novo"]
        draft.success_criteria = ["novo"]
        draft.risks_assumptions = ["novo"]
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd_muda_tudo)
    workflow_module.refine_prd_draft(_draft_completo(), [{"pergunta": "p", "resposta": "r"}])

    assert all(contador == 1 for contador in contadores.values())


def test_refine_prd_draft_forcar_rederivacao_completa_ignora_o_mapa(monkeypatch):
    """Mesmo com uma mudança estreita (só risks_assumptions), forcar_rederivacao_completa=True
    roda as 10 skills de qualquer forma — válvula de escape."""
    contadores = _mock_enriquecimento_com_contadores(monkeypatch)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    def fake_refine_prd(draft, respostas):
        draft.risks_assumptions = ["risco novo"]
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd)
    workflow_module.refine_prd_draft(
        _draft_completo(),
        [{"pergunta": "p", "resposta": "r"}],
        forcar_rederivacao_completa=True,
    )

    assert all(contador == 1 for contador in contadores.values())


def test_generate_prd_draft_sempre_roda_todas_as_10_skills(monkeypatch):
    """A geração inicial não recebe campos_alterados (não há 'antes' pra comparar) -> deve
    sempre rodar as 10 skills incondicionalmente, sem regressão desta otimização."""
    contadores = _mock_enriquecimento_com_contadores(monkeypatch)
    monkeypatch.setattr(
        workflow_module, "generate_prd", lambda ideia, contexto=None: _draft_completo()
    )
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    workflow_module.generate_prd_draft("uma ideia qualquer")

    assert all(contador == 1 for contador in contadores.values())
