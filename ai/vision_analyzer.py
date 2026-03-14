"""Claude Vision API를 사용한 도면 이미지 분석"""
import base64
import json
import re
import os
import anthropic
from config import AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE, ANTHROPIC_API_KEY
from ai.prompt_templates import DRAWING_ANALYSIS_PROMPT, CORRECTION_PROMPT_TEMPLATE


class VisionAnalyzer:
    """도면 이미지를 Claude Vision API로 분석"""

    SUPPORTED_TYPES = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    def __init__(self, api_key=None):
        self.api_key = api_key or ANTHROPIC_API_KEY
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def set_api_key(self, api_key):
        self.api_key = api_key
        self._client = None

    def test_connection(self):
        """API 키 유효성 테스트. 성공하면 True, 실패하면 에러 메시지 반환."""
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            client.messages.create(
                model=AI_MODEL,
                max_tokens=50,
                messages=[{"role": "user", "content": "Hello"}],
            )
            return True
        except Exception as e:
            return str(e)

    def _encode_image(self, image_path):
        """이미지 파일을 base64로 인코딩"""
        ext = os.path.splitext(image_path)[1].lower()
        media_type = self.SUPPORTED_TYPES.get(ext)
        if not media_type:
            raise ValueError(f"지원하지 않는 이미지 형식: {ext}")

        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return media_type, data

    def _extract_json(self, text):
        """응답 텍스트에서 JSON 추출 (마크다운 코드블록 처리)"""
        # ```json ... ``` 블록 추출
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            text = match.group(1)
        # 그래도 JSON이 아닌 경우 중괄호 기준으로 추출
        text = text.strip()
        if not text.startswith("{"):
            start = text.find("{")
            if start >= 0:
                text = text[start:]
        return json.loads(text)

    def analyze_image(self, image_path):
        """도면 이미지 분석. 결과를 dict로 반환."""
        media_type, image_data = self._encode_image(image_path)

        response = self.client.messages.create(
            model=AI_MODEL,
            max_tokens=AI_MAX_TOKENS,
            temperature=AI_TEMPERATURE,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": DRAWING_ANALYSIS_PROMPT,
                        },
                    ],
                }
            ],
        )

        raw_text = response.content[0].text
        return self._extract_json(raw_text), raw_text

    def analyze_with_corrections(self, image_path, original_response, corrections):
        """사용자 수정 사항을 반영하여 재분석"""
        media_type, image_data = self._encode_image(image_path)

        correction_prompt = CORRECTION_PROMPT_TEMPLATE.format(
            original_response=json.dumps(original_response, ensure_ascii=False, indent=2),
            corrections=corrections,
        )

        response = self.client.messages.create(
            model=AI_MODEL,
            max_tokens=AI_MAX_TOKENS,
            temperature=AI_TEMPERATURE,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": correction_prompt,
                        },
                    ],
                }
            ],
        )

        raw_text = response.content[0].text
        return self._extract_json(raw_text), raw_text
