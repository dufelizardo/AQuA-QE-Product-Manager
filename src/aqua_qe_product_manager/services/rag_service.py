from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from .embedding_service import embed

_COLLECTION_REFINEMENT_MEMORY = "refinement_answer_memory"
_VECTOR_SIZE = 1024  # dimensão do bge-m3
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_STORAGE_PATH = _PROJECT_ROOT / ".data" / "qdrant"


def _client() -> QdrantClient:
    _STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(_STORAGE_PATH))


def record_refinement_answer(
    pergunta: str, resposta: str, tipo_artefato: str, client: QdrantClient | None = None
) -> None:
    """Grava um par pergunta/resposta de um ciclo de refinamento real (visão, estratégia ou
    PRD), para reaproveitamento futuro como sugestão editável em ciclos de refinamento
    posteriores — nunca aplicada automaticamente."""
    client = client or _client()
    if not client.collection_exists(_COLLECTION_REFINEMENT_MEMORY):
        client.create_collection(
            collection_name=_COLLECTION_REFINEMENT_MEMORY,
            vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
        )
    vetor = embed([pergunta])[0]
    ponto = PointStruct(
        id=str(uuid4()),
        vector=vetor,
        payload={"pergunta": pergunta, "resposta": resposta, "tipo_artefato": tipo_artefato},
    )
    client.upsert(collection_name=_COLLECTION_REFINEMENT_MEMORY, points=[ponto])


def find_similar_refinement_answers(
    pergunta: str, k: int = 1, client: QdrantClient | None = None
) -> list[dict]:
    """Busca as k respostas de refinamento mais parecidas com a pergunta atual (memória
    institucional). Retorna lista vazia se a collection ainda não existir (nenhuma resposta
    registrada até agora) — nunca cria a collection nem indexa nada a partir daqui."""
    client = client or _client()
    if not client.collection_exists(_COLLECTION_REFINEMENT_MEMORY):
        return []
    vetor = embed([pergunta])[0]
    resultados = client.query_points(
        collection_name=_COLLECTION_REFINEMENT_MEMORY, query=vetor, limit=k
    ).points
    return [
        {
            "pergunta": ponto.payload["pergunta"],
            "resposta": ponto.payload["resposta"],
            "tipo_artefato": ponto.payload["tipo_artefato"],
            "score": ponto.score,
        }
        for ponto in resultados
    ]
