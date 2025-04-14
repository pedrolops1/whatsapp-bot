from flask import Flask, request, jsonify
import requests

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

    # Enviar resposta via UltraMSG
    instance_id = "instance114233"
    token = "o5ssmoftmlqij6xl"

    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    payload = {
        "to": phone,
        "body": resposta
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)

    return jsonify({"resposta": resposta}), 200
