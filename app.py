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

    # Aqui entrará a lógica da IA depois
    return jsonify({"resposta": "Mensagem recebida com sucesso!"}), 200
