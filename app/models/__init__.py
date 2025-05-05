from app.models.database import db

# テーブル定義
class Year(db.Model):
    __tablename__ = 'years'
    
    year_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(20), nullable=False)
    
    # リレーションシップ
    incomes = db.relationship('Income', backref='year_relation', lazy=True,
                             primaryjoin="or_(Year.year_id==Income.year_id, "
                                         "Year.year_id==Income.year_id-1)")
    
    def __repr__(self):
        return f'<Year {self.year_id}>'
    
    def to_dict(self):
        return {
            'year_id': self.year_id,
            'display_name': self.display_name
        }

class Income(db.Model):
    __tablename__ = 'income'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year_id = db.Column(db.Integer, db.ForeignKey('years.year_id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    monthly_total = db.Column(db.Integer, default=0)
    monthly_deduction = db.Column(db.Integer, default=0)
    year_end_adjustment = db.Column(db.Integer, default=0)
    monthly_income = db.Column(db.Integer, default=0)
    bonus_total = db.Column(db.Integer, default=0)
    bonus_deduction = db.Column(db.Integer, default=0)
    bonus_income = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    cumulative_total = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('year_id', 'month', name='unique_year_month'),
    )
    
    def __repr__(self):
        return f'<Income {self.year_id}/{self.month}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'year_id': self.year_id,
            'year': self.year,
            'month': self.month,
            'monthly_total': self.monthly_total,
            'monthly_deduction': self.monthly_deduction,
            'year_end_adjustment': self.year_end_adjustment,
            'monthly_income': self.monthly_income,
            'bonus_total': self.bonus_total,
            'bonus_deduction': self.bonus_deduction,
            'bonus_income': self.bonus_income,
            'total': self.total,
            'cumulative_total': self.cumulative_total
        } 