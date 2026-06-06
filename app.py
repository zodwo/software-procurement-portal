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
    * { font-family: 'IBM Plex Sans', sans-serif !important; }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(102,126,234,0.4) !important;
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
    order_data = {
        'Username': username,
        'Email': email,
        'Software': software_name,
        'User Group': user_group,
        'Date Assigned': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
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

    # ── HEADER ──────────────────────────────────────────────
    st.title("💼 Portal Zamówień Oprogramowania")
    st.caption("Szybkie i automatyczne nadawanie uprawnień z wsparciem AI")
    st.divider()

    left_col, right_col = st.columns([2, 1], gap="large")

    # ── LEFT: AI + CATALOGUE ────────────────────────────────
    with left_col:

        # AI box
        with st.container(border=True):
            st.subheader("🤖 Asystent AI — Znajdź odpowiednie oprogramowanie")
            st.caption("Opisz czego potrzebujesz, a AI zasugeruje najlepsze narzędzie z katalogu")

            user_need = st.text_area(
                "Opisz swoją potrzebę:",
                placeholder="np. 'Muszę tworzyć diagramy procesów' lub 'Potrzebuję narzędzia do analizy danych'",
                height=80,
                key="user_need",
                label_visibility="collapsed"
            )
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

        st.divider()
        st.subheader("📚 Katalog oprogramowania")
        st.caption("Kliknij **Wybierz** przy oprogramowaniu, aby je dodać do zamówienia")

        # Group by category
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
                is_recommended = (
                    st.session_state.recommendation and
                    st.session_state.recommendation['recommended_software'] == item['name']
                )

                # Pick container color via border
                with st.container(border=True):
                    name_col, btn_col = st.columns([4, 1])
                    with name_col:
                        # Build label with badges
                        badges = ""
                        if is_recommended:
                            badges += "✨ **AI** &nbsp;"
                        if is_selected:
                            badges += "✔ **Wybrane**"
                        if badges:
                            st.markdown(badges, unsafe_allow_html=True)

                        st.markdown(f"**{item['name']}**")
                        st.caption(item['description'])
                        st.code(item['group'], language=None)

                    with btn_col:
                        st.write("")  # spacing
                        st.write("")  # spacing
                        label = "✔ Wybrane" if is_selected else "➕ Wybierz"
                        if st.button(label, key=f"sel_{item['name']}"):
                            st.session_state.selected_software = item['name']
                            st.rerun()

    # ── RIGHT: ORDER PANEL ──────────────────────────────────
    with right_col:
        with st.container(border=True):
            st.subheader("🛒 Twoje zamówienie")

            if st.session_state.selected_software:
                selected_item = next(
                    (i for i in catalogue if i['name'] == st.session_state.selected_software), None
                )
                if selected_item:
                    st.success(f"✔ **{selected_item['name']}**")
                    st.code(selected_item['group'], language=None)
            else:
                st.info("👈 Wybierz oprogramowanie z katalogu lub skorzystaj z rekomendacji AI")

            st.divider()

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
                        ok_xl, err_xl = save_order_to_excel(
                            username, email, st.session_state.selected_software, sel['group']
                        )
                        if not ok_xl:
                            st.error(f"❌ {err_xl}")
                        else:
                            ok_mail, err_mail = send_confirmation_email(
                                email, username, st.session_state.selected_software, sel['group']
                            )
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

if __name__ == "__main__":
    main()
