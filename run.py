"""CLI simples para rodar o AQuA-QE Product Manager sem precisar mexer em sys.path manualmente."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

_RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(_RAIZ / "src"))
load_dotenv(_RAIZ / ".env")

from aqua_qe_product_manager.models import (  # noqa: E402
    ArtifactStatus,
    JobToBeDone,
    MarketAnalysis,
    PRDDraft,
    Persona,
    ProblemStatement,
    ProductStrategy,
    ProductVision,
)
from aqua_qe_product_manager.orchestrator.product_manager import (  # noqa: E402
    handle_discovery,
    handle_prd,
    handle_strategy,
    handle_vision,
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


def _rodar_prd(
    ideia: str, contexto: dict | None, saida: str | None, refinar: bool
) -> str | None:
    """Gera o PRD; retorna o texto formatado se aceito, ou None."""
    draft = handle_prd(ideia, contexto)
    print("\n--- PRD ---")
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

    return texto_final


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


def _rodar_completo(texto: str, saida: str | None, refinar: bool) -> None:
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
    prd_aceito = _rodar_prd(texto, contexto_prd, saida, refinar)
    if prd_aceito is None:
        print("\nExecução interrompida: PRD descartado.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o AQuA-QE Product Manager.")
    parser.add_argument(
        "--modo",
        choices=["descoberta", "visao", "estrategia", "prd", "completo"],
        default="prd",
    )
    entrada = parser.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--arquivo", help="Caminho de um arquivo .txt/.md de entrada.")
    entrada.add_argument("--texto", help="Texto de entrada direto (chat).")
    entrada.add_argument("--jira", help="Chave do ticket Jira (ex.: PROJ-123).")
    entrada.add_argument(
        "--confluence", help="URL completa ou ID de uma página do Confluence Cloud."
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
    args = parser.parse_args()

    texto = _ler_entrada(args)

    if args.modo == "descoberta":
        _rodar_descoberta(texto)
    elif args.modo == "visao":
        vision = _rodar_visao(texto, None, args.refinar)
        if vision and args.saida:
            export_markdown(_formatar_visao_markdown(vision), args.saida)
            print(f"exportado para: {args.saida}")
    elif args.modo == "estrategia":
        vision = _rodar_visao(texto, None, args.refinar)
        if vision is None:
            print("\nExecução interrompida: visão de produto descartada.")
            return
        strategy = _rodar_estrategia(vision, {"vision": vision}, args.refinar)
        if strategy and args.saida:
            export_markdown(_formatar_estrategia_markdown(strategy), args.saida)
            print(f"exportado para: {args.saida}")
    elif args.modo == "prd":
        _rodar_prd(texto, None, args.saida, args.refinar)
    else:
        _rodar_completo(texto, args.saida, args.refinar)


if __name__ == "__main__":
    main()
