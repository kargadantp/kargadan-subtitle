import os
import whisper
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from deep_translator import GoogleTranslator  # ✅ کتابخانه ترجمه

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📌 مدل Whisper را قبل از دریافت اولین درخواست لود می‌کنیم
model = whisper.load_model("large")  # 🔹 دقت بالا در تشخیص و ترجمه

def convert_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def translate_text(text, src_lang):
    """ 🔹 ترجمه متن از زبان اصلی به فارسی (در صورت نیاز) """
    if src_lang != "fa":  # ✅ اگر زبان فارسی نیست، ترجمه می‌شود
        translated_text = GoogleTranslator(source="auto", target="fa").translate(text)
        return translated_text
    return text  # ✅ اگر فارسی بود، نیازی به ترجمه نیست

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "فایلی آپلود نشده است."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "نام فایل معتبر نیست."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # ✅ مرحله 1: تشخیص زبان
        result = model.transcribe(file_path, task="transcribe")
        detected_language = result["language"]

        # ✅ مرحله 2: تبدیل گفتار به متن بدون ترجمه
        transcript_result = model.transcribe(file_path, language=detected_language)

        srt_filename = os.path.splitext(file.filename)[0] + ".srt"
        srt_path = os.path.join(UPLOAD_FOLDER, srt_filename)

        # ✅ مرحله 3: پردازش و ذخیره زیرنویس (با ترجمه در صورت نیاز)
        with open(srt_path, "w", encoding="utf-8") as f:
            for seg in transcript_result["segments"]:
                start = convert_time(seg["start"])
                end = convert_time(seg["end"])
                original_text = seg["text"].strip()
                
                # 🔹 ترجمه فقط اگر زبان فارسی نباشد
                translated_text = translate_text(original_text, detected_language)

                f.write(f"{seg['id']}\n{start} --> {end}\n{translated_text}\n\n")

        return jsonify({
            "message": "زیرنویس فارسی ساخته شد",
            "srt_url": f"http://127.0.0.1:5000/uploads/{srt_filename}"
        })

    except Exception as e:
        return jsonify({"error": f"خطا در پردازش فایل: {str(e)}"}), 500

@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
