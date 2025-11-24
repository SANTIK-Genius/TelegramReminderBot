import telebot
import json
import datetime
import threading
import time

TOKEN = "TOKEN"  # Your Token Here
bot = telebot.TeleBot(TOKEN)

REMINDERS_FILE = "reminders.json"

def load_reminders():
    try:
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_reminders(data):
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def scheduler():
    while True:
        reminders = load_reminders()
        now_dt = datetime.datetime.now()
        now_str = now_dt.strftime("%H:%M")
        changed = False

        for r in reminders:
            if not r["sent"]:
                r_time_dt = datetime.datetime.strptime(r["time"], "%H:%M")
                r_time_dt = r_time_dt.replace(year=now_dt.year, month=now_dt.month, day=now_dt.day)
                if now_dt >= r_time_dt:
                    try:
                        bot.send_message(r["chat_id"], f"🔔 Напоминание: {r['text']}")
                        r["sent"] = True
                        changed = True
                        print(f"Отправлено напоминание: {r['text']}")
                    except Exception as e:
                        print("Ошибка отправки:", e)

        if changed:
            save_reminders(reminders)

        time.sleep(15)

@bot.message_handler(commands=["add"])
def add_reminder(message):
    try:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            raise ValueError
        reminder_time = parts[1]
        text = parts[2]

        datetime.datetime.strptime(reminder_time, "%H:%M")

        data = load_reminders()
        data.append({
            "chat_id": message.chat.id,
            "time": reminder_time,
            "text": text,
            "sent": False
        })
        save_reminders(data)
        bot.reply_to(message, "✅ Напоминание добавлено!")
    except:
        bot.reply_to(message, "Используй: /add HH:MM Текст напоминания")

@bot.message_handler(commands=["list"])
def list_reminders(message):
    data = load_reminders()
    user_reminders = [r for r in data if r["chat_id"] == message.chat.id]
    if not user_reminders:
        bot.reply_to(message, "Нет напоминаний.")
        return
    text = "\n".join([f"{idx+1}) {r['time']} — {r['text']}" for idx, r in enumerate(user_reminders)])
    bot.reply_to(message, text)

@bot.message_handler(commands=["delete"])
def delete_reminder(message):
    try:
        idx = int(message.text.split()[1]) - 1
        data = load_reminders()
        user_reminders = [r for r in data if r["chat_id"] == message.chat.id]
        reminder_to_delete = user_reminders[idx]

        data.remove(reminder_to_delete)
        save_reminders(data)
        bot.reply_to(message, "✅ Напоминание удалено!")
    except:
        bot.reply_to(message, "Используй: /delete номер_напоминания")

threading.Thread(target=scheduler, daemon=True).start()
print("Бот запущен...")
bot.infinity_polling()
