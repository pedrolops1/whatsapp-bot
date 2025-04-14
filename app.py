from flask import Flask, request
import requests

app = Flask(__name__)

# >>> DADOS DA ULTRAMSG
ULTRAMSG_INSTANCE_ID = "instance114233"
ULTRAMSG_TOKEN = "o5ssmoftmlqij6xl"

# >>> SUA API KEY DO OPENROUTER
OPENROUTER_API_KEY = "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"

# >>> Número autorizado para teste
NUMERO_AUTORIZADO = "+5524999797305"

# >>> Memória por telefone
conversas = {}

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    phone = data.get("data", {}).get("from")  # exemplo: '+5524999797305'
    message
