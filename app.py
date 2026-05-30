import streamlit as st
import torch
import requests
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# ================================================================
# 1. تحميل النموذج الحسانية (للردود العامة)
# ================================================================
MODEL_ID = "ABMZD/hassaniya-gpt2-model"

@st.cache_resource
def load_model():
    tokenizer = GPT2Tokenizer.from_pretrained(MODEL_ID)
    model = GPT2LMHeadModel.from_pretrained(MODEL_ID)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return tokenizer, model, device

tokenizer, model, device = load_model()

def generate_hassaniya_response(prompt):
    """توليد رد من النموذج الحسانية"""
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        inputs,
        max_length=100,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.replace(prompt, "").strip()

# ================================================================
# 2. أدوات الـ Agent (للطلبات المحددة)
# ================================================================
def get_weather(city="Nouakchott"):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_resp = requests.get(geo_url, timeout=10)
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            return None
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = requests.get(weather_url, timeout=10)
        temp = weather_resp.json()["current_weather"]["temperature"]
        return f"الجو في {city}: {temp}°C"
    except:
        return None

def get_prayer_times(city="Nouakchott"):
    url = "https://api.aladhan.com/v1/timingsByCity"
    params = {"city": city, "country": "Mauritania", "method": 3}
    try:
        response = requests.get(url, params=params, timeout=10)
        timings = response.json()["data"]["timings"]
        return f"الفجر: {timings['Fajr']}, الظهر: {timings['Dhuhr']}, العصر: {timings['Asr']}, المغرب: {timings['Maghrib']}, العشاء: {timings['Isha']}"
    except:
        return None

# ================================================================
# 3. الـ Agent الرئيسي
# ================================================================
def process_query(user_input):
    user_input_lower = user_input.lower()
    
    # حالة 1: طلب أدوات خارجية (API)
    if "طقس" in user_input_lower or "حر" in user_input_lower:
        result = get_weather()
        if result:
            return {
                "response": f"بسم الله. {result} الحمد لله.",
                "action": "WEATHER_API",
                "sources": ["Open-Meteo API"],
                "confidence": "haute"
            }
    
    if "صلاة" in user_input_lower or "الفجر" in user_input_lower:
        result = get_prayer_times()
        if result:
            return {
                "response": f"الله أكبر. {result}",
                "action": "PRAYER_API",
                "sources": ["AlAdhan API"],
                "confidence": "haute"
            }
    
    # حالة 2: نموذج الحسانية (للردود العامة)
    response = generate_hassaniya_response(user_input)
    return {
        "response": response,
        "action": "HASSANIYA_MODEL",
        "sources": ["Hassaniya GPT-2 Model (TP2)"],
        "confidence": "moyenne"
    }

# ================================================================
# 4. واجهة Streamlit
# ================================================================
st.set_page_config(page_title="الشيخ محمد - Agent Hassaniya", page_icon="🕌")

st.title("🕌 الشيخ محمد - مساعد الحسانية الذكي")
st.caption("السلام عليكم. اسألني عن الطقس، الصلاة، أو أي شيء بالحسانية")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("شنو سؤالك؟..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("الشيخ محمد يفكر..."):
            result = process_query(prompt)
            st.write(result["response"])
            with st.expander("🔍 تفاصيل"):
                st.json({
                    "action": result["action"],
                    "sources": result["sources"],
                    "confidence": result["confidence"]
                })
    
    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
