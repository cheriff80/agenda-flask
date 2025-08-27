import json
import os
import schedule
import time
from datetime import datetime, timedelta
import asyncio
from telegram import Bot

# Configuración de Telegram

# "TU_TOKEN" - Buscar BotFather en Telegram -> START -> Escribir /newbot (crea un nuevo bot en Telegram: escribiendo un
# nombre para el bot y un nombre de usuario acabado en _bot) -> Se genera un token que deberás introducir en TU_TOKEN 
TOKEN = "TU_TOKEN" 

# "Id" - Escribe un mensaje a el bot que has creado -> Escribe en el navegador https://api.telegram.org/botTU_TOKEN/getUpdates ->
#  el "Id" que aparece en el chat del JASON  es el Id que debes introducir aquí
CHAT_ID = "Id"
bot = Bot(token=TOKEN)

EVENTOS_FILE = "eventos.json"

def cargar_eventos():
    if not os.path.exists(EVENTOS_FILE):
        return []
    with open(EVENTOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

async def send_telegram_message(texto):
    await bot.send_message(chat_id=CHAT_ID, text=texto)

def check_eventos():
    eventos = cargar_eventos()
    ahora = datetime.now()

    for evento in eventos:
        fecha_evento = datetime.strptime(f"{evento['fecha']} {evento['hora']}", "%Y-%m-%d %H:%M")
        aviso_horas = evento.get("aviso_horas", 1)  # por defecto 1 hora
        aviso_time = fecha_evento - timedelta(hours=aviso_horas)

        if aviso_time.strftime("%Y-%m-%d %H:%M") == ahora.strftime("%Y-%m-%d %H:%M"):
            asyncio.run(send_telegram_message(
                f"📅 Recordatorio: {evento['titulo']} a las {evento['hora']} (Hoy {evento['fecha']})"
            ))

# Revisar cada minuto
schedule.every(1).minutes.do(check_eventos)

print("✅ Notificador de agenda iniciado...")
while True:
    schedule.run_pending()
    time.sleep(1)


