from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/prorate', methods=['POST'])
def prorate():
    d = request.get_json(force=True)
    old_price = d['old_price']
    new_price = d['new_price']
    days_remaining = d['days_remaining']
    days_in_actual_month = d['days_in_actual_month']
    spec = d['spec']

    diff = new_price - old_price

    if spec == 'v1':
        charge = diff * (days_remaining / 30)
    elif spec == 'v2':
        charge = diff * (days_remaining / days_in_actual_month)
    else:
        return jsonify({"error": "invalid spec"}), 400

    return jsonify({"charge": charge})

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

import re

def canonicalize_args(args):
    """Sort keys, normalize whitespace in strings, drop client_ts field."""
    if isinstance(args, dict):
        result = {}
        for k, v in sorted(args.items()):
            if k == 'client_ts':
                continue
            result[k] = canonicalize_args(v)
        return result
    elif isinstance(args, list):
        return [canonicalize_args(v) for v in args]
    elif isinstance(args, str):
        return re.sub(r'\s+', ' ', args.strip())
    else:
        return args

@app.route('/check', methods=['POST'])
def check_budget():
    d = request.get_json(force=True)
    budget_tokens = d['budget_tokens']
    steps = d.get('steps', [])

    # 1. Budget check
    total_tokens = sum(s['tokens_used'] for s in steps)
    if total_tokens >= budget_tokens:
        return jsonify({
            "decision": "halt",
            "reason": f"Cumulative tokens_used ({total_tokens}) has reached the budget ({budget_tokens})."
        })

    if len(steps) == 0:
        return jsonify({"decision": "continue", "reason": "Fresh run, no steps taken yet."})

    # canonicalize all steps' (tool, args) once
    canon = [(s['tool'], canonicalize_args(s['args'])) for s in steps]

    # 2. Same tool + same args 3+ times in a row (trailing)
    run_len = 1
    for i in range(len(canon) - 1, 0, -1):
        if canon[i] == canon[i - 1]:
            run_len += 1
        else:
            break
    if run_len >= 3:
        return jsonify({
            "decision": "halt",
            "reason": f"Same tool call repeated {run_len} times in a row with identical arguments — looping."
        })

    # 3. 2-step A,B,A,B,... cycle for 6+ trailing steps
    trailing = canon[-6:] if len(canon) >= 6 else None
    if trailing:
        a, b = trailing[0], trailing[1]
        if a != b and all(trailing[i] == (a if i % 2 == 0 else b) for i in range(6)):
            return jsonify({
                "decision": "halt",
                "reason": "Trailing steps show a repeating 2-step A/B cycle for 6+ steps."
            })

    return jsonify({"decision": "continue", "reason": "Under budget, no loop detected; execution may proceed."})
