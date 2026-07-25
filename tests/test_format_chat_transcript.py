from aqua_qe_product_manager.models import ChatMessage
from aqua_qe_product_manager.skills.format_chat_transcript import format_chat_transcript


def test_formats_multiple_messages_with_speaker_prefix():
    mensagens = [
        ChatMessage(speaker="PM", text="precisamos entender o problema"),
        ChatMessage(speaker="Stakeholder", text="qual o publico-alvo?"),
    ]

    resultado = format_chat_transcript(mensagens)

    assert resultado == "PM: precisamos entender o problema\n\nStakeholder: qual o publico-alvo?"


def test_single_unattributed_message_returns_original_text_unchanged():
    texto_original = "Clientes precisam de um app para investir em CDB"

    resultado = format_chat_transcript([ChatMessage(speaker="", text=texto_original)])

    assert resultado == texto_original


def test_empty_list_returns_empty_string():
    assert format_chat_transcript([]) == ""


def test_roundtrip_parse_then_format_preserves_plain_text():
    from aqua_qe_product_manager.skills.parse_chat_transcript import parse_chat_transcript

    texto_original = "O sistema deve responder em: 2 segundos"

    resultado = format_chat_transcript(parse_chat_transcript(texto_original))

    assert resultado == texto_original
