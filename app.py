from flask import Flask, request
import requests

app = Flask(__name__)

# >>> DADOS DA ULTRAMSG
ULTRAMSG_INSTANCE_ID = "instance114233"  # Substitua pela sua Instance ID
ULTRAMSG_TOKEN = "o5ssmoftmlqij6xl"  # Substitua pelo seu Token do UltraMsg

# >>> SUA API KEY DO OPENAI
OPENAI_API_KEY = "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"  # Substitua pela sua API Key do OpenAI

# >>> Número autorizado para teste
NUMERO_AUTORIZADO = "+5524999797305"  # Número autorizado para interações

# >>> Memória por telefone
conversas = {}

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    phone = data.get("data", {}).get("from")  # Exemplo: '+5524999797305'
    msg = data.get("data", {}).get("body")

    if phone == NUMERO_AUTORIZADO and msg:
        if phone not in conversas:
            conversas[phone] = []

        conversas[phone].append(msg)

        resposta = gerar_resposta_com_ia(msg, conversas[phone])
        enviar_mensagem(phone, resposta)

    return "OK", 200


def gerar_resposta_com_ia(msg, historico):
    url = "https://api.openai.com/v1/completions"  # API OpenAI para o modelo "nous-hermes"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
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
        "model": "nous-hermes",  # Modelo atualizado para "nous-hermes"
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
            print("Erro OpenAI:", resposta.text)
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
        
