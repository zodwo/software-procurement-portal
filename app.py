import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import anthropic

st.set_page_config(
    page_title="Portal Zamówień Oprogramowania",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    * { font-family: 'IBM Plex Sans', sans-serif; }
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; }
    .stApp { background: transparent; }
    .main-container { background: white; border-radius: 16px; padding: 3rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 1400px; margin: 0 auto; }
    .header { text-align: center; margin-bottom: 2rem; border-bottom: 3px solid #667eea; padding-bottom: 2rem; }
    .header h1 { color: #1a202c; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem; }
    .header p { color: #718096; font-size: 1.1rem; }
    .order-panel { background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); border: 2px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; position: sticky; top: 1rem; }
    .software-card { background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); border: 2px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-bottom: 0.75rem; transition: all 0.2s ease; }
    .software-card:hover { box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2); border-color: #667eea; }
    .software-card.selected { border: 3px solid #667eea; background: linear-gradient(135deg, #ebf4ff 0%, #e8eaf6 100%); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25); }
    .software-card.ai-recommended { border: 3px solid #48bb78; background: linear-gradient(135deg, #f0fff4 0%, #e6ffed 100%); }
    .software-name { color: #2d3748; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.4rem; }
    .software-desc { color: #4a5568; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0.6rem; }
    .software-group { background: #667eea; color: white; padding: 0.25rem 0.7rem; border-radius: 6px; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; display: inline-block; }
    .ai-badge { background: #48bb78; color: white; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.78rem; font-weight: 600; display: inline-block; margin-bottom: 0.4rem; margin-right: 0.3rem; }
    .selected-badge { background: #667eea; color: white; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.78rem; font-weight: 600; display: inline-block; margin-bottom: 0.4rem; margin-right: 0.3rem; }
    .ai-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3); }
    .ai-box h3 { margin-top: 0; font-size: 1.3rem; margin-bottom: 0.5rem; }
    .ai-box p { margin: 0; opacity: 0.9; font-size: 0.95rem; }
    .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 0.75rem 2rem; font-weight: 600; font-size: 1rem; transition: all 0.3s ease; width: 100%; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { border-radius: 8px; border: 2px solid #e2e8f0; padding: 0.75rem; font-size: 1rem; }
    hr { border: none; border-top: 2px solid #e2e8f0; margin: 1.5rem 0; }
    .selected-software-display { background: white; border: 2px solid #667eea; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; text-align: center; }
    .selected-software-display .sw-name { font-weight: 700; color: #2d3748; font-size: 1rem; }
    .selected-software-display .sw-group { color: #667eea; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; margin-top: 0.3rem; }
    /* Hide the select buttons - they're functional but invisible, cards act as clickable */
    div[data-testid="stButton"] button[kind="secondary"] { 
        opacity: 0; height: 0; padding: 0; margin: -0.75rem 0 0 0; font-size: 0;
    }
</style>
""", unsafe_allow_html=True)

def load_catalogue():
    with open('catalogue.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_ai_recommendation(user_need, catalogue):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "Błąd: Brak klucza API."
    try:
        client = anthropic.Anthropic(api_key=api_key)
        catalogue_text = "\n".join([f"- {item['name']}: {item['description']}" for item in catalogue])
        prompt = f"""Na podstawie opisu potrzeby użytkownika, zarekomenduj JEDNO najlepiej pasujące oprogramowanie.

Opis potrzeby: {user_need}

Dostępne oprogramowanie:
{catalogue_text}

Odpowiedz TYLKO w formacie JSON:
{{
    "recommended_software": "dokładna nazwa z katalogu",
    "reasoning": "krótkie uzasadnienie po polsku (2-3 zdania)"
}}"""
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = message.content[0].text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        return json.loads(response_text), None
    except Exception as e:
        return None, f"Błąd podczas komunikacji z AI: {str(e)}"

def save_order_to_excel(username, email, software_name, user_group):
    order_data = {'Username': username, 'Email': email, 'Software': software_name, 'User Group': user_group, 'Date Assigned': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    excel_file = 'user_registry.xlsx'
    try:
        if os.path.exists(excel_file):
            df = pd.concat([pd.read_excel(excel_file), pd.DataFrame([order_data])], ignore_index=True)
        else:
            df = pd.DataFrame([order_data])
        df.to_excel(excel_file, index=False)
        return True, None
    except Exception as e:
        return False, f"Błąd zapisu: {str(e)}"

def send_confirmation_email(recipient_email, username, software_name, user_group):
    sender_email = os.environ.get("GMAIL_ADDRESS")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender_email or not sender_password:
        return False, "Brak konfiguracji email."
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Potwierdzenie dostępu: {software_name}"
        message["From"] = sender_email
        message["To"] = recipient_email
        html = f"""<html><body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">
<div style="max-width:600px;margin:0 auto;padding:20px;background:#f7fafc;border-radius:8px;">
<h2 style="color:#667eea;border-bottom:3px solid #667eea;padding-bottom:10px;">✓ Potwierdzenie przyznania dostępu</h2>
<p>Witaj <strong>{username}</strong>,</p>
<p>Twoje zamówienie zostało przetworzone pomyślnie!</p>
<div style="background:white;padding:20px;border-radius:8px;margin:20px 0;border-left:4px solid #667eea;">
<p><strong>Oprogramowanie:</strong> {software_name}</p>
<p><strong>Przypisana grupa:</strong> <code style="background:#edf2f7;padding:2px 6px;border-radius:4px;">{user_group}</code></p>
<p><strong>Data:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
<p style="color:#718096;font-size:0.9em;">Pozdrawiamy,<br><strong>Zespół IT</strong></p>
</div></body></html>"""
        message.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        return True, None
    except Exception as e:
        return False, f"Błąd emaila: {str(e)}"

def main():
    catalogue = load_catalogue()

    if 'recommendation' not in st.session_state:
        st.session_state.recommendation = None
    if 'selected_software' not in st.session_state:
        st.session_state.selected_software = None

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="header">
        <h1>💼 Portal Zamówień Oprogramowania</h1>
        <p>Szybkie i automatyczne nadawanie uprawnień z wsparciem AI</p>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([2, 1], gap="large")

    with left_col:
        # AI SECTION
        st.markdown("""
        <div class="ai-box">
            <h3>🤖 Asystent AI — Znajdź odpowiednie oprogramowanie</h3>
            <p>Opisz czego potrzebujesz, a AI zasugeruje najlepsze narzędzie z naszego katalogu</p>
        </div>
        """, unsafe_allow_html=True)

        user_need = st.text_area("Opisz swoją potrzebę:", placeholder="np. 'Muszę tworzyć diagramy procesów' lub 'Potrzebuję narzędzia do analizy danych'", height=90, key="user_need")

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            get_rec = st.button("✨ Uzyskaj rekomendację AI", key="ai_recommend")

        if get_rec and user_need.strip():
            with st.spinner("🤔 AI analizuje Twoją potrzebę..."):
                rec, error = get_ai_recommendation(user_need, catalogue)
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.session_state.recommendation = rec
                    st.session_state.selected_software = rec['recommended_software']
                    st.rerun()

        if st.session_state.recommendation:
            rec = st.session_state.recommendation
            st.info(f"🤖 **Dlaczego {rec['recommended_software']}?** {rec['reasoning']}")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 📚 Katalog oprogramowania")
        st.markdown("Kliknij **Wybierz** przy oprogramowaniu, aby je dodać do zamówienia:")

        categories = {}
        for item in catalogue:
            cat = item.get('category', 'Inne')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        for category, items in categories.items():
            st.markdown(f"**{category}**")
            for item in items:
                is_selected = st.session_state.selected_software == item['name']
                is_recommended = (st.session_state.recommendation and st.session_state.recommendation['recommended_software'] == item['name'])

                badges = ""
                if is_recommended:
                    badges += '<span class="ai-badge">✨ AI</span>'
                if is_selected:
                    badges += '<span class="selected-badge">✔ Wybrane</span>'

                card_class = "software-card" + (" selected" if is_selected else " ai-recommended" if is_recommended else "")

                st.markdown(f"""
                <div class="{card_class}">
                    {badges}
                    <div class="software-name">{item['name']}</div>
                    <div class="software-desc">{item['description']}</div>
                    <span class="software-group">Grupa: {item['group']}</span>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"➕ Wybierz", key=f"sel_{item['name']}"):
                    st.session_state.selected_software = item['name']
                    st.rerun()

    with right_col:
        st.markdown('<div class="order-panel">', unsafe_allow_html=True)
        st.markdown("### 🛒 Twoje zamówienie")

        if st.session_state.selected_software:
            selected_item = next((i for i in catalogue if i['name'] == st.session_state.selected_software), None)
            if selected_item:
                st.markdown(f"""
                <div class="selected-software-display">
                    <div class="sw-name">✔ {selected_item['name']}</div>
                    <div class="sw-group">{selected_item['group']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 Wybierz oprogramowanie z katalogu lub skorzystaj z rekomendacji AI")

        st.markdown("<hr>", unsafe_allow_html=True)

        username = st.text_input("Login (username):", placeholder="np. jkowalski", key="username")
        email = st.text_input("Adres email:", placeholder="np. jan@firma.pl", key="email")

        order_button = st.button("🚀 Zamów oprogramowanie", key="order_button")

        if order_button:
            if not st.session_state.selected_software:
                st.error("❌ Wybierz oprogramowanie!")
            elif not username.strip() or not email.strip():
                st.error("❌ Wypełnij login i email!")
            else:
                sel = next(i for i in catalogue if i['name'] == st.session_state.selected_software)
                with st.spinner("⏳ Przetwarzanie..."):
                    ok_xl, err_xl = save_order_to_excel(username, email, st.session_state.selected_software, sel['group'])
                    if not ok_xl:
                        st.error(f"❌ {err_xl}")
                    else:
                        ok_mail, err_mail = send_confirmation_email(email, username, st.session_state.selected_software, sel['group'])
                        if not ok_mail:
                            st.warning(f"⚠️ Zapisano, ale problem z emailem: {err_mail}")
                        else:
                            st.balloons()
                            st.success(f"""
                            ✅ **Gotowe!**

                            **{username}** otrzymał dostęp do:
                            **{st.session_state.selected_software}**

                            Grupa: `{sel['group']}`

                            📧 Potwierdzenie wysłano na **{email}**
                            """)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
