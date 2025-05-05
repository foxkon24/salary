import os
from dotenv import load_dotenv

# .envファイルがあれば読み込む（強制的に再読み込み）
load_dotenv(override=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    
    # SQLAlchemy設定
    # 環境変数DATABASE_URLを優先的に使用し、なければ個別の環境変数から構築
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"mysql://{os.environ.get('MYSQL_USER', 'user')}:{os.environ.get('MYSQL_PASSWORD', '09073965920')}"
        f"@{os.environ.get('MYSQL_HOST', 'localhost')}/{os.environ.get('MYSQL_DB', 'salary')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 会計年度の設定（5月開始、翌年4月終了）
    FISCAL_YEAR_START_MONTH = int(os.environ.get('FISCAL_YEAR_START_MONTH', 5))
    FISCAL_YEAR_END_MONTH = int(os.environ.get('FISCAL_YEAR_END_MONTH', 4)) 