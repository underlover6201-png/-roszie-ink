"""Flask 應用程式設定 - 分三環境"""
import os


class Config:
    """共用基底設定"""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-change-in-prod")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = int(os.environ.get("WTF_CSRF_TIME_LIMIT", 3600))

    # 郵件
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

    # 上傳
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "app/uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 20 * 1024 * 1024))
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

    # 儲存後端
    STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
    S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
    S3_REGION = os.environ.get("S3_REGION", "auto")
    S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")

    # 安全性
    MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", 5))
    LOGIN_LOCKOUT_MINUTES = int(os.environ.get("LOGIN_LOCKOUT_MINUTES", 30))

    # SEO
    SITE_URL = os.environ.get("SITE_URL", "http://localhost:5000")
    GA_TRACKING_ID = os.environ.get("GA_TRACKING_ID")

    # 綠界 ECPay 金流
    ECPAY_MERCHANT_ID = os.environ.get("ECPAY_MERCHANT_ID", "2000132")
    ECPAY_HASH_KEY = os.environ.get("ECPAY_HASH_KEY", "5294y06JbISpM5x9")
    ECPAY_HASH_IV = os.environ.get("ECPAY_HASH_IV", "v77hoKGq4kWxNNIS")
    ECPAY_API_URL = os.environ.get(
        "ECPAY_API_URL",
        "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
    )
    ECPAY_TEST_MODE = os.environ.get("ECPAY_TEST_MODE", "true").lower() == "true"

    # 天氣
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
    STUDIO_CITY = os.environ.get("STUDIO_CITY", "Taipei")
    STUDIO_LAT = float(os.environ.get("STUDIO_LAT", 25.0330))
    STUDIO_LON = float(os.environ.get("STUDIO_LON", 121.5654))

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_STORAGE_URL = REDIS_URL

    # 快取
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    RATELIMIT_ENABLED = False
    CACHE_TYPE = "SimpleCache"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    CACHE_TYPE = "SimpleCache"

    TALISMAN_CONTENT_SECURITY_POLICY = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "https://www.googletagmanager.com",
            "https://www.google-analytics.com",
            "'unsafe-inline'",
        ],
        "style-src": [
            "'self'",
            "https://fonts.googleapis.com",
            "'unsafe-inline'",
        ],
        "font-src": ["'self'", "https://fonts.gstatic.com"],
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'", "https://api.openweathermap.org"],
    }


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    CACHE_TYPE = "SimpleCache"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
