import os
from flask import Flask, request
import telebot

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

usuarios = {}

@app.route("/", methods=["GET"])
def home():
    return "Bot RH online"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# COMANDO /start
@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user.id

    usuarios[user] = {
        "etapa": 1,
        "respostas": []
    }

    bot.reply_to(message,
        "👋 Olá!\n\n"
        "Este é um espaço *100% anônimo* para você compartilhar sua percepção sobre a liderança.\n\n"
        "Sinta-se à vontade para responder com sinceridade.\n\n"
        "👉 Como você avalia a atuação da gestão no apoio às suas atividades diárias?",
        parse_mode="Markdown"
    )

# FLUXO PRINCIPAL
@bot.message_handler(func=lambda message: True)
def responder(message):
    user = message.from_user.id
    texto = message.text

    if user not in usuarios:
        bot.reply_to(message, "Digite /start para iniciar 🙂")
        return

    etapa = usuarios[user]["etapa"]

    # ETAPA 1
    if etapa == 1:
        usuarios[user]["respostas"].append(texto)
        usuarios[user]["etapa"] = 2

        bot.reply_to(message,
            "Entendo 👍\n\n"
            "👉 As demandas atuais estão claras e bem distribuídas pela liderança?"
        )

    # ETAPA 2
    elif etapa == 2:
        usuarios[user]["respostas"].append(texto)
        usuarios[user]["etapa"] = 3

        bot.reply_to(message,
            "Obrigado por compartilhar.\n\n"
            "👉 Você considera que a carga de trabalho está adequada ou há sobrecarga?"
        )

    # ETAPA 3
    elif etapa == 3:
        usuarios[user]["respostas"].append(texto)
        usuarios[user]["etapa"] = 4

        bot.reply_to(message,
            "Perfeito.\n\n"
            "👉 O que a gestão poderia melhorar para facilitar a execução das suas demandas?"
        )

    # FINAL (ETAPA 4)
    elif etapa == 4:
        usuarios[user]["respostas"].append(texto)

        r1, r2, r3, r4 = usuarios[user]["respostas"]

        resumo = f"""
📊 *RESUMO DO FEEDBACK*

Avaliação do suporte da gestão:  
👉 {r1}

Clareza na distribuição de demandas:  
👉 {r2}

Percepção sobre carga de trabalho:  
👉 {r3}

Sugestões de melhoria:  
👉 {r4}
"""

        bot.reply_to(message,
            "✅ Entrevista concluída!\n\n"
            f"{resumo}\n\n"
            "📌 Solicitamos que, após responder à entrevista sobre a liderança e sua rotina no ambiente de trabalho, "
            "seja realizado um print da participação e enviado neste canal:\n"
            "https://forms.gle/3zftakgirW51eRgt5\n\n"
            "📌 Posteriormente, após a reunião com a gestão, pedimos que acesse o link abaixo para avaliar como foi o feedback recebido:\n"
            "https://forms.gle/paqCERk6bXUDsAwS8\n\n"
            "Ressaltamos que sua participação é essencial e todas as respostas serão tratadas de forma anônima.\n\n"
            "🙏 Agradecemos pela colaboração.",
            parse_mode="Markdown"
        )

        del usuarios[user]

# inicialização
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("RENDER_EXTERNAL_URL") + "/" + TOKEN)
    app.run(host="0.0.0.0", port=10000)