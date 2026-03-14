"""통신선로 설계 및 예산 산출 프로그램 - 진입점"""
import sys
import os

# 프로젝트 루트를 모듈 검색 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import init_db
from gui.app import MainApp


def main():
    # DB 초기화
    init_db()

    # GUI 실행
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
