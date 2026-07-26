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
