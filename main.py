from flask import Flask, jsonify, request, Response
import heapq
from collections import defaultdict

transactions = []
balances = defaultdict(int)
counter = 0

app = Flask(__name__) 

@app.route('/add', methods = ['POST'])
def add():
    global counter
    req = request.get_json()
    if not req:
        return "Invalid JSON\n", 400
    string = req["timestamp"]
    string = string.replace("T", "-")
    string = string.replace("Z", "-")
    string = string.replace(":", "-")
    sort_order = []
    i = 0
    while i < len(string) - 1:
        mini = []
        y = i
        while string[y] != '-':
            mini.append(int(string[y]))
            y += 1
        s = map(str, mini)
        num = ''.join(s)
        num = int(num)
        sort_order.append(num)
        i = y + 1
    sort_order.append(counter)
    counter += 1
    sort_order = tuple(sort_order)
    heapq.heappush(transactions, (sort_order, req))
    balances[req["payer"]] += req["points"]
    return Response(status=200)

@app.route('/spend', methods = ['POST'])
def spend():
    req = request.get_json()
    if not req:
        return "Invalid JSON\n", 400
    points = req["points"]
    if sum(balances.values()) < points:
        return "Not Enough Points\n", 400
    res_dict = defaultdict(int)
    while transactions:
        cur_transaction = transactions[0][1]
        if points < cur_transaction["points"]:
            transactions[0][1]["points"] -= points
            res_dict[cur_transaction["payer"]] -= points
            balances[cur_transaction["payer"]] -= points
            points = 0
        else:
            points -= transactions[0][1]["points"]
            res_dict[cur_transaction["payer"]] -= transactions[0][1]["points"]
            balances[cur_transaction["payer"]] -= transactions[0][1]["points"]
            heapq.heappop(transactions)
            
        if points == 0:
            json_array = jsonify([{"payer": key, "points": value} for key, value in res_dict.items()])
            return json_array, 200
    return Response(status=400)

@app.route('/balance', methods = ['GET'])
def balance():
    return jsonify(balances), 200
    
if __name__ == '__main__': 
    app.run(debug=True, port=8000)