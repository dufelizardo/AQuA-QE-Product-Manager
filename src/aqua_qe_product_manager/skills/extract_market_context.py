from ..models import Competitor, MarketAnalysis
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você estrutura contexto de mercado (concorrentes, tendências) "
    "EXCLUSIVAMENTE a partir do texto de entrada. Nunca liste um concorrente "
    "ou tendência que não esteja citado literalmente no texto, mesmo que "
    "você reconheça o mercado descrito e 'saiba' quem são concorrentes "
    "reais desse mercado — esse conhecimento geral nunca deve ser usado "
    "aqui. Se o texto não citar nenhum concorrente ou tendência, responda "
    "com listas vazias. Inventar um concorrente ou tendência aqui é o "
    "erro mais grave que você pode cometer nesta tarefa."
)


def extract_market_context(texto: str) -> MarketAnalysis:
    """Estrutura o contexto de mercado citado no texto de entrada. Nunca preenche com concorrentes/tendências do conhecimento geral do modelo (GR-M1)."""
    prompt = (
        f"Texto:\n{texto}\n\n"
        "Identifique apenas os concorrentes e tendências de mercado citados "
        "literalmente no texto.\n"
        'Responda apenas em JSON: {"concorrentes": [{"nome": "...", '
        '"pontos_fortes": ["..."], "pontos_fracos": ["..."], "trecho_fonte": "..."}], '
        '"tendencias": ["..."], "contexto_mercado": "..."}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    competidores = [
        Competitor(
            name=item.get("nome") or "",
            strengths=item.get("pontos_fortes") or [],
            weaknesses=item.get("pontos_fracos") or [],
            source_reference=item.get("trecho_fonte") or "",
        )
        for item in dados.get("concorrentes", [])
    ]
    return MarketAnalysis(
        competitors=competidores,
        trends=dados.get("tendencias") or [],
        market_context=dados.get("contexto_mercado") or "",
    )
