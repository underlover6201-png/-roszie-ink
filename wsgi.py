"""生產環境 WSGI 進入點（Gunicorn 使用）"""
import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402

app = create_app(os.environ.get("FLASK_ENV", "production"))
