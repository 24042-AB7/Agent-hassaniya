import streamlit as st
import requests
from datetime import datetime

# ================================================================
# 1. إعدادات الصفحة
# ================================================================
st.set_page_config(
    page_title="الشيخ محمد - Agent Hassaniya",
    page_icon="🕌",
    layout="centered"
)

st.markdown("""
    <style>
    .main { background-color: #f5f0e8; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ================================================================
# 2. أدوات الـ Agent (نفس أدوات Exercice 2-3)
# ================================================================
def get_weather(city="Nouakchott"):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_resp = requests.get(geo_url, timeout=10)
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            return f"ما لقيتش مدينة {city}"
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = requests.get(weather_url, timeout=10)
        temp = weather_resp.json()["current_weather"]["temperature"]
        return f"الجو في {city}: {temp}°C"
    except:
        return "عذراً، ما قدرتش أجيب المعلومة"

def get_prayer_times(city="Nouakchott", country="Mauritania"):
    url = "https://api.aladhan.com/v1/timingsByCity"
    params = {"city": city, "country": country, "method": 3}
    try:
        response = requests.get(url, params=params, timeout=10)
        timings = response.json()["data"]["timings"]
        return f"الفجر: {timings['Fajr']}, الظهر: {timings['Dhuhr']}, العصر: {timings['Asr']}, المغرب: {timings['Maghrib']}, العشاء: {timings['Isha']}"
    except:
        return "عذراً، ما قدرتش أجيب أوقات الصلاة"

def get_proverb(topic=""):
    proverbs = {
        "الصبر": "الصبر مفتاح الفرج - معناه: بعد العسر يسر",
        "العلم": "العلم نور والجهل ظلام",
        "default": "العقل زينة الإنسان"
    }
    return proverbs.get(topic, proverbs["default"])

# ================================================================
# 3. معالجة السؤال (نفس Agent Exercice 3)
# ================================================================
def process_with_agent(user_input, thread_id):
    user_input_lower = user_input.lower()
    
    # الحصول على تفضيلات المستخدم من الذاكرة
    preferences = st.session_state.get("preferences", {})
    
    # تحديد الأداة المناسبة
    if "طقس" in user_input_lower or "حر" in user_input_lower:
        result = get_weather()
        return {
            "response": f"بسم الله. {result} الحمد لله.",
            "action": "WEATHER_API",
            "sources": ["Open-Meteo API"],
            "confidence": "haute"
        }
    elif "صلاة" in user_input_lower or "الفجر" in user_input_lower:
        result = get_prayer_times()
        return {
            "response": f"الله أكبر. {result}",
            "action": "PRAYER_API",
            "sources": ["AlAdhan API"],
            "confidence": "haute"
        }
    elif "مثل" in user_input_lower or "حكمة" in user_input_lower:
        result = get_proverb("الصبر")
        return {
            "response": f"المثل الحساني: {result}\nوالله أعلم.",
            "action": "PROVERB_RAG",
            "sources": ["Dataset: amthal-hassaniya"],
            "confidence": "haute"
        }
    elif "سوق" in user_input_lower and not preferences.get("aime_chaleur", True):
        return {
            "response": "نظراً لأنك لا تحب الحر، أنصحك تروح للسوق في الصباح الباكر.",
            "action": "MEMORY_ADAPTED",
            "sources": ["Mémoire épisodique"],
            "confidence": "haute"
        }
    elif "السلام" in user_input_lower:
        return {
            "response": "وعليكم السلام ورحمة الله. كيف يمكنني مساعدتك يا ولدي؟",
            "action": "GREETING",
            "sources": ["Personnage"],
            "confidence": "haute"
        }
    else:
        return {
            "response": "الحمد لله على كل حال. والله أعلم يا ولدي.",
            "action": "DIRECT",
            "sources": ["Connaissances du cheikh"],
            "confidence": "moyenne"
        }

# ================================================================
# 4. واجهة المستخدم
# ================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3069/3069171.png", width=100)
    st.title("🕌 الشيخ محمد")
    st.info("""
    **الشخصية:** شيخ محظرة تقليدية
    **اللغة:** الحسانية
    **الأدوات:** الطقس، الصلاة، الأمثال
    """)
    st.divider()
    st.write("📊 **هيكل الإجابة:**")
    st.caption("- response: الرد بالحسانية")
    st.caption("- action: الأداة المستخدمة")
    st.caption("- sources: المصادر")
    st.caption("- confidence: مستوى الثقة")
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.session_state.preferences = {}
        st.rerun()

st.title("🕌 الشيخ محمد - Agent Hassaniya")
st.caption("السلام عليكم. اسألني عن الطقس، الصلاة، أو الأمثال...")

# تهيئة الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preferences" not in st.session_state:
    st.session_state.preferences = {}
if "thread_id" not in st.session_state:
    import random
    st.session_state.thread_id = f"user_{random.randint(1, 10000)}"

# عرض المحادثة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "metadata" in msg:
            with st.expander("🔍 تفاصيل"):
                st.json(msg["metadata"])

# إدخال المستخدم
if prompt := st.chat_input("شنو سؤالك يا ولدي؟..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("الشيخ محمد يفكر..."):
            result = process_with_agent(prompt, st.session_state.thread_id)
            st.write(result["response"])
            
            # عرض التفاصيل المطلوبة في Exercice 8
            with st.expander("🔍 تفاصيل الإجابة"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🎯 Action", result["action"])
                    st.metric("📊 Confiance", result["confidence"])
                with col2:
                    st.write("**📚 Sources:**")
                    for s in result["sources"]:
                        st.write(f"- {s}")
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "metadata": {
            "action": result["action"],
            "sources": result["sources"],
            "confidence": result["confidence"]
        }
    })

st.markdown("---")
st.markdown("<center style='color: #8b5a2b;'>🤖 Agent LangChain | 🕌 Cheikh Muhammad</center>", unsafe_allow_html=True)
