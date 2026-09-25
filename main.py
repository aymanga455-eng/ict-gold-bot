import time
import pandas as pd
import requests
import yfinance as yf

# ==========================================
# 1. إعدادات Telegram والتداول
# ==========================================
TELEGRAM_BOT_TOKEN = "8639853527:AAGFt_Y4xYrlYl3ZHlkTAkpclmF96XvMt8w"
TELEGRAM_CHAT_ID = "7445309212"

# الزوج المراد تحليله والإطار الزمني
SYMBOL = "GC=F"       # الذهب
TIMEFRAME = "15m"    # إطار 15 دقيقة


# ==========================================
# 2. دالة إرسال الرسائل لـ Telegram
# ==========================================
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ تم إرسال التنبيه إلى Telegram بنجاح.")
        else:
            print(f"❌ خطأ في الإرسال: {response.text}")
    except Exception as e:
        print(f"❌ استثناء أثناء الإرسال: {e}")


# ==========================================
# 3. دالة جلب البيانات وتحليل شروط ICT
# ==========================================
def analyze_ict_setup():
    print(f"🔍 جاري جلب البيانات وتحليل {SYMBOL} على إطار {TIMEFRAME}...")
    
    # جلب بيانات أحدث الشموع
    df = yf.download(tickers=SYMBOL, period="5d", interval=TIMEFRAME, progress=False)
    
    if df.empty or len(df) < 20:
        print("⚠️ لم يتم جلب بيانات كافية.")
        return

    # تنظيف وتنسيق البيانات
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # تحديد مستويات السيولة
    recent_high = df['High'].iloc[-15:-3].max()
    recent_low = df['Low'].iloc[-15:-3].min()
    
    # الشموع الأخيرة
    c1 = df.iloc[-4]
    c2 = df.iloc[-3]
    c3 = df.iloc[-2]
    
    # --- أ) كشف فرصة شراء (Bullish ICT Setup) ---
    swept_sell_side = (c2['Low'] < recent_low) and (c2['Close'] > recent_low)
    bullish_fvg = c3['Low'] > c1['High']
    
    if swept_sell_side and bullish_fvg:
        fvg_top = round(c3['Low'], 2)
        fvg_bottom = round(c1['High'], 2)
        entry_price = round((fvg_top + fvg_bottom) / 2, 2)
        stop_loss = round(c2['Low'], 2)
        
        msg = (
            f"🚀 *فرصة شراء ICT ممتازة (Bullish Setup)*\n\n"
            f"📌 *الرمز:* `{SYMBOL}`\n"
            f"⏱ *الإطار الزمني:* `{TIMEFRAME}`\n\n"
            f"🔹 *السبب:* سحب سيولة القيعان (Sell-side Sweep) + تشكل Bullish FVG\n"
            f"🎯 *منطقة الفجوة (FVG Zone):* {fvg_bottom} - {fvg_top}\n"
            f"📍 *نقطة الدخول المقترحة (50% FVG):* `{entry_price}`\n"
            f"🛑 *وقف الخسارة (SL):* `{stop_loss}`\n\n"
            f"⚠️ *ملاحظة:* القرار النهائي يعود لك بعد مراجعة الشارت."
        )
        send_telegram_alert(msg)
        return

    # --- ب) كشف فرصة بيع (Bearish ICT Setup) ---
    swept_buy_side = (c2['High'] > recent_high) and (c2['Close'] < recent_high)
    bearish_fvg = c3['High'] < c1['Low']
    
    if swept_buy_side and bearish_fvg:
        fvg_top = round(c1['Low'], 2)
        fvg_bottom = round(c3['High'], 2)
        entry_price = round((fvg_top + fvg_bottom) / 2, 2)
        stop_loss = round(c2['High'], 2)
        
        msg = (
            f"🔻 *فرصة بيع ICT ممتازة (Bearish Setup)*\n\n"
            f"📌 *الرمز:* `{SYMBOL}`\n"
            f"⏱ *الإطار الزمني:* `{TIMEFRAME}`\n\n"
            f"🔹 *السبب:* سحب سيولة القمم (Buy-side Sweep) + تشكل Bearish FVG\n"
            f"🎯 *منطقة الفجوة (FVG Zone):* {fvg_bottom} - {fvg_top}\n"
            f"📍 *نقطة الدخول المقترحة (50% FVG):* `{entry_price}`\n"
            f"🛑 *وقف الخسارة (SL):* `{stop_loss}`\n\n"
            f"⚠️ *ملاحظة:* القرار النهائي يعود لك بعد مراجعة الشارت."
        )
        send_telegram_alert(msg)
        return

    print("ℹ️ لا توجد فرص مكتملة في الوقت الحالي.")

# ==========================================
# 4. تشغيل السكربت بشكل دوري كل 5 دقائق
# ==========================================
if __name__ == "__main__":
    print("🤖 المساعد الذكي لمراقبة ICT شغال الآن...")
    while True:
        try:
            analyze_ict_setup()
            time.sleep(300)
        except Exception as e:
            print(f"❌ حدث خطأ غير متوقع: {e}")
            time.sleep(60)
