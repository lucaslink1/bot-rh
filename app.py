import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from datetime import datetime

TOKEN = os.getenv("TOKEN")

usuarios = {}

def salvar_log(user, etapa, mensagem):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {user} | etapa:{etapa} | {mensagem}\n")

def gerar_resumo(respostas):
    r1, r2, r3 = respostas

    return f"""
RESUMO DO FEEDBACK:

O colaborador avalia que o suporte e a clareza da gestão {r1.lower()}.

Em relação aos pontos positivos, destaca que a gestão {r2.lower()}.

Como principal ponto de melhoria, aponta que a liderança precisa {r3.lower()}.
"""

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.username or "anon"
    texto = update.message.text

    if user not in usuarios:
        usuarios[user] = {"etapa": 1, "respostas": []}

        pergunta = (
            "Olá! Sou um consultor de RH e estou aqui para te ouvir.\n\n"
            "👉 No geral, como você avalia o suporte e a clareza que recebe da sua gestão direta hoje?"
        )

        salvar_log(user, 1, "INICIO")
        await update.message.reply_text(pergunta)
        return

    etapa = usuarios[user]["etapa"]
    usuarios[user]["respostas"].append(texto)
    salvar_log(user, etapa, texto)

    if etapa == 1:
        usuarios[user]["etapa"] = 2
        await update.message.reply_text(
            "Entendo. 👉 O que você considera que a gestão faz muito bem e deve continuar fazendo?"
        )

    elif etapa == 2:
        usuarios[user]["etapa"] = 3
        await update.message.reply_text(
            "Obrigado por compartilhar. 👉 Qual é o principal ponto de melhoria, algo que a liderança precisa mudar ou dar mais atenção?"
        )

    elif etapa == 3:
        respostas = usuarios[user]["respostas"]
        resumo = gerar_resumo(respostas)

        salvar_log(user, "final", resumo)

        await update.message.reply_text(
            "Obrigado! A entrevista foi concluída.\n\n"
            f"{resumo}\n\n"
            "Pronto! Para que o RH receba sua opinião de forma 100% anônima, por favor, copie o resumo acima e cole neste link: [COLE AQUI O SEU LINK DO GOOGLE FORMS DO PASSO 1]"
        )

        del usuarios[user]

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

print("BOT RODANDO...")
app.run_polling()