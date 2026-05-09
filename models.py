from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Trade(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    pair = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(20), nullable=False)
    pnl = db.Column(db.Float, nullable=False, default=0.0)
    commission = db.Column(db.Float, nullable=False, default=0.0)
    rr = db.Column(db.Float, nullable=False, default=0.0)
    ruleCompliant = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='closed')
    is_demo = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'pair': self.pair,
            'result': self.result,
            'pnl': self.pnl,
            'commission': self.commission,
            'rr': self.rr,
            'ruleCompliant': self.ruleCompliant,
            'notes': self.notes,
            'status': self.status
        }

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    initialBalance = db.Column(db.Float, nullable=False, default=1000.0)
    monthlyTargetPct = db.Column(db.Float, nullable=False, default=20.0)
    dailyLossLimitPct = db.Column(db.Float, nullable=False, default=6.0)
    monthlyDDLimitPct = db.Column(db.Float, nullable=False, default=10.0)
    minWinRate = db.Column(db.Float, nullable=False, default=50.0)
    minRR = db.Column(db.Float, nullable=False, default=2.0)
    minComplianceRate = db.Column(db.Float, nullable=False, default=90.0)
    maxRiskPerTradePct = db.Column(db.Float, nullable=False, default=2.0)
    demoInitialBalance = db.Column(db.Float, nullable=False, default=10000.0)

    def to_dict(self):
        return {
            'initialBalance': self.initialBalance,
            'monthlyTargetPct': self.monthlyTargetPct,
            'dailyLossLimitPct': self.dailyLossLimitPct,
            'monthlyDDLimitPct': self.monthlyDDLimitPct,
            'minWinRate': self.minWinRate,
            'minRR': self.minRR,
            'minComplianceRate': self.minComplianceRate,
            'maxRiskPerTradePct': self.maxRiskPerTradePct,
            'demoInitialBalance': self.demoInitialBalance
        }
