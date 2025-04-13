from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot funcionando!"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    phone = data.get('data', {}).get('from')
    message = data.get('data', {}).get('body')

    print(f"Mensagem de {phone}: {message}")

        resposta = ""

    if "oi" in message.lower():
        resposta = "Oi amor, tudo bem?"
    elif "tá aí" in message.lower() or "ta ai" in message.lower():
        resposta = "Tô sim, tava pensando em você..."
    elif any(palavra in message.lower() for palavra in ["gostosa", "safada", "delícia", "tesão"]):
        resposta = "Hmm... você tá meio saidinho hoje, hein? Me conta mais..."
    else:
        resposta = "Awn, adorei sua mensagem... me conta mais sobre isso!"

    print(f"Resposta enviada: {resposta}")

    return jsonify({"resposta": "Mensagem recebida com sucesso!"}), 200
