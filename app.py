from flask import Flask, request
import requests
import sqlite3

app = Flask(__name__)

# >>> DADOS DA ULTRAMSG
ULTRAMSG_INSTANCE_ID = "instance114233"
ULTRAMSG_TOKEN = "o5ssmoftmlqij6xl"

# >>> SUA API KEY DO OPENROUTER
OPENROUTER_API_KEY = "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"

# >>> Número autorizado para teste
NUMERO_AUTORIZADO = "+5524999797305"

# >>> Configuração SQLite
DATABASE = 'conversas.db'

# Função para criar o banco de dados e a tabela de conversas
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversas (
                    numero TEXT PRIMARY KEY,
                    historico TEXT,
                    ultima_pergunta TEXT
                  )''')
    conn.commit()
    conn.close()

# Função para salvar a conversa no banco de dados
def salvar_conversa(numero, historico, ultima_pergunta):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO conversas (numero, historico, ultima_pergunta)
                 VALUES (?, ?, ?)''', (numero, str(historico), ultima_pergunta))
    conn.commit()
    conn.close()

# Função para obter o histórico de conversa do banco de dados
def obter_conversa(numero):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT historico, ultima_pergunta FROM conversas WHERE numero = ?", (numero,))
    resultado = c.fetchone()
    conn.close()
    if resultado:
        return eval(resultado[0]), resultado[1]  # Retorna o histórico como lista e a última pergunta
    else:
        return [], ""

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Recebido webhook:", data)

    phone = data.get("data", {}).get("from")  # Ex: '5524999797305@c.us'
    mensagem = data.get("data", {}).get("body")

    if phone and "@c.us" in phone:
        numero_limpo = "+" + phone.replace("@c.us", "")
    else:
        print("Formato de número não reconhecido:", phone)
        return "Ignorado", 200

    if numero_limpo != NUMERO_AUTORIZADO or not mensagem:
        print(f"Mensagem ou número não autorizado: {numero_limpo}, {mensagem}")
        return "Ignorado", 200

    # Obter o histórico de conversa e a última pergunta feita
    historico, ultima_pergunta = obter_conversa(numero_limpo)
    historico.append(mensagem)

    # Gerar a resposta com IA com o histórico atualizado e verificando a última pergunta
    resposta = gerar_resposta_com_ia(mensagem, historico, ultima_pergunta)
    
    # Salvar o histórico e a última pergunta no banco de dados
    salvar_conversa(numero_limpo, historico, resposta)

    # Enviar a resposta
    enviar_mensagem(numero_limpo, resposta)

    return "OK", 200

def gerar_resposta_com_ia(msg, historico, ultima_pergunta):
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
Seja leve, charmosa, com um toque carinhoso e responda no estilo de uma conversa casual no WhatsApp.
Use abreviações naturais como "vc", "tb", "pq", etc. e evite falar de maneira muito formal ou cheia de detalhes. Seja mais descomplicada."""
        }
    ]

    for m in historico[-5:]:
        mensagens.append({"role": "user", "content": m})

    # Se a última pergunta foi repetitiva, alteramos a maneira de perguntar
    if "Como foi o seu dia?" in ultima_pergunta:
        nova_pergunta = "E aí, teve algo de novo hoje?"
    else:
        nova_pergunta = "Como vc tá? Tudo certo?"

    mensagens.append({"role": "user", "content": nova_pergunta})

    body = {
        "model": "openai/gpt-3.5-turbo",
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

init_db()  # Garante que o banco e a tabela sejam criados mesmo no Render

if __name__ == "__main__":
    app.run(debug=True)
    
