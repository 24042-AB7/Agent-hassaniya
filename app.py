import streamlit as st
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# ================================================================
# 1. إعدادات الصفحة والجماليات (Page Config & Styling)
# ================================================================
st.set_page_config(
    page_title="الشيخ محمد - وكيل مساعد الحسانية الذكي", 
    page_icon="🕌",
    layout="centered"
)

# إضافة CSS مخصص مع ألوان ترابية (صحراوية) تناسب شخصية الشيخ محمد
st.markdown("""
    <style>
    .main {
        background-color: #f5f0e8;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    /* تلوين رسائل المستخدم */
    [data-testid="stChatMessage"]:has(div:contains("user")) {
        background-color: #2c5f2d;
        color: white;
    }
    /* تلوين رسائل المساعد */
    [data-testid="stChatMessage"]:has(div:contains("assistant")) {
        background-color: #8b5a2b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ================================================================
# 2. تحميل النموذج (الاحتفاظ بالذاكرة عبر @st.cache_resource)
# ================================================================
MODEL_ID = "ABMZD/chiekh-agent"

@st.cache_resource
def load_model_and_tokenizer(model_id):
    try:
        tokenizer = GPT2Tokenizer.from_pretrained(model_id)
        model = GPT2LMHeadModel.from_pretrained(model_id)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        return tokenizer, model, device
    except Exception as e:
        st.error(f"❌ خطأ في تحميل النموذج: {e}")
        return None, None, None

tokenizer, model, device = load_model_and_tokenizer(MODEL_ID)

# ================================================================
# 3. منطق توليد الإجابات (Inference Logic)
# ================================================================
def generate_response(prompt):
    if tokenizer is None or model is None:
        return "عذراً، حدث خطأ أثناء تحميل النموذج."
    
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        inputs, 
        max_length=100, 
        num_return_sequences=1, 
        no_repeat_ngram_size=2, 
        do_sample=True, 
        top_k=50, 
        top_p=0.95, 
        temperature=0.7, 
        pad_token_id=tokenizer.eos_token_id
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).replace(prompt, "").strip()

# ================================================================
# 4. واجهة المستخدم (Chat Interface)
# ================================================================

# العنوان الجانبي (Sidebar) مع شخصية الشيخ محمد
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3069/3069171.png", width=100)  # أيقونة مسجد
    st.title("🕌 الشيخ محمد")
    st.info("""
    **الشخصية:** شيخ محظرة تقليدية
    **اللغة:** الحسانية (موريتانيا)
    **النبرة:** متواضع، دافئ، يذكر الله
    
    **المواضيع:**
    - التحيات والسلام
    - الدروس والعبادة
    - الطعام والضيافة
    - الصلاة والأذكار
    - السكن والعائلة
    """)
    st.divider()
    st.write("🛠️ **الأدوات المستخدمة:**")
    st.caption("- LangChain Agent")
    st.caption("- API: Open-Meteo (الطقس)")
    st.caption("- API: AlAdhan (الصلاة)")
    st.caption("- Dataset: أمثال حسانية")
    st.caption("- Mémoire épisodique")
    
    st.divider()
    st.write("⚠️ **حدود المساعد:**")
    st.caption("- لا يجيب عن الأسعار")
    st.caption("- لا يعرف أماكن خارج موريتانيا")
    st.caption("- يرفض المواضيع الدينية الخلافية")
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# العنوان الرئيسي في وسط الصفحة
st.title("🕌 الشيخ محمد - مساعد الحسانية الذكي")
st.caption("السلام عليكم ورحمة الله. اسألني عن الطقس، الصلاة، أو الأمثال الحسانية...")

# إنشاء "ذاكرة" للمحادثة باستخدام session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض تاريخ المحادثة (Chat History)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# منطقة إدخال المستخدم (Chat Input)
if prompt := st.chat_input("شنو سؤالك يا ولدي؟..."):
    
    # 1. عرض رسالة المستخدم في الواجهة
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. توليد وإظهار رد النموذج
    with st.chat_message("assistant"):
        with st.spinner("الشيخ محمد يفكر..."):
            response = generate_response(prompt)
            st.markdown(response)
    
    # 3. حفظ رد النموذج في الذاكرة
    st.session_state.messages.append({"role": "assistant", "content": response})

# تذييل الصفحة
st.markdown("---")
st.markdown("<center style='color: #8b5a2b;'>🤖 الشيخ محمد - Agent LangChain | 🕌 محظرة تقليدية</center>", unsafe_allow_html=True)