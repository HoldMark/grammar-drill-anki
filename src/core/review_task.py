import json

from ..llm.deepseek import deepseek_client, DeepSeekClient
from ..data.models import ReviewResponseModel
from ..db.db_writer import store
from ..data.parse_data import DataToReview
from ..utils.logs.func import log
from ..data.base_request_data import get_deepseek_request_data


@log
def review_task(data: dict) -> dict:
    data_to_review = DataToReview(**data)
    data = get_deepseek_request_data(data_to_review.dict_view())
    content = deepseek_client.generate_content(data)

    result = {"result": "Error"}

    if content != DeepSeekClient.ERROR:
        raw_text = content["choices"][0]["message"]["content"]
        result = json.loads(raw_text)
        store(data_to_review, ReviewResponseModel(**result))

    return result
