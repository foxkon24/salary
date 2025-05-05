from flask import Flask, request, redirect
from app.config import Config
from app.models.database import db
import os

def create_app(config_class=Config):
    """アプリケーションファクトリー"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # SecretKeyの設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    
    # リバースプロキシのサブパス設定
    app.config['APPLICATION_ROOT'] = '/system/salary'
    
    # リクエスト前処理フック（SCRIPT_NAMEを設定）
    @app.before_request
    def fix_script_name():
        """Nginxプロキシ経由のリクエストを処理するためのSCRIPT_NAME設定"""
        script_name = '/system/salary'
        
        # リクエストURLをロギング
        print(f"処理前 - Request URL: {request.url}")
        print(f"処理前 - SCRIPT_NAME: {request.environ.get('SCRIPT_NAME')}")
        print(f"処理前 - PATH_INFO: {request.environ.get('PATH_INFO')}")
        
        # 既にスクリプト名が設定されていなければ設定する
        if request.environ.get('SCRIPT_NAME') == '':
            request.environ['SCRIPT_NAME'] = script_name
            
            # ルートパスまたはスクリプト名で始まる場合の処理
            if request.environ['PATH_INFO'] == script_name:
                request.environ['PATH_INFO'] = '/'
            elif request.environ['PATH_INFO'].startswith(script_name + '/'):
                request.environ['PATH_INFO'] = request.environ['PATH_INFO'][len(script_name):]
                
        # 処理後のリクエスト情報を表示
        print(f"処理後 - Request URL: {request.url}")
        print(f"処理後 - SCRIPT_NAME: {request.environ.get('SCRIPT_NAME')}")
        print(f"処理後 - PATH_INFO: {request.environ.get('PATH_INFO')}")
    
    # SQLAlchemyの初期化
    db.init_app(app)
    
    # テンプレート関数を追加
    @app.context_processor
    def inject_app_url():
        """アプリケーションURLをテンプレートに提供"""
        def get_host_url():
            # 現在のリクエストホストに基づいてURLを構築
            current_host = request.host
            scheme = request.scheme
            
            # 現在のリクエストURLの情報をログに出力
            print(f"Current host: {current_host}")
            print(f"Current URL scheme: {scheme}")
            
            # 関数ではなく文字列を返す
            return f"{scheme}://{current_host}{request.script_root}"
        
        # 関数ではなく文字列を返す
        return {'app_url': get_host_url()}
    
    # ルート登録
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # 直接/system/salaryにアクセスした場合のリダイレクト
    @app.route('/system/salary')
    @app.route('/system/salary/')
    def system_salary_redirect():
        print("直接/system/salaryにアクセスされました")
        return redirect('/')
    
    # Jinja2フィルターの追加
    @app.template_filter('format_currency')
    def format_currency(value):
        """数値を通貨形式でフォーマット"""
        try:
            return f"¥{int(value):,}"
        except (TypeError, ValueError):
            return "¥0"
    
    @app.context_processor
    def utility_processor():
        """テンプレートで使用するユーティリティ関数"""
        def get_month_name(month):
            """月の数値から月名を取得"""
            return f"{month}月"
        
        def get_fiscal_year_label(year):
            """会計年度のラベルを生成"""
            return f"{year}年度（{year}年5月〜{year+1}年4月）"
        
        def format_currency(value):
            """通貨フォーマット（例: ¥123,456）"""
            try:
                return f"¥{int(value):,}"
            except (TypeError, ValueError):
                return "¥0"
        
        # デバッグ用に呼び出しを確認
        print(f"ユーティリティ関数の登録: get_month_name, get_fiscal_year_label, format_currency")
        print(f"サンプル出力: {get_month_name(5)}, {get_fiscal_year_label(2026)}, {format_currency(10000)}")
        
        return dict(
            get_month_name=get_month_name,
            get_fiscal_year_label=get_fiscal_year_label,
            format_currency=format_currency
        )
    
    # データベース作成コマンド
    @app.cli.command('init-db')
    def init_db_command():
        """データベースのテーブルを初期化するコマンド"""
        db.create_all()
        print('データベースを初期化しました')
    
    return app 