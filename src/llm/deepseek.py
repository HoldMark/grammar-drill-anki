from json import JSONDecodeError

import requests
from requests import Response

from ..utils.logs.api import logging as log
from ..config.read_env import DEEPSEEK_API_KEY
from ..utils.logs.logger import get_logger

logger = get_logger(__name__)

MODEL = "deepseek-v4-flash"
URL = "https://api.deepseek.com/chat/completions"


class DeepSeekClient:
    ERROR = "Got an error"

    @log("Request (DeepSeek)")
    def _request(self, data: dict) -> Response:
        return requests.post(url=URL, headers=self._headers, json=data)

    def generate_content(self, data: dict):
        result = self._request(data)

        if result.status_code != 200:
            logger.error(f"DeepSeek request failed with status {result.status_code}: {result.text}")
            return self.ERROR

        try:
            return result.json()
        except JSONDecodeError:
            return self.ERROR

    @property
    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        }


deepseek_client = DeepSeekClient()
