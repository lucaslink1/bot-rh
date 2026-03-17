import os
from flask import Flask, request
import telebot

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

usuarios = {}

# rota base (só pra testar se tá online)
@app.route("/", methods=["GET"])
def home():
    return "Bot online"

# webhook do telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# lógica do chatbot
@bot.message_handler(func=lambda message: True)
def responder(message):
    user = message.from_user.username or "anon"
    texto = message.text

    # PRIMEIRA INTERAÇÃO
    if user not in usuarios:
        usuarios[user] = {"etapa": 1, "respostas": []}
        bot.reply_to(message,
            "Olá! Sou um consultor de RH e estou aqui para te ouvir.\n\n"
            "👉 No geral, como você avalia o suporte e a clareza que recebe da sua gestão direta hoje?"
        )
        return

    etapa = usuarios[user]["etapa"]
    usuarios[user]["respostas"].append(texto)

    # PERGUNTA 2
    if etapa == 1:
        usuarios[user]["etapa"] = 2
        bot.reply_to(message,
            "Entendo. 👉 O que você considera que a gestão faz muito bem e deve continuar fazendo?"
        )

    # PERGUNTA 3
    elif etapa == 2:
        usuarios[user]["etapa"] = 3
        bot.reply_to(message,
            "Obrigado por compartilhar. 👉 Qual é o principal ponto de melhoria, algo que a liderança precisa mudar ou dar mais atenção?"
        )

    # FINAL
    elif etapa == 3:
        r1, r2, r3 = usuarios[user]["respostas"]

        resumo = f"""
RESUMO DO FEEDBACK:

O colaborador avalia que o suporte e a clareza da gestão {r1.lower()}.

Em relação aos pontos positivos, destaca que a gestão {r2.lower()}.

Como principal ponto de melhoria, aponta que a liderança precisa {r3.lower()}.
"""

        bot.reply_to(message,
            "Obrigado por compartilhar sua visão. A entrevista foi concluída.\n\n"
            f"{resumo}\n\n"
            "Pronto! Para que o RH receba sua opinião de forma 100% anônima, "
            "por favor, copie o resumo acima e cole neste link:\n"
            "https://forms.gle/SEU_LINK_AQUI"
        )

        del usuarios[user]

# inicialização
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("RENDER_EXTERNAL_URL") + "/" + TOKEN)
    app.run(host="0.0.0.0", port=10000)