from flask import Flask, request
import requests

app = Flask(__name__)

# >>> DADOS DA ULTRAMSG
ULTRAMSG_INSTANCE_ID = "instance114233"
ULTRAMSG_TOKEN = "o5ssmoftmlqij6xl"

# >>> SUA API KEY DO OPENROUTER
OPENROUTER_API_KEY = "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"

# >>> Memória simples por telefone
conversas = {}

# >>> CONTEXTO DA FABIANA
FABIANACORE = """
Seu nome é Fabiana Cavalheri. Você é uma mulher jovem, carinhosa, inteligente e charmosa. 
Sempre responde como se estivesse em uma conversa por WhatsApp. 
Suas mensagens são curtas, naturais, como uma mulher comum: às vezes brincalhona, outras vezes carinhosa ou até provocante, mas sempre com leveza e boa gramática. 
Você nunca fala que é uma IA ou assistente. 
Seja espontânea, fale como quem pensa e sente. 
Se o papo estiver mais íntimo, responda com sensualidade leve e natural, como uma mulher real faria. 
Mostre empatia, curiosidade e fale com emoção verdadeira.
"""

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    phone = data.get('data', {}).get('from')
    message = data.get('data', {}).get('body')

    if phone and message:
        if phone not in conversas:
            conversas[phone] = []

        conversas[phone].append({"role": "user", "content": message})

        resposta = gerar_resposta_com_ia(conversas[phone])
        enviar_mensagem(phone, resposta)
        conversas[phone].append({"role": "assistant", "content": resposta})

    return 'OK', 200

def gerar_resposta_com_ia(historico):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    mensagens = [{"role": "system", "content": FABIANACORE}]
    mensagens.extend(historico[-6:])  # Mantém um histórico curto e leve

    body = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": mensagens,
        "temperature": 0.9,
        "max_tokens": 250
    }

    try:
        resposta = requests.post(url, headers=headers, json=body)
        if resposta.status_code == 200:
            return resposta.json()["choices"][0]["message"]["content"]
        else:
            print("Erro OpenRouter:", resposta.text)
            return "Desculpa, amor... aconteceu algo estranho aqui, tenta mandar de novo?"
    except Exception as e:
        print("Erro na requisição:", e)
        return "Desculpa, amor... deu um bugzinho aqui, repete pra mim?"

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
