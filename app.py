from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DEFAULT_SETTINGS = {
    'initialBalance': 1000.0,
    'monthlyTargetPct': 20.0,
    'dailyLossLimitPct': 6.0,
    'monthlyDDLimitPct': 10.0,
    'minWinRate': 50.0,
    'minRR': 2.0,
    'minComplianceRate': 90.0,
    'maxRiskPerTradePct': 2.0,
    'demoInitialBalance': 10000.0,
}

def row_to_trade(row):
    return {
        'id': row['id'],
        'date': row['date'],
        'pair': row['pair'],
        'result': row['result'],
        'pnl': row['pnl'],
        'commission': row['commission'],
        'rr': row['rr'],
        'ruleCompliant': row['rule_compliant'],
        'notes': row['notes'] or '',
        'status': row['status'],
    }

def row_to_settings(row):
    return {
        'initialBalance': row['initial_balance'],
        'monthlyTargetPct': row['monthly_target_pct'],
        'dailyLossLimitPct': row['daily_loss_limit_pct'],
        'monthlyDDLimitPct': row['monthly_dd_limit_pct'],
        'minWinRate': row['min_win_rate'],
        'minRR': row['min_rr'],
        'minComplianceRate': row['min_compliance_rate'],
        'maxRiskPerTradePct': row['max_risk_per_trade_pct'],
        'demoInitialBalance': row['demo_initial_balance'],
    }

def settings_to_row(data):
    return {
        'initial_balance': float(data.get('initialBalance', DEFAULT_SETTINGS['initialBalance'])),
        'monthly_target_pct': float(data.get('monthlyTargetPct', DEFAULT_SETTINGS['monthlyTargetPct'])),
        'daily_loss_limit_pct': float(data.get('dailyLossLimitPct', DEFAULT_SETTINGS['dailyLossLimitPct'])),
        'monthly_dd_limit_pct': float(data.get('monthlyDDLimitPct', DEFAULT_SETTINGS['monthlyDDLimitPct'])),
        'min_win_rate': float(data.get('minWinRate', DEFAULT_SETTINGS['minWinRate'])),
        'min_rr': float(data.get('minRR', DEFAULT_SETTINGS['minRR'])),
        'min_compliance_rate': float(data.get('minComplianceRate', DEFAULT_SETTINGS['minComplianceRate'])),
        'max_risk_per_trade_pct': float(data.get('maxRiskPerTradePct', DEFAULT_SETTINGS['maxRiskPerTradePct'])),
        'demo_initial_balance': float(data.get('demoInitialBalance', DEFAULT_SETTINGS['demoInitialBalance'])),
    }

@app.route('/')
def index():
    return render_template('index.html')

# --- Trades API ---

@app.route('/api/trades', methods=['GET'])
def get_trades():
    is_demo = request.args.get('demo', 'false').lower() == 'true'
    res = supabase.table('trades').select('*').eq('is_demo', is_demo).order('date').execute()
    return jsonify([row_to_trade(r) for r in res.data])

@app.route('/api/trades', methods=['POST'])
def add_trade():
    data = request.json
    is_demo = request.args.get('demo', 'false').lower() == 'true'
    row = {
        'id': data['id'],
        'date': data['date'],
        'pair': data['pair'],
        'result': data['result'],
        'pnl': float(data.get('pnl', 0.0)),
        'commission': float(data.get('commission', 0.0)),
        'rr': float(data.get('rr', 0.0)),
        'rule_compliant': bool(data.get('ruleCompliant', True)),
        'notes': data.get('notes', ''),
        'status': data.get('status', 'closed'),
        'is_demo': is_demo,
    }
    res = supabase.table('trades').insert(row).execute()
    return jsonify(row_to_trade(res.data[0])), 201

@app.route('/api/trades/<trade_id>', methods=['PUT'])
def update_trade(trade_id):
    data = request.json
    row = {
        'date': data['date'],
        'pair': data['pair'],
        'result': data['result'],
        'pnl': float(data.get('pnl', 0.0)),
        'commission': float(data.get('commission', 0.0)),
        'rr': float(data.get('rr', 0.0)),
        'rule_compliant': bool(data.get('ruleCompliant', True)),
        'notes': data.get('notes', ''),
        'status': data.get('status', 'closed'),
    }
    res = supabase.table('trades').update(row).eq('id', trade_id).execute()
    if not res.data:
        return jsonify({'error': 'Trade not found'}), 404
    return jsonify(row_to_trade(res.data[0]))

@app.route('/api/trades/<trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    supabase.table('trades').delete().eq('id', trade_id).execute()
    return jsonify({'success': True})

# --- Settings API ---

@app.route('/api/settings', methods=['GET'])
def get_settings():
    res = supabase.table('settings').select('*').limit(1).execute()
    if res.data:
        return jsonify(row_to_settings(res.data[0]))
    return jsonify(DEFAULT_SETTINGS)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    row = settings_to_row(data)
    res = supabase.table('settings').select('id').limit(1).execute()
    if res.data:
        sid = res.data[0]['id']
        updated = supabase.table('settings').update(row).eq('id', sid).execute()
    else:
        updated = supabase.table('settings').insert(row).execute()
    return jsonify(row_to_settings(updated.data[0]))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
