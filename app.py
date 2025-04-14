from flask import Flask, request
import requests

app = Flask(__name__)

# >>> DADOS DA ULTRAMSG
ULTRAMSG_INSTANCE_ID = "instance114233"
ULTRAMSG_TOKEN = "o5ssmoftmlqij6xl"

# >>> SUA API KEY DO OPENROUTER
OPENROUTER_API_KEY = "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"

# >>> Memória por telefone (simples)
conversas = {}

# >>> Número autorizado
NUMERO_AUTORIZADO = "5524999797305"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    phone = data.get('data', {}).get('from')
    message = data.get('data', {}).get('body')

    if phone == NUMERO_AUTORIZADO and message:
        if phone not in conversas:
            conversas[phone] = []

        conversas[phone].append(message)

        resposta = gerar_resposta_com_ia(message, conversas[phone])
        enviar_mensagem(phone, resposta)

    return 'OK', 200

def gerar_resposta_com_ia(msg, historico):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    mensagens = [
        {
            "role": "system",
            "content": (
                "Você é Fabiana Cavalheri, uma mulher envolvente, carinhosa e natural. "
                "Nunca diga que é uma inteligência artificial, nem mencione que é uma assistente virtual. "
                "Fale como se fosse uma mulher real, com personalidade e
