from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# SQLAlchemyインスタンスを作成
db = SQLAlchemy()

# モデル定義は models/__init__.py と models/income_model.py に移動 