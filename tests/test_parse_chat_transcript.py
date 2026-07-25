from aqua_qe_product_manager.models import ChatMessage
from aqua_qe_product_manager.skills.parse_chat_transcript import parse_chat_transcript


def test_parses_multiple_speakers():
    texto = "PM: precisamos entender o problema\nStakeholder: qual o publico-alvo?\nPM: pessoa fisica"

    resultado = parse_chat_transcript(texto)

    assert resultado == [
        ChatMessage(speaker="PM", text="precisamos entender o problema"),
        ChatMessage(speaker="Stakeholder", text="qual o publico-alvo?"),
        ChatMessage(speaker="PM", text="pessoa fisica"),
    ]


def test_speaker_with_multiple_words():
    texto = "Maria Silva: precisamos revisar a visao"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="Maria Silva", text="precisamos revisar a visao")]


def test_continuation_line_attaches_to_previous_speaker():
    texto = "PM: precisamos entender o problema\ne tambem o mercado"

    resultado = parse_chat_transcript(texto)

    assert len(resultado) == 1
    assert resultado[0].speaker == "PM"
    assert resultado[0].text == "precisamos entender o problema\ne tambem o mercado"


def test_plain_text_without_speakers_falls_back_to_single_message():
    texto = "Clientes precisam de um app para investir em CDB"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="", text=texto)]


def test_colon_mid_sentence_is_not_mistaken_for_a_speaker():
    texto = "O sistema deve responder em: 2 segundos"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="", text=texto)]


def test_empty_lines_are_ignored():
    texto = "PM: primeira mensagem\n\n\nStakeholder: segunda mensagem"

    resultado = parse_chat_transcript(texto)

    assert resultado == [
        ChatMessage(speaker="PM", text="primeira mensagem"),
        ChatMessage(speaker="Stakeholder", text="segunda mensagem"),
    ]
