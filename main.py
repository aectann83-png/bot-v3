import telebot, io, re, os, threading, time
from PIL import Image
from flask import Flask
from gradio_client import Client

BOT_TOKEN = os.getenv("BOT_TOKEN", "8966447867:AAFXMt4kO4nwrUSzRccrepQjGJG4f47Z_sQ")
HF_TOKEN = os.getenv("HF_TOKEN", "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")

bot = telebot.TeleBot(BOT_TOKEN)
print("=== BOT V3 SMART ETERNAL ===")

app = Flask(__name__)
@app.route("/")
def health():
    return "Bot V3 is alive!", 200

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

@bot.message_handler(content_types=['photo'])
def handle(m):
    cap = m.caption if m.caption else "cinematic motion"
    s = re.search(r'(\d+)\s*сек', cap)
    sec = int(s.group(1)) if s else 3
    sec = max(1, min(sec, 5))
    prompt = re.sub(r'\d+\s*сек,?', '', cap).strip()
    if not prompt:
        prompt = "cinematic camera movement, slow dolly, high detail, 4k"
    final_prompt = f"{prompt}, cinematic lighting, smooth motion, high quality, film grain, 24fps"

    bot.reply_to(m, f"🎬 Принял V3! Делаю {sec} сек...\n{final_prompt}\nПодожди 60-90 сек, делаю киношно.")

    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        img_bytes = bot.download_file(file_info.file_path)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        gradio = Client("Wan-AI/Wan2.1-I2V-14B-480P", hf_token=HF_TOKEN)
        result = gradio.predict(
            img,
            final_prompt,
            sec,
            api_name="/predict"
        )
        print(f"Video generated: {result}")
        with open(result, "rb") as v:
            bot.send_video(m.chat.id, v, caption=f"✅ Готово V3 {sec} сек\n{prompt}")
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(m, f"⚠️ Ошибка V3: {e}\nПопробуй еще раз через минуту, модель просыпается.")
        time.sleep(2)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🎬 Привет! Я BOT V3 SMART ETERNAL\n\nКидай фото с подписью типа:\n`3 сек, идет по темному коридору, хоррор`\n`2 сек, крупный план, испуг`\n\nДелаю 1-5 сек, киношное качество!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Flask started, starting bot polling...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error: {e}, restarting in 5 sec")
            time.sleep(5)
