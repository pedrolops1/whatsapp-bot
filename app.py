from flask import Flask, request
import requests

app = Flask(__name__)

ULTRAMSG_INSTANCE_ID = "instance114233"
ULTRAMSG_TOKEN = "o5ssmoftmlqij6xl"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    phone = data.get('data', {}).get('from')  # ex: '5524999797305'
    message = data.get('data', {}).get('body')

    if phone and message:
        resposta = gerar_resposta(message)
        enviar_mensagem(phone, resposta)

    return 'OK', 200

def gerar_resposta(msg):
    # Aqui você pode personalizar suas respostas automáticas
    return f"Você disse: {msg}"

def enviar_mensagem(phone, texto):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": phone,
        "body": texto
    }
    requests.post(url, data=payload)

if __name__ == '__main__':
    app.run()
