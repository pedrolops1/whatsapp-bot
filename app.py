from flask import Flask, request
import requests

app = Flask(__name__)

# >>> DADOS DA ULTRAMSG
ULTRAMSG_INSTANCE_ID = "instance114233"
ULTRAMSG_TOKEN = "o5ssmoftmlqij6xl"

# >>> SUA NOVA API KEY DO OPENROUTER
OPENROUTER_API_KEY = "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"

# >>> Número autorizado para teste
NUMERO_AUTORIZADO = "+5524999797305"

# >>> Memória por telefone
conversas = {}

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    
    # Adicionando log para depuração
    print("Recebido webhook:", data)
    
    phone = data.get("data", {}).get("from")  # Exemplo: '+5524999797305'
    msg = data.get("data", {}).get("body")

    # Verificando se a mensagem e número são válidos
    if phone == NUMERO_AUTORIZADO and msg:
        print(f"Mensagem recebida de {phone}: {msg}")  # Log de mensagem recebida
        if phone not in conversas:
            conversas[phone] = []

        conversas[phone].append(msg)

        resposta = gerar_resposta_com_ia(msg, conversas[phone])
        enviar_mensagem(phone, resposta)
    else:
        print(f"Mensagem ou número não autorizado: {phone}, {msg}")  # Log de número ou mensagem não autorizado

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
        
        # Logando a resposta da API
        if resposta.status_code == 200:
            print("Resposta da IA:", resposta.json())  # Log da resposta da IA
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

    # Logando antes de enviar a mensagem
    print(f"Enviando mensagem para {phone}: {message}")
    response = requests.post(url, data=payload)

    # Verificando o status da resposta
    if response.status_code == 200:
        print(f"Mensagem enviada para {phone}")
    else:
        print(f"Erro ao enviar mensagem para {phone}: {response.text}")

# Verificando se o servidor está rodando corretamente
if __name__ == "__main__":
    app.run(debug=True)
