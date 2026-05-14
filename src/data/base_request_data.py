import json

from .models import ReviewResponseModel
from .prompts import check_grammar
from ..llm.deepseek import MODEL


def get_base_request_data(text) -> dict:
    return {
        "contents": [{"parts": [{"text": json.dumps(text)}], "role": "user"}],
        "systemInstruction": {
            "parts": [{"text": check_grammar}],
            "role": "user",
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            **ReviewResponseModel.schema(),
        },
    }


def get_deepseek_request_data(text) -> dict:
    schema = json.dumps(ReviewResponseModel.schema(), ensure_ascii=False)
    system_content = f"{check_grammar}\n\nYou must return a JSON object strictly matching this schema:\n{schema}"
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": json.dumps(text)},
        ],
        "response_format": {"type": "json_object"},
    }
