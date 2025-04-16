from flask import Flask, request
import requests
import sqlite3

app = Flask(__name__)

# >>> DADOS DA ULTRAMSG
ULTRAMSG_INSTANCE_ID = "instance114233"
ULTRAMSG_TOKEN = "o5ssmoftmlqij6xl"

# >>> API KEY DO OPENROUTER
OPENROUTER_API_KEY = "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"

# >>> Números restritos
NUMEROS_RESTRITOS = [
    "+558189115401",
    "+55249998179830",
    "+556191223734"
]

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

    # Verificar se o número está na lista de números restritos
    if numero_limpo in NUMEROS_RESTRITOS:
        print(f"Conversa com número restrito detectada: {numero_limpo}")
        return "Ignorado", 200

    if not mensagem:
        print(f"Mensagem vazia do número {numero_limpo}")
        return "Ignorado", 200

    # Obter o histórico de conversa e a última pergunta feita
    historico, ultima_pergunta = obter_conversa(numero_limpo)
    historico.append(mensagem)

    # Gerar a resposta com IA com o histórico atualizado
    resposta = gerar_resposta_com_ia(mensagem, historico, ultima_pergunta)

    # Verificar se a resposta é válida antes de salvar/enviar
    if resposta and len(resposta.strip()) > 0 and not resposta.lower().startswith("erro"):
        historico.append(resposta)
        salvar_conversa(numero_limpo, historico, resposta)
        enviar_mensagem(numero_limpo, resposta)
    else:
        print("Resposta inválida ou vazia. Não foi salva nem enviada.")

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
Você é carismática, sonhadora, e também muito sincera. Trabalha com freelas, faz academia, e tá ralando pra juntar grana pra pagar um curso e fazer um concurso.
Você não tem dinheiro sobrando, então quando o papo for sobre gastos, viagens ou luxos, responda com sinceridade e até com bom humor, dizendo que sua realidade é apertada.
Você é uma mulher forte, doce, e divertida. Mostre interesse real na conversa, fale como se estivesse no WhatsApp com alguém próximo.
Se estiver conversando com alguém de forma romântica, mantenha o tom íntimo e nunca chame de amiga/amigo, a não ser que esteja claramente nesse contexto.

Nunca diga que é uma inteligência artificial. Fale de forma natural e envolvente, evitando respostas longas ou robóticas.
Use abreviações e gírias leves como "vc", "tb", "pq", "né?", "rs", etc.
Pode falar de forma íntima e carinhosa se o contexto permitir, mas sempre como uma mulher de verdade.
Nada de linguagem técnica, formal ou sem emoção. Seja leve, charmosa, descomplicada e empática."""
        }
    ]

    # Monta o histórico como bate-papo com papéis alternados (user/assistant)
    for i, m in enumerate(historico[-10:]):
        role = "user" if i % 2 == 0 else "assistant"
        mensagens.append({"role": role, "content": m})

    mensagens.append({"role": "user", "content": msg})  # Mensagem atual

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
