from flask import Flask, render_template, request, jsonify
from models import db, Trade, Settings
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'trading.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    # Initialize default settings if not exists
    if not Settings.query.first():
        default_settings = Settings()
        db.session.add(default_settings)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

# --- Trades API ---

@app.route('/api/trades', methods=['GET'])
def get_trades():
    is_demo = request.args.get('demo', 'false').lower() == 'true'
    trades = Trade.query.filter_by(is_demo=is_demo).all()
    return jsonify([trade.to_dict() for trade in trades])

@app.route('/api/trades', methods=['POST'])
def add_trade():
    data = request.json
    is_demo = request.args.get('demo', 'false').lower() == 'true'
    
    trade = Trade(
        id=data['id'],
        date=data['date'],
        pair=data['pair'],
        result=data['result'],
        pnl=data.get('pnl', 0.0),
        commission=data.get('commission', 0.0),
        rr=data.get('rr', 0.0),
        ruleCompliant=data.get('ruleCompliant', True),
        notes=data.get('notes', ''),
        status=data.get('status', 'closed'),
        is_demo=is_demo
    )
    db.session.add(trade)
    db.session.commit()
    return jsonify(trade.to_dict()), 201

@app.route('/api/trades/<trade_id>', methods=['PUT'])
def update_trade(trade_id):
    data = request.json
    trade = Trade.query.get(trade_id)
    if not trade:
        return jsonify({'error': 'Trade not found'}), 404
        
    trade.date = data.get('date', trade.date)
    trade.pair = data.get('pair', trade.pair)
    trade.result = data.get('result', trade.result)
    trade.pnl = data.get('pnl', trade.pnl)
    trade.commission = data.get('commission', trade.commission)
    trade.rr = data.get('rr', trade.rr)
    trade.ruleCompliant = data.get('ruleCompliant', trade.ruleCompliant)
    trade.notes = data.get('notes', trade.notes)
    trade.status = data.get('status', trade.status)
    
    db.session.commit()
    return jsonify(trade.to_dict())

@app.route('/api/trades/<trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    trade = Trade.query.get(trade_id)
    if not trade:
        return jsonify({'error': 'Trade not found'}), 404
        
    db.session.delete(trade)
    db.session.commit()
    return jsonify({'success': True})

# --- Settings API ---

@app.route('/api/settings', methods=['GET'])
def get_settings():
    settings = Settings.query.first()
    return jsonify(settings.to_dict())

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    settings = Settings.query.first()
    
    for key, value in data.items():
        if hasattr(settings, key):
            setattr(settings, key, float(value) if value != '' else 0.0)
            
    db.session.commit()
    return jsonify(settings.to_dict())

if __name__ == '__main__':
    app.run(debug=True, port=5001)
