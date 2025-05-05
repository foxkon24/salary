from sqlalchemy import case, func, and_, or_
from app.models.database import db
from app.models import Year, Income
from app.config import Config

class IncomeModel:
    def get_years(self):
        """全年度情報を取得"""
        years = Year.query.order_by(Year.year_id).all()
        return [year.to_dict() for year in years]
    
    def add_year(self, year_id):
        """新しい年度を追加する"""
        # すでに存在する年度かチェック
        existing_year = Year.query.get(year_id)
        if existing_year:
            return False, "この年度は既に登録されています"
        
        try:
            # 年度テーブルに追加
            new_year = Year(year_id=year_id, display_name=f"{year_id}年度")
            db.session.add(new_year)
            db.session.commit()
            
            # 会計年度の各月のレコードを初期化
            self.initialize_year_records(year_id)
            
            return True, f"{year_id}年度を追加しました"
        except Exception as e:
            db.session.rollback()
            return False, f"エラーが発生しました: {str(e)}"
    
    def delete_year(self, year_id):
        """年度とその関連データを削除する"""
        try:
            print(f"年度削除開始: 年度ID {year_id}")
            
            # 該当する年度の月次データを削除
            start_month = Config.FISCAL_YEAR_START_MONTH
            end_month = Config.FISCAL_YEAR_END_MONTH
            
            # 当年5月〜12月のデータを削除
            result1 = Income.query.filter(
                Income.year_id == year_id,
                Income.month >= start_month
            ).delete(synchronize_session='fetch')
            print(f"当年データ削除: {result1}件")
            
            # 翌年1月〜4月のデータを削除
            result2 = Income.query.filter(
                Income.year_id == year_id,
                Income.month <= end_month
            ).delete(synchronize_session='fetch')
            print(f"翌年データ削除: {result2}件")
            
            # セッションをフラッシュ
            db.session.flush()
            
            # 年度テーブルから削除
            year = Year.query.get(year_id)
            if year:
                print(f"年度テーブルからの削除: {year.year_id} ({year.display_name})")
                db.session.delete(year)
                # 削除後にセッションをフラッシュ
                db.session.flush()
            else:
                print(f"年度が見つかりません: {year_id}")
            
            # 変更をコミット
            db.session.commit()
            print(f"年度削除成功: {year_id}年度")
            return True, f"{year_id}年度を削除しました"
        except Exception as e:
            db.session.rollback()
            print(f"年度削除エラー: {str(e)}")
            return False, f"削除中にエラーが発生しました: {str(e)}"
    
    def initialize_year_records(self, year_id):
        """指定された年度の月次データを初期化する"""
        start_month = Config.FISCAL_YEAR_START_MONTH  # 通常は5月
        end_month = Config.FISCAL_YEAR_END_MONTH      # 通常は4月
        next_year = year_id + 1
        
        # 当年の5月〜12月のレコードを作成
        for month in range(start_month, 13):
            income = Income(
                year_id=year_id,
                year=year_id,
                month=month,
                monthly_total=0,
                monthly_deduction=0,
                year_end_adjustment=0,
                monthly_income=0,
                bonus_total=0,
                bonus_deduction=0,
                bonus_income=0,
                total=0,
                cumulative_total=0
            )
            db.session.add(income)
        
        # 翌年の年度データが存在しない場合は作成
        next_year_record = Year.query.get(next_year)
        if not next_year_record:
            next_year_record = Year(year_id=next_year, display_name=f"{next_year}年度")
            db.session.add(next_year_record)
            db.session.commit()
        
        # 翌年の1月〜4月のレコードを作成
        for month in range(1, end_month + 1):
            income = Income(
                year_id=year_id,
                year=next_year,
                month=month,
                monthly_total=0,
                monthly_deduction=0,
                year_end_adjustment=0,
                monthly_income=0,
                bonus_total=0,
                bonus_deduction=0,
                bonus_income=0,
                total=0,
                cumulative_total=0
            )
            db.session.add(income)
        
        db.session.commit()
        
        # 隣接する年度がすでに存在する場合は、累計計算を更新
        self._refresh_all_cumulative_totals(year_id)
    
    def _refresh_all_cumulative_totals(self, fiscal_year):
        """指定された会計年度の累計額を再計算"""
        fiscal_records = self.get_income_by_fiscal_year(fiscal_year)
        
        # 累計を計算して更新
        cumulative = 0
        for record in fiscal_records:
            # 累計に当月の合計を追加
            record_id = record['id']
            record_total = record['total']
            cumulative += record_total
            
            # 累計を更新
            income_record = Income.query.get(record_id)
            income_record.cumulative_total = cumulative
        
        db.session.commit()
        
    def get_income_by_fiscal_year(self, fiscal_year):
        """会計年度ごとの給与情報を取得
        会計年度は5月から翌年4月まで
        """
        start_month = Config.FISCAL_YEAR_START_MONTH  # 通常は5月
        end_month = Config.FISCAL_YEAR_END_MONTH      # 通常は4月
        
        print(f"Fetching data for fiscal year {fiscal_year}, start_month={start_month}, end_month={end_month}")
        
        # 指定された会計年度のデータを取得
        results = db.session.query(Income, Year.display_name)\
            .join(Year, Income.year_id == Year.year_id)\
            .filter(
                or_(
                    and_(Income.year_id == fiscal_year, Income.month >= start_month),
                    and_(Income.year_id == fiscal_year, Income.month <= end_month)
                )
            )\
            .order_by(
                case(
                    (Income.month >= start_month, Income.month - start_month),
                    else_=Income.month + (12 - start_month)
                )
            ).all()
        
        print(f"Found {len(results)} records for fiscal year {fiscal_year}")
        
        if len(results) == 0:
            # データが見つからない場合、詳細なデバッグ情報を出力
            may_dec = Income.query.filter(Income.year_id == fiscal_year, Income.month >= start_month).count()
            jan_apr = Income.query.filter(Income.year_id == fiscal_year, Income.month <= end_month).count()
            print(f"詳細: {fiscal_year}年{start_month}月～12月のレコード数: {may_dec}")
            print(f"詳細: {fiscal_year}年1月～{end_month}月のレコード数: {jan_apr}")
            
            # データがない場合は0で初期化したデータを返す
            income_list = []
            for month in range(start_month, 13):  # 5月〜12月
                income_list.append({
                    'id': 0,
                    'year_id': fiscal_year,
                    'year': fiscal_year,
                    'month': month,
                    'monthly_total': 0,
                    'monthly_deduction': 0,
                    'year_end_adjustment': 0,
                    'monthly_income': 0,
                    'bonus_total': 0,
                    'bonus_deduction': 0,
                    'bonus_income': 0,
                    'total': 0,
                    'cumulative_total': 0,
                    'display_name': f"{fiscal_year}年度"
                })
            next_year = fiscal_year + 1
            for month in range(1, end_month + 1):  # 1月〜4月
                income_list.append({
                    'id': 0,
                    'year_id': fiscal_year,
                    'year': next_year,
                    'month': month,
                    'monthly_total': 0,
                    'monthly_deduction': 0,
                    'year_end_adjustment': 0,
                    'monthly_income': 0,
                    'bonus_total': 0,
                    'bonus_deduction': 0,
                    'bonus_income': 0,
                    'total': 0,
                    'cumulative_total': 0,
                    'display_name': f"{fiscal_year}年度"
                })
            return income_list
            
        # 結果を辞書形式に変換
        income_list = []
        for income, display_name in results:
            income_dict = income.to_dict()
            income_dict['display_name'] = display_name
            income_list.append(income_dict)
            
        return income_list
    
    def get_income_summary_by_year(self):
        """年度ごとの収入合計サマリーを取得"""
        start_month = Config.FISCAL_YEAR_START_MONTH
        end_month = Config.FISCAL_YEAR_END_MONTH
        
        print(f"Calculating yearly summary with start_month={start_month}, end_month={end_month}")
        
        # SQLAlchemyでフィスカルイヤーごとの集計を行う
        fiscal_year = case(
            (Income.month >= start_month, Income.year_id),
            (Income.month <= end_month, Income.year_id)
        ).label('fiscal_year')
        
        results = db.session.query(
            fiscal_year,
            func.sum(Income.monthly_total).label('total_monthly'),
            func.sum(Income.bonus_total).label('total_bonus'),
            func.sum(Income.total).label('grand_total')
        ).group_by(fiscal_year).order_by(fiscal_year).all()
        
        print(f"Found {len(results)} yearly summary records")
        
        # 結果を辞書形式に変換
        summary_list = []
        for fiscal_year, total_monthly, total_bonus, grand_total in results:
            summary_list.append({
                'fiscal_year': fiscal_year,
                'total_monthly': total_monthly if total_monthly else 0,
                'total_bonus': total_bonus if total_bonus else 0,
                'grand_total': grand_total if grand_total else 0
            })
            
        return summary_list
    
    def update_income(self, id, monthly_total, monthly_deduction, year_end_adjustment, 
                     bonus_total, bonus_deduction):
        """給与情報を更新し、計算フィールドも更新"""
        # 計算フィールドの値を計算
        monthly_income = monthly_total - monthly_deduction + year_end_adjustment
        bonus_income = bonus_total - bonus_deduction
        total = monthly_total + bonus_total
        
        # 指定されたIDの給与情報を取得して更新
        income = Income.query.get(id)
        if not income:
            return False
            
        income.monthly_total = int(monthly_total)
        income.monthly_deduction = int(monthly_deduction)
        income.year_end_adjustment = int(year_end_adjustment)
        income.monthly_income = int(monthly_income)
        income.bonus_total = int(bonus_total)
        income.bonus_deduction = int(bonus_deduction)
        income.bonus_income = int(bonus_income)
        income.total = int(total)
        
        db.session.commit()
        
        # 累計額を更新
        self._update_cumulative_totals(id)
        
        return True
    
    def _update_cumulative_totals(self, updated_id):
        """給与情報が更新された後、そのレコードの会計年度の累計額を再計算"""
        # 更新されたレコードの年度と月を取得
        income = Income.query.get(updated_id)
        if not income:
            return False
        
        year_id = income.year_id
        month = income.month
        
        # 会計年度の開始月と終了月
        start_month = Config.FISCAL_YEAR_START_MONTH
        end_month = Config.FISCAL_YEAR_END_MONTH
        
        # 会計年度を判定
        fiscal_year = year_id
        
        # この会計年度の全レコードを取得して累計を計算
        fiscal_records = self.get_income_by_fiscal_year(fiscal_year)
        
        # 累計を計算して更新
        cumulative = 0
        for record in fiscal_records:
            # 累計に当月の合計を追加
            record_id = record['id']
            record_total = record['total']
            cumulative += record_total
            
            # 累計を更新
            income_record = Income.query.get(record_id)
            income_record.cumulative_total = cumulative
        
        db.session.commit()
        return True 