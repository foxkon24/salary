from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app.models.income_model import IncomeModel
from app.models import Income
from app.config import Config
import json

main_bp = Blueprint('main', __name__)
income_model = IncomeModel()

@main_bp.route('/')
def index():
    """ダッシュボード（トップページ）"""
    # 全年度情報を取得
    years = income_model.get_years()
    print(f"年度一覧: {years}")
    
    # 年度別サマリーの取得
    yearly_summary = income_model.get_income_summary_by_year()
    print(f"年度別サマリー: {yearly_summary}")
    
    # GETパラメータから年度IDを取得（指定されていない場合は最新年度を表示）
    year_id = request.args.get('year_id', type=int)
    if not year_id and years:
        year_id = years[-1]['year_id']  # デフォルトで最新年度を選択
    elif not year_id:
        year_id = 2022  # 年度がない場合のデフォルト値
    
    print(f"選択された年度ID: {year_id}")
    
    # 選択された年度の給与情報を取得
    year_data = income_model.get_income_by_fiscal_year(year_id)
    print(f"年度データ: 取得件数 {len(year_data)}")
    
    return render_template(
        'index.html', 
        years=years, 
        selected_year=year_id,
        year_data=year_data,
        yearly_summary=yearly_summary
    )

@main_bp.route('/add-year', methods=['POST'])
def add_year():
    """新しい年度をデータベースに追加"""
    year_id = request.form.get('year_id', type=int)
    if not year_id:
        flash('有効な年度を入力してください', 'danger')
        return redirect(url_for('main.index'))
    
    # 年度の範囲チェック
    if year_id < 2000 or year_id > 2100:
        flash('年度は2000～2100の範囲で入力してください', 'danger')
        return redirect(url_for('main.index'))
    
    # 年度を追加
    success, message = income_model.add_year(year_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    # 追加した年度を選択してトップページにリダイレクト
    return redirect(url_for('main.index', year_id=year_id) if success else url_for('main.index'))

@main_bp.route('/delete-year/<int:year_id>', methods=['POST'])
def delete_year(year_id):
    """年度とその関連データを削除する"""
    print(f"削除リクエスト受信: 年度ID {year_id}")
    
    if year_id < 2000 or year_id > 2100:
        flash('無効な年度IDです', 'danger')
        return redirect(url_for('main.index'))
    
    # 年度を削除
    success, message = income_model.delete_year(year_id)
    
    print(f"削除処理結果: 成功={success}, メッセージ={message}")
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    # リダイレクト先を修正（給与データ管理ページに戻る）
    return redirect(url_for('main.salary_management'))

# 年度選択はGETパラメータで処理するため、このルートは不要
# @main_bp.route('/year/<int:year_id>')
# def view_year(year_id):
#     """特定年度の給与情報表示"""
#     # 全年度情報を取得
#     years = income_model.get_years()
#     
#     # 選択された年度の給与情報を取得
#     year_data = income_model.get_income_by_fiscal_year(year_id)
#     
#     # 年度別サマリーの取得
#     yearly_summary = income_model.get_income_summary_by_year()
#     
#     return render_template(
#         'index.html', 
#         years=years, 
#         selected_year=year_id,
#         year_data=year_data,
#         yearly_summary=yearly_summary
#     )

@main_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_income(id):
    """給与情報編集画面"""
    if request.method == 'POST':
        # フォームからデータを取得
        monthly_total = int(float(request.form.get('monthly_total', 0)))
        monthly_deduction = int(float(request.form.get('monthly_deduction', 0)))
        year_end_adjustment = int(float(request.form.get('year_end_adjustment', 0)))
        bonus_total = int(float(request.form.get('bonus_total', 0)))
        bonus_deduction = int(float(request.form.get('bonus_deduction', 0)))
        
        # 給与データを更新
        income_model.update_income(
            id, monthly_total, monthly_deduction, year_end_adjustment, 
            bonus_total, bonus_deduction
        )
        
        # 現在のレコードの年度情報を取得
        income = Income.query.get(id)
        year_id = income.year_id if income else 2022
        
        # url_forを使用してリダイレクト（給与データ管理ページに戻る）
        return redirect(url_for('main.salary_management', year_id=year_id))
    
    # 指定されたIDの給与情報を取得
    income = Income.query.get(id)
    
    if not income:
        return redirect(url_for('main.index'))
    
    return render_template('edit.html', income=income)

# APIエンドポイント - Nginxプロキシ経由でも正しく動作するよう設定
@main_bp.route('/api/years')
def api_years():
    """年度情報のJSONデータ提供"""
    years = income_model.get_years()
    return jsonify(years)

@main_bp.route('/api/year/<int:year_id>')
def api_year_data(year_id):
    """特定年度の給与情報のJSONデータ提供"""
    year_data = income_model.get_income_by_fiscal_year(year_id)
    
    # 月ごとのデータを整形（Chart.js用）
    months = []
    monthly_totals = []
    bonus_totals = []
    cumulative_totals = []
    
    print(f"APIから返す年度データ (ID: {year_id}): {len(year_data)}件")
    
    for record in year_data:
        month_name = f"{record['month']}月"
        months.append(month_name)
        # Decimal型をfloatに変換
        monthly_totals.append(float(record['monthly_total']))
        bonus_totals.append(float(record['bonus_total']))
        cumulative_totals.append(float(record['cumulative_total']))
    
    # 生データをシリアライズ可能な形式に変換
    serializable_data = []
    for record in year_data:
        record_dict = {}
        for key, value in record.items():
            # Decimalオブジェクトをfloatに変換
            if hasattr(value, 'as_tuple') and hasattr(value, 'quantize'):  # Decimalの簡易判定
                record_dict[key] = float(value)
            else:
                record_dict[key] = value
        serializable_data.append(record_dict)
    
    # 月次合計と賞与合計を計算して表示
    monthly_sum = sum(monthly_totals)
    bonus_sum = sum(bonus_totals)
    total_sum = monthly_sum + bonus_sum
    
    print(f"月次合計: {monthly_sum}, 賞与合計: {bonus_sum}, 総合計: {total_sum}")
    
    response_data = {
        'labels': months,
        'monthly_totals': monthly_totals,
        'bonus_totals': bonus_totals,
        'cumulative_totals': cumulative_totals,
        'raw_data': serializable_data
    }
    
    print(f"月次データ応答: {len(months)}ヶ月分のデータ")
    
    return jsonify(response_data)

@main_bp.route('/api/yearly_summary')
def api_yearly_summary():
    """年度別サマリーのJSONデータ提供"""
    yearly_summary = income_model.get_income_summary_by_year()
    
    # Chart.js用にデータを整形
    years = []
    total_monthly = []
    total_bonus = []
    grand_total = []
    
    print(f"APIから返す年度サマリー: {len(yearly_summary)}件")
    
    for record in yearly_summary:
        fiscal_year = record['fiscal_year']
        years.append(f"{fiscal_year}年度")
        # Decimal型をfloatに変換
        total_monthly.append(float(record['total_monthly']))
        total_bonus.append(float(record['total_bonus']))
        grand_total.append(float(record['grand_total']))
    
    # 生データをシリアライズ可能な形式に変換
    serializable_summary = []
    for record in yearly_summary:
        record_dict = {}
        for key, value in record.items():
            # Decimalオブジェクトをfloatに変換
            if hasattr(value, 'as_tuple') and hasattr(value, 'quantize'):  # Decimalの簡易判定
                record_dict[key] = float(value)
            else:
                record_dict[key] = value
        serializable_summary.append(record_dict)
    
    response_data = {
        'labels': years,
        'total_monthly': total_monthly,
        'total_bonus': total_bonus,
        'grand_total': grand_total,
        'raw_data': serializable_summary
    }
    
    print(f"年度別サマリー応答データ: {response_data}")
    
    return jsonify(response_data)

@main_bp.route('/debug')
def debug_info():
    """URLデバッグ情報を表示する一時的なエンドポイント"""
    # 現在のホストに基づいてアプリURLを構築
    current_host = request.host
    scheme = request.scheme
    app_url = f"{scheme}://{current_host}/system/salary"
    
    debug_info = {
        'url': request.url,
        'base_url': request.base_url,
        'host': request.host,
        'script_root': request.script_root,
        'path': request.path,
        'full_path': request.full_path,
        'script_name': request.environ.get('SCRIPT_NAME', ''),
        'path_info': request.environ.get('PATH_INFO', ''),
        'query_string': request.query_string.decode() if request.query_string else '',
        'headers': dict(request.headers),
        'app_url': app_url,
    }
    
    # コンソールにも表示
    for key, value in debug_info.items():
        if key != 'headers':  # ヘッダーは長いので除外
            print(f"DEBUG: {key} = {value}")
    
    return jsonify(debug_info)

@main_bp.route('/salary-management')
def salary_management():
    """給与データ管理ページ"""
    # 全年度情報を取得
    years = income_model.get_years()
    
    # GETパラメータから年度IDを取得（指定されていない場合は最新年度を表示）
    year_id = request.args.get('year_id', type=int)
    if not year_id and years:
        year_id = years[-1]['year_id']  # デフォルトで最新年度を選択
    elif not year_id:
        year_id = 2022  # 年度がない場合のデフォルト値
    
    # 選択された年度の給与情報を取得
    year_data = income_model.get_income_by_fiscal_year(year_id)
    
    return render_template(
        'salary_management.html', 
        years=years, 
        selected_year=year_id,
        year_data=year_data
    ) 