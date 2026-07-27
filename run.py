"""CLI simples para rodar o AQuA-QE Product Manager sem precisar mexer em sys.path manualmente."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

_RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(_RAIZ / "src"))
load_dotenv(_RAIZ / ".env")

from aqua_qe_product_manager.models import (  # noqa: E402
    MOSCOW_CATEGORIAS,
    ArtifactStatus,
    JobToBeDone,
    MarketAnalysis,
    PRDDraft,
    Persona,
    PrioritizedRequirement,
    PriorityInputs,
    ProblemStatement,
    ProductStrategy,
    ProductVision,
)
from aqua_qe_product_manager.orchestrator.product_manager import (  # noqa: E402
    handle_discovery,
    handle_existing_prd,
    handle_moscow_classification,
    handle_prd,
    handle_strategy,
    handle_vision,
)
from aqua_qe_product_manager.skills.compute_rice_score import compute_rice_score  # noqa: E402
from aqua_qe_product_manager.skills.compute_wsjf_score import compute_wsjf_score  # noqa: E402
from aqua_qe_product_manager.skills.create_confluence_page import (  # noqa: E402
    create_confluence_page,
)
from aqua_qe_product_manager.skills.export_markdown import export_markdown  # noqa: E402
from aqua_qe_product_manager.skills.format_chat_transcript import (  # noqa: E402
    format_chat_transcript,
)
from aqua_qe_product_manager.skills.format_prd_markdown import format_prd_markdown  # noqa: E402
from aqua_qe_product_manager.skills.generate_prd_clarifying_questions import (  # noqa: E402
    generate_prd_clarifying_questions,
)
from aqua_qe_product_manager.skills.generate_strategy_clarifying_questions import (  # noqa: E402
    generate_strategy_clarifying_questions,
)
from aqua_qe_product_manager.skills.generate_vision_clarifying_questions import (  # noqa: E402
    generate_vision_clarifying_questions,
)
from aqua_qe_product_manager.skills.parse_chat_transcript import parse_chat_transcript  # noqa: E402
from aqua_qe_product_manager.skills.read_confluence_page import read_confluence_page  # noqa: E402
from aqua_qe_product_manager.skills.read_jira_issue import read_jira_issue  # noqa: E402
from aqua_qe_product_manager.skills.read_text_file import read_text_file  # noqa: E402
from aqua_qe_product_manager.skills.update_confluence_page import (  # noqa: E402
    update_confluence_page,
)
from aqua_qe_product_manager.workflow.generate_prd import refine_prd_draft  # noqa: E402
from aqua_qe_product_manager.workflow.generate_product_strategy import (  # noqa: E402
    refine_strategy_draft,
)
from aqua_qe_product_manager.workflow.generate_product_vision import (  # noqa: E402
    refine_vision_draft,
)


def _ler_entrada(args: argparse.Namespace) -> str:
    if args.arquivo:
        return read_text_file(args.arquivo)
    if args.jira:
        return read_jira_issue(args.jira)
    if args.confluence:
        return read_confluence_page(args.confluence)
    # chat (--texto): normaliza a transcrição (remetente por linha), quando houver;
    # texto corrido sem remetentes volta inalterado (ver parse_chat_transcript).
    return format_chat_transcript(parse_chat_transcript(args.texto))


def _perguntar_sim_nao(mensagem: str) -> bool:
    resposta = input(f"{mensagem} (s/n): ").strip().lower()
    return resposta in ("s", "sim", "y", "yes")


# --- Descoberta ---------------------------------------------------------


def _imprimir_descoberta(
    problem_statement: ProblemStatement,
    personas: list[Persona],
    jobs: list[JobToBeDone],
    market_analysis: MarketAnalysis,
) -> None:
    print("\n--- descoberta ---")
    print(f"problema: {problem_statement.problem or '(não identificado)'}")
    print(f"usuários afetados: {problem_statement.affected_users or '(não identificado)'}")
    print(f"personas identificadas: {len(personas)}")
    for persona in personas:
        print(f"  - {persona.name}: {persona.description}")
    print(f"jobs to be done identificados: {len(jobs)}")
    for job in jobs:
        print(f"  - Quando {job.situation}, quero {job.motivation}, para que {job.expected_outcome}")
    print(f"concorrentes citados: {len(market_analysis.competitors)}")
    for concorrente in market_analysis.competitors:
        print(f"  - {concorrente.name}")
    if market_analysis.trends:
        print(f"tendências citadas: {market_analysis.trends}")


def _rodar_descoberta(
    texto: str,
) -> tuple[ProblemStatement, list[Persona], list[JobToBeDone], MarketAnalysis]:
    """Sintetiza a descoberta e a exibe. Sem ciclo de aceite formal (ver docs/agent/acceptance_patterns.md)."""
    resultado = handle_discovery(texto)
    _imprimir_descoberta(*resultado)
    return resultado


# --- Visão de produto -----------------------------------------------------


def _imprimir_visao(vision: ProductVision) -> None:
    print(f"status: {vision.status.value}")
    print(f"statement: {vision.statement}")
    print(f"público-alvo: {vision.target_audience}")
    print(f"diferenciais: {vision.differentiators}")
    print(f"métrica norte: {vision.north_star_metric or '(não definida)'}")
    if vision.review_notes:
        print("observações da revisão:")
        for nota in vision.review_notes:
            print(f"  - {nota}")


def _ciclo_de_refinamento_visao(vision: ProductVision) -> ProductVision:
    while vision.status != ArtifactStatus.DRAFT_VALIDATED and vision.review_notes:
        perguntas = generate_vision_clarifying_questions(vision)
        if not perguntas:
            break

        print("\nO revisor apontou problemas na visão. Responda para ajudar a refinar:")
        respostas = []
        for pergunta in perguntas:
            resposta = input(f"  {pergunta}\n  > ")
            respostas.append({"pergunta": pergunta, "resposta": resposta})

        vision = refine_vision_draft(vision, respostas)
        print("\n--- visão refinada ---")
        _imprimir_visao(vision)

        if vision.status != ArtifactStatus.DRAFT_VALIDATED and not _perguntar_sim_nao(
            "\nTentar refinar de novo?"
        ):
            break
    return vision


def _rodar_visao(
    ideia: str, contexto: dict | None, refinar: bool
) -> ProductVision | None:
    """Gera a visão de produto; retorna a visão aceita, ou None se descartada."""
    vision = handle_vision(ideia, contexto)
    print("\n--- visão de produto ---")
    _imprimir_visao(vision)

    if refinar:
        vision = _ciclo_de_refinamento_visao(vision)

    if not _perguntar_sim_nao("\nAceitar esta visão?"):
        return None

    vision.status = ArtifactStatus.ACCEPTED
    return vision


# --- Estratégia de produto -------------------------------------------------


def _imprimir_estrategia(strategy: ProductStrategy) -> None:
    print(f"status: {strategy.status.value}")
    print(f"metas: {len(strategy.goals)}")
    for meta in strategy.goals:
        print(f"  - {meta.description} (métrica: {meta.metric or '(não definida)'})")
    print(f"temas de roadmap: {strategy.roadmap_themes}")
    print(f"horizonte de tempo: {strategy.time_horizon or '(não definido)'}")
    if strategy.review_notes:
        print("observações da revisão:")
        for nota in strategy.review_notes:
            print(f"  - {nota}")


def _ciclo_de_refinamento_estrategia(strategy: ProductStrategy) -> ProductStrategy:
    while strategy.status != ArtifactStatus.DRAFT_VALIDATED and strategy.review_notes:
        perguntas = generate_strategy_clarifying_questions(strategy)
        if not perguntas:
            break

        print("\nO revisor apontou problemas na estratégia. Responda para ajudar a refinar:")
        respostas = []
        for pergunta in perguntas:
            resposta = input(f"  {pergunta}\n  > ")
            respostas.append({"pergunta": pergunta, "resposta": resposta})

        strategy = refine_strategy_draft(strategy, respostas)
        print("\n--- estratégia refinada ---")
        _imprimir_estrategia(strategy)

        if strategy.status != ArtifactStatus.DRAFT_VALIDATED and not _perguntar_sim_nao(
            "\nTentar refinar de novo?"
        ):
            break
    return strategy


def _rodar_estrategia(
    vision: ProductVision, contexto: dict | None, refinar: bool
) -> ProductStrategy | None:
    """Gera a estratégia de produto a partir da visão aceita; retorna a estratégia aceita, ou None se descartada."""
    strategy = handle_strategy(vision, contexto)
    print("\n--- estratégia de produto ---")
    _imprimir_estrategia(strategy)

    if refinar:
        strategy = _ciclo_de_refinamento_estrategia(strategy)

    if not _perguntar_sim_nao("\nAceitar esta estratégia?"):
        return None

    strategy.status = ArtifactStatus.ACCEPTED
    return strategy


# --- PRD ---------------------------------------------------------------


def _imprimir_prd(draft: PRDDraft) -> None:
    print(f"status: {draft.status.value}")
    print(f"objetivo: {draft.objective}")
    print(f"escopo: {draft.scope}")
    print(f"requisitos funcionais: {len(draft.functional_requirements)}")
    print(f"personas: {len(draft.personas)}")
    print(f"jornadas do usuário: {len(draft.user_journeys)}")
    print(f"objetivos de negócio (KPI): {len(draft.business_objectives)}")
    print(f"casos de uso: {len(draft.use_cases)}")
    print(f"dependências: {draft.dependencies}")
    print(f"premissas técnicas: {len(draft.technical_assumptions)}")
    print(f"restrições: {len(draft.constraints)}")
    print(f"glossário: {len(draft.glossary)}")
    print(f"métricas de produto candidatas (sugeridas, a confirmar): {draft.candidate_product_metrics}")
    print(f"MVP: {draft.mvp_scope}")
    print(f"versão futura: {draft.future_scope}")
    if draft.review_notes:
        print("observações da revisão:")
        for nota in draft.review_notes:
            print(f"  - {nota}")


def _ciclo_de_refinamento_prd(draft: PRDDraft) -> PRDDraft:
    while draft.status != ArtifactStatus.DRAFT_VALIDATED and draft.review_notes:
        perguntas = generate_prd_clarifying_questions(draft)
        if not perguntas:
            break

        print("\nO revisor apontou problemas no PRD. Responda para ajudar a refinar:")
        respostas = []
        for pergunta in perguntas:
            resposta = input(f"  {pergunta}\n  > ")
            respostas.append({"pergunta": pergunta, "resposta": resposta})

        draft = refine_prd_draft(draft, respostas)
        print("\n--- PRD refinado ---")
        _imprimir_prd(draft)

        if draft.status != ArtifactStatus.DRAFT_VALIDATED and not _perguntar_sim_nao(
            "\nTentar refinar de novo?"
        ):
            break
    return draft


def _publicar_ou_atualizar_confluence(
    texto_formatado: str,
    publicar_confluence: bool,
    atualizar_confluence: str | None,
) -> None:
    """Cria uma página nova ou atualiza uma existente no Confluence, sempre sob confirmação humana explícita. Compartilhado entre PRD, visão e estratégia."""
    if atualizar_confluence:
        if not _perguntar_sim_nao(
            f"\nAtualizar a página {atualizar_confluence} no Confluence com esta versão?"
        ):
            return
        update_confluence_page(atualizar_confluence, texto_formatado)
        print(f"página atualizada no Confluence: {atualizar_confluence}")
        return

    if publicar_confluence:
        if not _perguntar_sim_nao("\nPublicar no Confluence?"):
            return
        titulo = input("Título da página no Confluence: ").strip()
        url = create_confluence_page(texto_formatado, titulo)
        print(f"publicado no Confluence: {url}")


def _imprimir_priorizacao(itens: list[PrioritizedRequirement]) -> None:
    for item in itens:
        if item.score is not None:
            print(f"  - [{item.score:.2f}] {item.requirement}")
        else:
            categoria = item.moscow or "(não classificado)"
            print(f"  - [{categoria}] {item.requirement}")
            if item.moscow_justification:
                print(f"      {item.moscow_justification}")


def _corrigir_moscow_manualmente(
    itens: list[PrioritizedRequirement],
) -> list[PrioritizedRequirement]:
    """Correção manual por item — priorização é decisão de negócio do humano, não um fato a pedir de novo ao LLM."""
    print("\nCorreção manual (deixe em branco para manter a categoria atual):")
    for item in itens:
        atual = item.moscow or "(vazio)"
        resposta = (
            input(
                f"  {item.requirement}\n"
                f"  categoria atual: {atual} — nova (must/should/could/wont/vazio) > "
            )
            .strip()
            .lower()
        )
        if resposta in MOSCOW_CATEGORIAS:
            item.moscow = resposta
            item.moscow_justification = "categoria definida manualmente pelo usuário"
    return itens


def _priorizar_moscow(
    texto_fonte: str, requisitos: list[str]
) -> list[PrioritizedRequirement]:
    itens = handle_moscow_classification(requisitos, texto_fonte)
    print("\n--- priorização MoSCoW ---")
    _imprimir_priorizacao(itens)

    if not _perguntar_sim_nao("\nAceitar esta priorização?"):
        itens = _corrigir_moscow_manualmente(itens)
        print("\n--- priorização corrigida ---")
        _imprimir_priorizacao(itens)

    return itens


def _coletar_float(mensagem: str) -> float:
    while True:
        bruto = input(mensagem).strip().replace(",", ".")
        try:
            return float(bruto)
        except ValueError:
            print("  valor inválido, informe um número.")


def _priorizar_numerico(metodo: str, requisitos: list[str]) -> list[PrioritizedRequirement]:
    """RICE/WSJF interativo: todos os números vêm do usuário — o agente nunca estima nenhum (GR-M4)."""
    print(f"\n--- priorização {metodo.upper()} (informe os números para cada requisito) ---")
    itens: list[PrioritizedRequirement] = []
    for requisito in requisitos:
        print(f"\n{requisito}")
        inputs = PriorityInputs()
        if metodo == "rice":
            inputs.reach = _coletar_float("  reach: ")
            inputs.impact = _coletar_float("  impact: ")
            inputs.confidence = _coletar_float("  confidence (0-1): ")
            inputs.effort = _coletar_float("  effort: ")
            score = compute_rice_score(inputs.reach, inputs.impact, inputs.confidence, inputs.effort)
        else:
            inputs.business_value = _coletar_float("  business value: ")
            inputs.time_criticality = _coletar_float("  time criticality: ")
            inputs.risk_reduction = _coletar_float("  risk reduction: ")
            inputs.job_size = _coletar_float("  job size: ")
            score = compute_wsjf_score(
                inputs.business_value,
                inputs.time_criticality,
                inputs.risk_reduction,
                inputs.job_size,
            )
        itens.append(
            PrioritizedRequirement(
                requirement=requisito, metodo_numerico=metodo, score=score, inputs=inputs
            )
        )

    itens.sort(key=lambda item: item.score or 0.0, reverse=True)
    print(f"\n--- resultado {metodo.upper()} (maior para menor) ---")
    _imprimir_priorizacao(itens)
    return itens


def _formatar_priorizacao_markdown(itens: list[PrioritizedRequirement], metodo: str) -> str:
    """Formata a priorização em Markdown — sempre exportada em arquivo separado do PRD (--saida-priorizacao), nunca mesclada nele."""
    if metodo == "moscow":
        linhas = [
            f"- **{item.moscow or '(não classificado)'}** — {item.requirement}"
            + (f"\n  {item.moscow_justification}" if item.moscow_justification else "")
            for item in itens
        ]
    else:
        linhas = [f"- **{item.score:.2f}** — {item.requirement}" for item in itens]
    return f"# Priorização ({metodo.upper()})\n\n" + "\n".join(linhas) + "\n"


def _priorizar_requisitos(
    draft: PRDDraft,
    texto_fonte: str,
    priorizar: str | None,
    saida_priorizacao: str | None,
) -> None:
    if not priorizar:
        return
    if not draft.functional_requirements:
        print("\nSem requisitos funcionais para priorizar.")
        return

    if priorizar == "moscow":
        itens = _priorizar_moscow(texto_fonte, draft.functional_requirements)
    else:
        itens = _priorizar_numerico(priorizar, draft.functional_requirements)

    if saida_priorizacao:
        export_markdown(_formatar_priorizacao_markdown(itens, priorizar), saida_priorizacao)
        print(f"priorização exportada para: {saida_priorizacao}")


def _finalizar_prd_interativo(
    draft: PRDDraft,
    saida: str | None,
    refinar: bool,
    publicar_confluence: bool = False,
    atualizar_confluence: str | None = None,
    priorizar: str | None = None,
    saida_priorizacao: str | None = None,
) -> str | None:
    """Ciclo de refinamento/aceite/exportação/publicação/priorização compartilhado, independente de o PRD ter sido gerado ou carregado de um arquivo existente."""
    _imprimir_prd(draft)

    if refinar:
        draft = _ciclo_de_refinamento_prd(draft)

    if not _perguntar_sim_nao("\nAceitar este PRD?"):
        return None

    draft.status = ArtifactStatus.ACCEPTED
    texto_final = format_prd_markdown(draft)

    if saida:
        export_markdown(texto_final, saida)
        print(f"exportado para: {saida}")

    _publicar_ou_atualizar_confluence(texto_final, publicar_confluence, atualizar_confluence)
    _priorizar_requisitos(draft, texto_final, priorizar, saida_priorizacao)

    return texto_final


def _rodar_prd(
    ideia: str,
    contexto: dict | None,
    saida: str | None,
    refinar: bool,
    publicar_confluence: bool = False,
    atualizar_confluence: str | None = None,
    priorizar: str | None = None,
    saida_priorizacao: str | None = None,
) -> str | None:
    """Gera o PRD; retorna o texto formatado se aceito, ou None."""
    draft = handle_prd(ideia, contexto)
    print("\n--- PRD ---")
    return _finalizar_prd_interativo(
        draft,
        saida,
        refinar,
        publicar_confluence,
        atualizar_confluence,
        priorizar,
        saida_priorizacao,
    )


def _rodar_prd_existente(
    caminho: str,
    saida: str | None,
    refinar: bool,
    publicar_confluence: bool = False,
    atualizar_confluence: str | None = None,
    priorizar: str | None = None,
    saida_priorizacao: str | None = None,
) -> str | None:
    """Carrega um PRD existente e aplica o mesmo ciclo de validação/revisão/refinamento/aceite/publicação/priorização, preservando a redação original nos campos que o refinamento não tocar."""
    draft = handle_existing_prd(caminho)
    print("\n--- PRD carregado de arquivo existente ---")
    return _finalizar_prd_interativo(
        draft,
        saida,
        refinar,
        publicar_confluence,
        atualizar_confluence,
        priorizar,
        saida_priorizacao,
    )


# --- Exportação isolada de visão/estratégia -------------------------------


def _lista_md(itens: list[str]) -> str:
    return "\n".join(f"- {item}" for item in itens) if itens else "(nenhum)"


def _formatar_visao_markdown(vision: ProductVision) -> str:
    """Formata a visão em Markdown, seções conforme knowledge/templates/product_vision.md."""
    return (
        "# Visão de Produto\n\n"
        f"## Statement\n{vision.statement}\n\n"
        f"## Público-alvo\n{vision.target_audience}\n\n"
        f"## Diferenciais\n{_lista_md(vision.differentiators)}\n\n"
        f"## Métrica norte\n{vision.north_star_metric or '(não definida)'}\n"
    )


def _formatar_estrategia_markdown(strategy: ProductStrategy) -> str:
    """Formata a estratégia em Markdown, seções conforme knowledge/templates/product_strategy.md."""
    metas_md = (
        "\n".join(
            f"- {meta.description} — métrica: {meta.metric or '(não definida)'}, "
            f"alvo: {meta.target or '(não definido)'}, prazo: {meta.timeframe or '(não definido)'}"
            for meta in strategy.goals
        )
        or "(nenhuma)"
    )
    return (
        "# Estratégia de Produto\n\n"
        f"## Metas\n{metas_md}\n\n"
        f"## Temas de roadmap\n{_lista_md(strategy.roadmap_themes)}\n\n"
        f"## Horizonte de tempo\n{strategy.time_horizon or '(não definido)'}\n"
    )


# --- Modo completo -------------------------------------------------------


def _rodar_completo(
    texto: str,
    saida: str | None,
    refinar: bool,
    publicar_confluence: bool = False,
    atualizar_confluence: str | None = None,
    priorizar: str | None = None,
    saida_priorizacao: str | None = None,
) -> None:
    """Encadeia descoberta -> visão -> estratégia -> PRD numa execução só, com aceite humano em cada etapa."""
    problem_statement, personas, jobs, market_analysis = _rodar_descoberta(texto)
    contexto_descoberta = {
        "problem_statement": problem_statement,
        "personas": personas,
        "jobs_to_be_done": jobs,
        "market_analysis": market_analysis,
    }

    vision = _rodar_visao(texto, contexto_descoberta, refinar)
    if vision is None:
        print("\nExecução interrompida: visão de produto descartada.")
        return

    contexto_visao = {**contexto_descoberta, "vision": vision}
    strategy = _rodar_estrategia(vision, contexto_visao, refinar)
    if strategy is None:
        print("\nExecução interrompida: estratégia de produto descartada.")
        return

    contexto_prd = {**contexto_visao, "strategy": strategy}
    prd_aceito = _rodar_prd(
        texto,
        contexto_prd,
        saida,
        refinar,
        publicar_confluence,
        atualizar_confluence,
        priorizar,
        saida_priorizacao,
    )
    if prd_aceito is None:
        print("\nExecução interrompida: PRD descartado.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o AQuA-QE Product Manager.")
    parser.add_argument(
        "--modo",
        choices=["descoberta", "visao", "estrategia", "prd", "completo"],
        default="prd",
    )
    entrada = parser.add_mutually_exclusive_group()
    entrada.add_argument("--arquivo", help="Caminho de um arquivo .txt/.md de entrada.")
    entrada.add_argument("--texto", help="Texto de entrada direto (chat).")
    entrada.add_argument("--jira", help="Chave do ticket Jira (ex.: PROJ-123).")
    entrada.add_argument(
        "--confluence", help="URL completa ou ID de uma página do Confluence Cloud."
    )
    entrada.add_argument(
        "--prd-existente",
        dest="prd_existente",
        help=(
            "Caminho de um PRD .md já existente (mesmo formato de "
            "format_prd_markdown) para carregar como PRDDraft estruturado e "
            "refinar, em vez de gerar um PRD novo do zero. Só válido com "
            "--modo prd."
        ),
    )
    parser.add_argument(
        "--saida",
        help="Caminho do .md exportado (modos visao/estrategia/prd/completo, após aceite).",
    )
    parser.add_argument(
        "--refinar",
        action="store_true",
        help=(
            "Ativa o ciclo interativo de perguntas/refinamento para artefatos "
            "não aprovados, antes do aceite humano (que é sempre perguntado, "
            "com ou sem esta flag)."
        ),
    )
    parser.add_argument(
        "--publicar-confluence",
        action="store_true",
        dest="publicar_confluence",
        help=(
            "Modos prd/completo/visao/estrategia: após aceitar o artefato, "
            "pergunta o título e publica como página nova no Confluence "
            "(CONFLUENCE_SPACE_KEY)."
        ),
    )
    parser.add_argument(
        "--atualizar-confluence",
        dest="atualizar_confluence",
        help=(
            "Modos prd/completo/visao/estrategia: após aceitar o artefato, "
            "atualiza a página existente informada (URL completa ou ID) no "
            "Confluence, em vez de criar uma nova. Mutuamente exclusivo com "
            "--publicar-confluence."
        ),
    )
    parser.add_argument(
        "--priorizar",
        choices=["moscow", "rice", "wsjf"],
        help=(
            "Modos prd/completo: após aceitar o PRD, prioriza os requisitos "
            "funcionais. 'moscow' classifica automaticamente a partir de "
            "sinais de linguagem no PRD; 'rice'/'wsjf' pedem os números de "
            "cada requisito interativamente (o agente nunca estima esses "
            "números — GR-M4) e calculam o score em Python puro."
        ),
    )
    parser.add_argument(
        "--saida-priorizacao",
        dest="saida_priorizacao",
        help="Caminho do .md exportado com a priorização, sempre separado do --saida do PRD.",
    )
    args = parser.parse_args()

    if not any([args.arquivo, args.texto, args.jira, args.confluence, args.prd_existente]):
        parser.error(
            "informe exatamente uma entrada: --arquivo, --texto, --jira, "
            "--confluence ou --prd-existente."
        )
    if args.prd_existente and args.modo != "prd":
        parser.error("--prd-existente só é válido com --modo prd.")
    if args.publicar_confluence and args.atualizar_confluence:
        parser.error("--publicar-confluence e --atualizar-confluence são mutuamente exclusivos.")
    _modos_confluence = ("prd", "completo", "visao", "estrategia")
    if args.publicar_confluence and args.modo not in _modos_confluence:
        parser.error(f"--publicar-confluence só é válido com --modo {'/'.join(_modos_confluence)}.")
    if args.atualizar_confluence and args.modo not in _modos_confluence:
        parser.error(f"--atualizar-confluence só é válido com --modo {'/'.join(_modos_confluence)}.")
    _modos_priorizacao = ("prd", "completo")
    if args.priorizar and args.modo not in _modos_priorizacao:
        parser.error(f"--priorizar só é válido com --modo {'/'.join(_modos_priorizacao)}.")

    if args.prd_existente:
        _rodar_prd_existente(
            args.prd_existente,
            args.saida,
            args.refinar,
            args.publicar_confluence,
            args.atualizar_confluence,
            args.priorizar,
            args.saida_priorizacao,
        )
        return

    texto = _ler_entrada(args)

    if args.modo == "descoberta":
        _rodar_descoberta(texto)
    elif args.modo == "visao":
        vision = _rodar_visao(texto, None, args.refinar)
        if vision:
            texto_visao = _formatar_visao_markdown(vision)
            if args.saida:
                export_markdown(texto_visao, args.saida)
                print(f"exportado para: {args.saida}")
            _publicar_ou_atualizar_confluence(
                texto_visao, args.publicar_confluence, args.atualizar_confluence
            )
    elif args.modo == "estrategia":
        vision = _rodar_visao(texto, None, args.refinar)
        if vision is None:
            print("\nExecução interrompida: visão de produto descartada.")
            return
        strategy = _rodar_estrategia(vision, {"vision": vision}, args.refinar)
        if strategy:
            texto_estrategia = _formatar_estrategia_markdown(strategy)
            if args.saida:
                export_markdown(texto_estrategia, args.saida)
                print(f"exportado para: {args.saida}")
            _publicar_ou_atualizar_confluence(
                texto_estrategia, args.publicar_confluence, args.atualizar_confluence
            )
    elif args.modo == "prd":
        _rodar_prd(
            texto,
            None,
            args.saida,
            args.refinar,
            args.publicar_confluence,
            args.atualizar_confluence,
            args.priorizar,
            args.saida_priorizacao,
        )
    else:
        _rodar_completo(
            texto,
            args.saida,
            args.refinar,
            args.publicar_confluence,
            args.atualizar_confluence,
            args.priorizar,
            args.saida_priorizacao,
        )


if __name__ == "__main__":
    main()
