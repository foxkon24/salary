import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（強制的に再読み込み）
load_dotenv(override=True)

from app import create_app
from datetime import datetime
from app.models.database import db

# 環境変数からポート番号を取得
port = int(os.environ.get('PORT', 8090))

app = create_app()

# コンテキストプロセッサの追加
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# アプリケーションコンテキスト内でDBを初期化
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print(f"============================================")
    print(f"アプリケーションを開始しています...")
    print(f"ポート番号: {port}")
    print(f"Nginx経由でアクセス: http://localhost:8080/system/salary")
    print(f"直接アクセス: http://localhost:{port}/")
    print(f"直接アクセス(app_url): http://localhost:{port}/system/salary")
    print(f"============================================")
    print(f"注意: このアプリケーションはNginxリバースプロキシで'/system/salary'として提供されるよう設定されています")
    print(f"     APIエンドポイントは '/system/salary/api/~' として提供されます")
    app.run(
        debug=os.environ.get('DEBUG', 'True').lower() == 'true', 
        host='0.0.0.0', 
        port=port
    )