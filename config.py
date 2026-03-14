"""통신선로 설계 프로그램 설정"""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# .env 파일 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))
DB_PATH = os.path.join(BASE_DIR, "telecom_design.db")

# 간접비 비율
INDIRECT_LABOR_RATE = 0.12      # 간접노무비: 노무비 × 12%
SAFETY_MGMT_RATE = 0.03         # 안전관리비: (노무비+재료비) × 3%
GENERAL_MGMT_RATE = 0.06        # 일반관리비: (노무비+경비) × 6%
PROFIT_RATE = 0.05              # 이윤: (노무비+일반관리비) × 5%
VAT_RATE = 0.10                 # 부가세: 소계 × 10%

# 캔버스 설정
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800
GRID_SIZE = 20

# 요소 상태별 색상
STATUS_COLORS = {
    "existing": "#8B4513",   # 기존: 갈색
    "damaged": "#FF0000",    # 파손: 빨강
    "new": "#0000FF",        # 신설: 파랑
    "demolish": "#808080",   # 철거: 회색
}

# 요소 타입
ELEMENT_TYPES = ["pole", "cable", "terminal", "house", "dropwire"]

# AI 설정
AI_MODEL = "claude-sonnet-4-20250514"
AI_MAX_TOKENS = 4096
AI_TEMPERATURE = 0.1
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
