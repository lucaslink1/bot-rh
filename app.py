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
        "👉 No geral, como você avalia o suporte e a clareza que recebe da sua gestão direta hoje?",
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
            "👉 O que você considera que a gestão faz muito bem e deve continuar fazendo?"
        )

    # ETAPA 2
    elif etapa == 2:
        usuarios[user]["respostas"].append(texto)
        usuarios[user]["etapa"] = 3

        bot.reply_to(message,
            "Obrigado por compartilhar.\n\n"
            "👉 Qual é o principal ponto de melhoria, algo que a liderança precisa mudar ou dar mais atenção?"
        )

    # FINAL
    elif etapa == 3:
        usuarios[user]["respostas"].append(texto)
        r1, r2, r3 = usuarios[user]["respostas"]

        resumo = f"""
📊 *RESUMO DO FEEDBACK*

O colaborador avalia que o suporte e a clareza da gestão:  
👉 {r1}

Pontos positivos destacados:  
👉 {r2}

Principais oportunidades de melhoria:  
👉 {r3}
"""

        bot.reply_to(message,
            "✅ Entrevista concluída!\n\n"
            f"{resumo}\n\n"
            "📌 Para enviar sua resposta de forma totalmente anônima, copie o resumo acima e cole neste formulário:\n"
            "https://forms.gle/fD7apMXa5rNFhRNK9",
            parse_mode="Markdown"
        )

        del usuarios[user]

# inicialização
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("RENDER_EXTERNAL_URL") + "/" + TOKEN)
    app.run(host="0.0.0.0", port=10000)