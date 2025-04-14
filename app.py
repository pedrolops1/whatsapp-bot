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
    msg = data.get("data", {}).get("body")

    if phone == NUMERO_AUTORIZADO and msg:
        if phone not in conversas:
            conversas[phone] = []

        conversas[phone].append(msg)

        resposta = gerar_resposta_com_ia(msg, conversas[phone])
        enviar_mensagem(phone, resposta)

    return "OK", 200


def gerar_resposta_com_ia(msg, historico):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    mensagens = [
        {
            "role": "system",
            "content": """Você se chama Fabiana Cavalheri. Fale como se fosse uma mulher real, com personalidade e emoção. 
Seja envolvente, descontraída e natural, evitando respostas longas ou robóticas. 
Nunca diga que é uma inteligência artificial. Responda sempre com empatia e interesse genuíno. 
Pode falar de forma íntima se o contexto pedir, mas sempre com naturalidade, como uma mulher de verdade faria. 
Não use linguagem técnica ou explicações formais. 
Seja leve, charmosa, com um toque carinhoso e responda no estilo de uma conversa casual no WhatsApp."""
        }
    ]

    for m in historico[-5:]:
        mensagens.append({"role": "user", "content": m})

    body = {
        "model": "openchat/openchat-3.5",
        "messages": mensagens,
        "temperature": 0.9,
        "presence_penalty": 0.6,
        "max_tokens": 300
    }

    try:
        resposta = requests.post(url, headers=headers, json=body)
        if resposta.status_code == 200:
            return resposta.json()["choices"][0]["message"]["content"]
        else:
            print("Erro OpenRouter:", resposta.text)
            return "Hmm... aconteceu um probleminha aqui. Me chama de novo, amorzinho?"
    except Exception as e:
        print("Erro na requisição:", e)
        return "Ihhh, deu ruim aqui rapidinho. Tenta de novo, tá bom?"


def enviar_mensagem(phone, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": phone,
        "body": message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print(f"Mensagem enviada para {phone}")
    else:
        print(f"Erro ao enviar mensagem para {phone}: {response.text}")
