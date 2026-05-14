from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import os, json

load_dotenv()  # .env ファイルを自動読み込み

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
    split  = row.get('rule_split_entry', True)
    sl_tp  = row.get('rule_sl_tp_set',   True)
    chart  = row.get('rule_chart_basis',  True)
    return {
        'id':             row['id'],
        'date':           row['date'],
        'pair':           row['pair'],
        'result':         row['result'],
        'pnl':            row['pnl'],
        'commission':     row['commission'],
        'rr':             row['rr'],
        'lotSize':        row.get('lot_size', 0) or 0,
        'entryPrice':     row.get('entry_price', 0) or 0,
        'ruleSplitEntry': split,
        'ruleSlTpSet':    sl_tp,
        'ruleChartBasis': chart,
        'ruleCompliant':  split and sl_tp and chart,
        'notes':          row['notes'] or '',
        'status':         row['status'],
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
    split = bool(data.get('ruleSplitEntry', True))
    sl_tp = bool(data.get('ruleSlTpSet',    True))
    chart = bool(data.get('ruleChartBasis', True))
    row = {
        'id':                data['id'],
        'date':              data['date'],
        'pair':              data['pair'],
        'result':            data['result'],
        'pnl':               float(data.get('pnl', 0.0)),
        'commission':        float(data.get('commission', 0.0)),
        'rr':                float(data.get('rr', 0.0)),
        'lot_size':          float(data.get('lotSize', 0.0)),
        'entry_price':       float(data.get('entryPrice', 0.0)),
        'rule_split_entry':  split,
        'rule_sl_tp_set':    sl_tp,
        'rule_chart_basis':  chart,
        'rule_compliant':    split and sl_tp and chart,
        'notes':             data.get('notes', ''),
        'status':            data.get('status', 'closed'),
        'is_demo':           is_demo,
    }
    res = supabase.table('trades').insert(row).execute()
    return jsonify(row_to_trade(res.data[0])), 201

@app.route('/api/trades/<trade_id>', methods=['PUT'])
def update_trade(trade_id):
    data = request.json
    split = bool(data.get('ruleSplitEntry', True))
    sl_tp = bool(data.get('ruleSlTpSet',    True))
    chart = bool(data.get('ruleChartBasis', True))
    row = {
        'date':             data['date'],
        'pair':             data['pair'],
        'result':           data['result'],
        'pnl':              float(data.get('pnl', 0.0)),
        'commission':       float(data.get('commission', 0.0)),
        'rr':               float(data.get('rr', 0.0)),
        'lot_size':         float(data.get('lotSize', 0.0)),
        'entry_price':      float(data.get('entryPrice', 0.0)),
        'rule_split_entry': split,
        'rule_sl_tp_set':   sl_tp,
        'rule_chart_basis': chart,
        'rule_compliant':   split and sl_tp and chart,
        'notes':            data.get('notes', ''),
        'status':           data.get('status', 'closed'),
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

# --- Poker API ---

def row_to_poker(row):
    return {
        'id':                 row['id'],
        'date':               row['date'],
        'hands':              row['hands'],
        'bbSize':             row['bb_size'],
        'resultBb':           row['result_bb'],
        'ruleNoEmotion':      row['rule_no_emotion'],
        'ruleStopTilted':     row['rule_stop_tilted'],
        'ruleNoRandomCalls':  row['rule_no_random_calls'],
        'notes':              row['notes'] or '',
    }

@app.route('/api/poker', methods=['GET'])
def get_poker_sessions():
    res = supabase.table('poker_sessions').select('*').order('date').execute()
    return jsonify([row_to_poker(r) for r in res.data])

@app.route('/api/poker', methods=['POST'])
def add_poker_session():
    data = request.json
    row = {
        'id':                  data['id'],
        'date':                data['date'],
        'hands':               int(data.get('hands', 0)),
        'bb_size':             float(data.get('bbSize', 1)),
        'result_bb':           float(data.get('resultBb', 0)),
        'rule_no_emotion':     bool(data.get('ruleNoEmotion', True)),
        'rule_stop_tilted':    bool(data.get('ruleStopTilted', True)),
        'rule_no_random_calls':bool(data.get('ruleNoRandomCalls', True)),
        'notes':               data.get('notes', ''),
    }
    res = supabase.table('poker_sessions').insert(row).execute()
    return jsonify(row_to_poker(res.data[0])), 201

@app.route('/api/poker/<session_id>', methods=['PUT'])
def update_poker_session(session_id):
    data = request.json
    row = {
        'date':                data['date'],
        'hands':               int(data.get('hands', 0)),
        'bb_size':             float(data.get('bbSize', 1)),
        'result_bb':           float(data.get('resultBb', 0)),
        'rule_no_emotion':     bool(data.get('ruleNoEmotion', True)),
        'rule_stop_tilted':    bool(data.get('ruleStopTilted', True)),
        'rule_no_random_calls':bool(data.get('ruleNoRandomCalls', True)),
        'notes':               data.get('notes', ''),
    }
    res = supabase.table('poker_sessions').update(row).eq('id', session_id).execute()
    if not res.data:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(row_to_poker(res.data[0]))

@app.route('/api/poker/<session_id>', methods=['DELETE'])
def delete_poker_session(session_id):
    supabase.table('poker_sessions').delete().eq('id', session_id).execute()
    return jsonify({'success': True})

# --- Poker Daily Checkins ---

def row_to_checkin(row):
    return {'date': row['date'], 'todoGto': row['todo_gto']}

@app.route('/api/poker/checkins', methods=['GET'])
def get_poker_checkins():
    res = supabase.table('poker_daily_checkins').select('*').execute()
    return jsonify([row_to_checkin(r) for r in res.data])

@app.route('/api/poker/checkins', methods=['POST'])
def upsert_poker_checkin():
    data = request.json
    row = {'date': data['date'], 'todo_gto': bool(data.get('todoGto', False))}
    res = supabase.table('poker_daily_checkins').upsert(row, on_conflict='date').execute()
    return jsonify(row_to_checkin(res.data[0]))

# --- Prediction Market Bets ---

def row_to_prediction(row):
    return {
        'id':             row['id'],
        'date':           row['date'],
        'category':       row['category'],
        'title':          row['title'],
        'betAmount':      row['bet_amount'],
        'resultUsd':      row['result_usd'],  # None = pending bet
        'rulePositiveEv': row['rule_positive_ev'],
        'ruleUsedEvCalc': row['rule_used_ev_calc'],
        'notes':          row['notes'] or '',
    }

def parse_result_usd(data):
    v = data.get('resultUsd')
    if v is None or v == '':
        return None
    return float(v)

@app.route('/api/prediction', methods=['GET'])
def get_prediction_bets():
    res = supabase.table('prediction_bets').select('*').order('date').execute()
    return jsonify([row_to_prediction(r) for r in res.data])

@app.route('/api/prediction', methods=['POST'])
def add_prediction_bet():
    data = request.json
    row = {
        'id':               data['id'],
        'date':             data['date'],
        'category':         data.get('category', ''),
        'title':            data.get('title', ''),
        'bet_amount':       float(data.get('betAmount', 0)),
        'result_usd':       parse_result_usd(data),
        'rule_positive_ev':  bool(data.get('rulePositiveEv', True)),
        'rule_used_ev_calc': bool(data.get('ruleUsedEvCalc', True)),
        'notes':            data.get('notes', ''),
    }
    res = supabase.table('prediction_bets').insert(row).execute()
    return jsonify(row_to_prediction(res.data[0])), 201

@app.route('/api/prediction/<bet_id>', methods=['PUT'])
def update_prediction_bet(bet_id):
    data = request.json
    row = {
        'date':             data['date'],
        'category':         data.get('category', ''),
        'title':            data.get('title', ''),
        'bet_amount':       float(data.get('betAmount', 0)),
        'result_usd':       parse_result_usd(data),
        'rule_positive_ev':  bool(data.get('rulePositiveEv', True)),
        'rule_used_ev_calc': bool(data.get('ruleUsedEvCalc', True)),
        'notes':            data.get('notes', ''),
    }
    res = supabase.table('prediction_bets').update(row).eq('id', bet_id).execute()
    if not res.data:
        return jsonify({'error': 'Bet not found'}), 404
    return jsonify(row_to_prediction(res.data[0]))

@app.route('/api/prediction/<bet_id>', methods=['DELETE'])
def delete_prediction_bet(bet_id):
    supabase.table('prediction_bets').delete().eq('id', bet_id).execute()
    return jsonify({'success': True})

# --- Poker Hand Reviews ---

def row_to_hand(row):
    def jl(s, default):
        try: return json.loads(s or default)
        except: return json.loads(default)
    return {
        'id':              row['id'],
        'date':            row['date'],
        'heroPosition':    row['hero_position'],
        'villainPosition': row['villain_position'],
        'heroHand':        jl(row['hero_hand'],   '[]'),
        'villainHand':     jl(row['villain_hand'], '[]'),
        'flopBoard':       jl(row['flop_board'],   '[]'),
        'turnCard':        jl(row['turn_card'],    'null'),
        'riverCard':       jl(row['river_card'],   'null'),
        'preflopPotBb':    row['preflop_pot_bb'],
        'preflopAction':   row['preflop_action'],
        'preflopMemo':     row['preflop_memo'],
        'flopPotBb':       row['flop_pot_bb'],
        'flopAction':      row['flop_action'],
        'flopMemo':        row['flop_memo'],
        'turnPotBb':       row['turn_pot_bb'],
        'turnAction':      row['turn_action'],
        'turnMemo':        row['turn_memo'],
        'riverPotBb':      row['river_pot_bb'],
        'riverAction':     row['river_action'],
        'riverMemo':       row['river_memo'],
        'resultBb':        row['result_bb'],
        'notes':           row['notes'] or '',
    }

def hand_to_row(data):
    return {
        'date':             data['date'],
        'hero_position':    data.get('heroPosition', ''),
        'villain_position': data.get('villainPosition', ''),
        'hero_hand':        json.dumps(data.get('heroHand', [])),
        'villain_hand':     json.dumps(data.get('villainHand', [])),
        'flop_board':       json.dumps(data.get('flopBoard', [])),
        'turn_card':        json.dumps(data.get('turnCard')),
        'river_card':       json.dumps(data.get('riverCard')),
        'preflop_pot_bb':   float(data.get('preflopPotBb', 0)),
        'preflop_action':   data.get('preflopAction', ''),
        'preflop_memo':     data.get('preflopMemo', ''),
        'flop_pot_bb':      float(data.get('flopPotBb', 0)),
        'flop_action':      data.get('flopAction', ''),
        'flop_memo':        data.get('flopMemo', ''),
        'turn_pot_bb':      float(data.get('turnPotBb', 0)),
        'turn_action':      data.get('turnAction', ''),
        'turn_memo':        data.get('turnMemo', ''),
        'river_pot_bb':     float(data.get('riverPotBb', 0)),
        'river_action':     data.get('riverAction', ''),
        'river_memo':       data.get('riverMemo', ''),
        'result_bb':        float(data['resultBb']) if data.get('resultBb') not in (None, '') else None,
        'notes':            data.get('notes', ''),
    }

@app.route('/api/poker/hands', methods=['GET'])
def get_hand_reviews():
    res = supabase.table('poker_hand_reviews').select('*').order('date', desc=True).execute()
    return jsonify([row_to_hand(r) for r in res.data])

@app.route('/api/poker/hands', methods=['POST'])
def add_hand_review():
    data = request.json
    row = {'id': data['id'], **hand_to_row(data)}
    res = supabase.table('poker_hand_reviews').insert(row).execute()
    return jsonify(row_to_hand(res.data[0])), 201

@app.route('/api/poker/hands/<hand_id>', methods=['PUT'])
def update_hand_review(hand_id):
    data = request.json
    res = supabase.table('poker_hand_reviews').update(hand_to_row(data)).eq('id', hand_id).execute()
    if not res.data:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(row_to_hand(res.data[0]))

@app.route('/api/poker/hands/<hand_id>', methods=['DELETE'])
def delete_hand_review(hand_id):
    supabase.table('poker_hand_reviews').delete().eq('id', hand_id).execute()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
