import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import anthropic

# ========================================
# KONFIGURACJA STRONY
# ========================================

st.set_page_config(
    page_title="Portal Zamówień Oprogramowania",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================================
# CUSTOM CSS - Estetyka inspirowana portalami wewnętrznymi firm
# ========================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    * {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Główny kontener */
    .main-container {
        background: white;
        border-radius: 16px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Nagłówek */
    .header {
        text-align: center;
        margin-bottom: 3rem;
        border-bottom: 3px solid #667eea;
        padding-bottom: 2rem;
    }
    
    .header h1 {
        color: #1a202c;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        color: #718096;
        font-size: 1.1rem;
    }
    
    /* Karty oprogramowania */
    .software-card {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .software-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .software-name {
        color: #2d3748;
        font-weight: 600;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }
    
    .software-desc {
        color: #4a5568;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 0.8rem;
    }
    
    .software-group {
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    /* AI Recommendation Box */
    .ai-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    
    .ai-box h3 {
        margin-top: 0;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Kategorie */
    .category-badge {
        background: #edf2f7;
        color: #4a5568;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    /* Przyciski */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Inputy */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Success/Error messages */
    .success-box {
        background: #f0fff4;
        border-left: 4px solid #48bb78;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #fff5f5;
        border-left: 4px solid #f56565;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 2px solid #e2e8f0;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# FUNKCJE POMOCNICZE
# ========================================

def load_catalogue():
    """Wczytuje katalog oprogramowania z pliku JSON"""
    with open('catalogue.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_ai_recommendation(user_need, catalogue):
    """
    Używa Claude API do rekomendacji oprogramowania na podstawie opisu potrzeby użytkownika
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "Błąd: Brak klucza API. Skonfiguruj ANTHROPIC_API_KEY w ustawieniach Streamlit."
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Przygotowanie informacji o katalogu dla AI
        catalogue_text = "\n".join([
            f"- {item['name']}: {item['description']}" 
            for item in catalogue
        ])
        
        prompt = f"""Na podstawie poniższego opisu potrzeby użytkownika, zarekomenduj JEDNO najlepiej pasujące oprogramowanie z dostępnego katalogu.

Opis potrzeby użytkownika:
{user_need}

Dostępne oprogramowanie:
{catalogue_text}

Odpowiedz w formacie JSON:
{{
    "recommended_software": "dokładna nazwa oprogramowania z katalogu",
    "reasoning": "krótkie uzasadnienie (2-3 zdania) po polsku, dlaczego to oprogramowanie jest najlepsze dla tej potrzeby"
}}

WAŻNE: Pole "recommended_software" musi zawierać DOKŁADNIE taką samą nazwę jak w katalogu."""

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parsowanie odpowiedzi
        response_text = message.content[0].text
        
        # Usuwanie potencjalnych znaczników markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        recommendation = json.loads(response_text)
        return recommendation, None
        
    except Exception as e:
        return None, f"Błąd podczas komunikacji z AI: {str(e)}"

def save_order_to_excel(username, email, software_name, user_group):
    """
    Zapisuje zamówienie do pliku Excel (rejestr użytkowników)
    """
    order_data = {
        'Username': username,
        'Email': email,
        'Software': software_name,
        'User Group': user_group,
        'Date Assigned': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    excel_file = 'user_registry.xlsx'
    
    try:
        # Sprawdź czy plik istnieje
        if os.path.exists(excel_file):
            df_existing = pd.read_excel(excel_file)
            df_new = pd.DataFrame([order_data])
            df = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df = pd.DataFrame([order_data])
        
        # Zapisz do pliku
        df.to_excel(excel_file, index=False)
        return True, None
    except Exception as e:
        return False, f"Błąd podczas zapisu do Excel: {str(e)}"

def send_confirmation_email(recipient_email, username, software_name, user_group):
    """
    Wysyła email z potwierdzeniem zamówienia
    """
    # Dane do wysyłki emaila (konfigurowane w Streamlit Secrets)
    sender_email = os.environ.get("GMAIL_ADDRESS")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not sender_email or not sender_password:
        return False, "Błąd: Brak konfiguracji email. Skonfiguruj GMAIL_ADDRESS i GMAIL_APP_PASSWORD."
    
    try:
        # Tworzenie wiadomości
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Potwierdzenie przyznania dostępu: {software_name}"
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Treść emaila
        text = f"""
Witaj {username},

Twoje zamówienie zostało przetworzone pomyślnie!

Szczegóły:
- Oprogramowanie: {software_name}
- Przypisana grupa: {user_group}
- Data przyznania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Dostęp do oprogramowania został aktywowany. Możesz teraz korzystać z przypisanych narzędzi.

Pozdrawiamy,
Zespół IT
        """
        
        html = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: #f7fafc; border-radius: 8px;">
      <h2 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px;">
        ✓ Potwierdzenie przyznania dostępu
      </h2>
      
      <p>Witaj <strong>{username}</strong>,</p>
      
      <p>Twoje zamówienie zostało przetworzone pomyślnie!</p>
      
      <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
        <h3 style="margin-top: 0; color: #2d3748;">Szczegóły zamówienia:</h3>
        <p><strong>Oprogramowanie:</strong> {software_name}</p>
        <p><strong>Przypisana grupa:</strong> <code style="background: #edf2f7; padding: 2px 6px; border-radius: 4px;">{user_group}</code></p>
        <p><strong>Data przyznania:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
      </div>
      
      <p>Dostęp do oprogramowania został aktywowany. Możesz teraz korzystać z przypisanych narzędzi.</p>
      
      <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
      
      <p style="color: #718096; font-size: 0.9em;">
        Pozdrawiamy,<br>
        <strong>Zespół IT</strong>
      </p>
    </div>
  </body>
</html>
        """
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Wysyłka przez Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        return True, None
    except Exception as e:
        return False, f"Błąd podczas wysyłki emaila: {str(e)}"

# ========================================
# GŁÓWNA APLIKACJA
# ========================================

def main():
    # Header
    st.markdown("""
    <div class="main-container">
        <div class="header">
            <h1>💼 Portal Zamówień Oprogramowania</h1>
            <p>Szybkie i automatyczne nadawanie uprawnień z wsparciem AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Wczytanie katalogu
    catalogue = load_catalogue()
    
    # ========================================
    # SEKCJA 1: AI RECOMMENDATION
    # ========================================
    
    st.markdown("""
    <div class="ai-box">
        <h3>🤖 Asystent AI - Znajdź odpowiednie oprogramowanie</h3>
        <p>Opisz czego potrzebujesz, a AI zasugeruje najlepsze narzędzie z naszego katalogu</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_need = st.text_area(
        "Opisz swoją potrzebę:",
        placeholder="np. 'Muszę tworzyć diagramy procesów biznesowych' lub 'Potrzebuję narzędzia do analizy danych sprzedażowych'",
        height=100,
        key="user_need"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        get_recommendation = st.button("✨ Uzyskaj rekomendację AI", key="ai_recommend")
    
    # Przechowywanie rekomendacji w session state
    if 'recommendation' not in st.session_state:
        st.session_state.recommendation = None
    
    if get_recommendation and user_need.strip():
        with st.spinner("🤔 AI analizuje Twoją potrzebę..."):
            recommendation, error = get_ai_recommendation(user_need, catalogue)
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.session_state.recommendation = recommendation
    
    # Wyświetlenie rekomendacji
    if st.session_state.recommendation:
        rec = st.session_state.recommendation
        st.success("✅ AI znalazło dopasowanie!")
        
        # Znajdź pełne informacje o rekomendowanym oprogramowaniu
        recommended_item = next(
            (item for item in catalogue if item['name'] == rec['recommended_software']),
            None
        )
        
        if recommended_item:
            st.markdown(f"""
            <div class="software-card" style="border: 3px solid #48bb78;">
                <div class="category-badge">✨ Rekomendacja AI</div>
                <div class="software-name">{recommended_item['name']}</div>
                <div class="software-desc">{recommended_item['description']}</div>
                <p style="color: #2d3748; margin-top: 1rem;"><strong>Dlaczego to oprogramowanie?</strong><br>
                {rec['reasoning']}</p>
                <span class="software-group">Grupa: {recommended_item['group']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
    
    # ========================================
    # SEKCJA 2: KATALOG OPROGRAMOWANIA
    # ========================================
    
    st.markdown("### 📚 Pełny katalog oprogramowania")
    st.markdown("Możesz też przeglądać i zamówić bezpośrednio z katalogu:")
    
    # Grupowanie po kategoriach
    categories = {}
    for item in catalogue:
        cat = item.get('category', 'Inne')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    # Wyświetlanie katalogu
    for category, items in categories.items():
        st.markdown(f"#### {category}")
        for item in items:
            st.markdown(f"""
            <div class="software-card">
                <div class="software-name">{item['name']}</div>
                <div class="software-desc">{item['description']}</div>
                <span class="software-group">Grupa: {item['group']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ========================================
    # SEKCJA 3: FORMULARZ ZAMÓWIENIA
    # ========================================
    
    st.markdown("### 📝 Złóż zamówienie")
    
    # Wybór oprogramowania
    software_names = [item['name'] for item in catalogue]
    
    # Jeśli jest rekomendacja AI, ustaw ją jako domyślną
    default_index = 0
    if st.session_state.recommendation:
        rec_name = st.session_state.recommendation['recommended_software']
        if rec_name in software_names:
            default_index = software_names.index(rec_name)
    
    selected_software = st.selectbox(
        "Wybierz oprogramowanie:",
        software_names,
        index=default_index,
        key="software_select"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        username = st.text_input(
            "Twój login (username):",
            placeholder="np. jkowalski",
            key="username"
        )
    
    with col2:
        email = st.text_input(
            "Twój adres email:",
            placeholder="np. jan.kowalski@firma.pl",
            key="email"
        )
    
    # Przycisk zamówienia
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        order_button = st.button("🚀 Zamów oprogramowanie", key="order_button", type="primary")
    
    if order_button:
        if not username.strip() or not email.strip():
            st.error("❌ Wypełnij wszystkie pola!")
        else:
            # Znajdź szczegóły wybranego oprogramowania
            selected_item = next(item for item in catalogue if item['name'] == selected_software)
            
            with st.spinner("⏳ Przetwarzanie zamówienia..."):
                # 1. Zapisz do Excel
                success_excel, error_excel = save_order_to_excel(
                    username, email, selected_software, selected_item['group']
                )
                
                if not success_excel:
                    st.error(f"❌ {error_excel}")
                else:
                    # 2. Wyślij email
                    success_email, error_email = send_confirmation_email(
                        email, username, selected_software, selected_item['group']
                    )
                    
                    if not success_email:
                        st.warning(f"⚠️ Zamówienie zapisane, ale wystąpił problem z emailem: {error_email}")
                    else:
                        st.balloons()
                        st.success(f"""
                        ✅ **Zamówienie przetworzone pomyślnie!**
                        
                        - Użytkownik: **{username}**
                        - Email: **{email}**
                        - Oprogramowanie: **{selected_software}**
                        - Przypisana grupa: **{selected_item['group']}**
                        
                        📧 Email z potwierdzeniem został wysłany na adres: **{email}**
                        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
