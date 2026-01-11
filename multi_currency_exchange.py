import streamlit as st
import requests
from datetime import datetime

# --- 1. 設定網頁 ---
st.set_page_config(
    page_title="多國匯率秒算",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ✨ CSS：UI + 參考 Mobile版做法（不改架構，修正錯位/爆版） ---
st.markdown("""
<style>
  /* 版面限制 */
  .block-container{
      max-width: 520px !important;
      padding-left: 0.5rem !important;
      padding-right: 0.5rem !important;
      padding-top: 1rem !important;
      padding-bottom: 1rem !important;
  }
  html { font-size: 16px; }

  /* ✅ 關鍵：flex 子項允許縮（避免內容撐爆造成錯位） */
  * { min-width: 0 !important; }

  /* 關鍵修正：避免欄位爆版/怪異堆疊 */
  div[data-testid="column"] {
      min-width: 0 !important;
      padding: 0 !important;
  }

  /* 稍微拉近欄位間距 */
  div[data-testid="stHorizontalBlock"] {
      gap: 0.4rem !important;
  }

  /* 下拉選單與輸入框 */
  .stSelectbox div[data-baseweb="select"] > div{
      padding: 0.2rem 0.5rem !important;
      min-height: 2.4rem !important;
      display: flex !important;
      align-items: center !important;
  }
  .stNumberInput input{
      padding: 0.2rem 0.5rem !important;
      min-height: 2.4rem !important;
  }
  div[data-testid="stNumberInput"] button{ display: none !important; }
  div[data-testid="InputInstructions"]{ display: none !important; }

  /* 按鈕樣式 */
  div.row-widget.stButton > button {
      padding: 0rem !important;
      width: 100%;
      height: 2.4rem !important;
      line-height: 1 !important;
      border: 1px solid rgba(128, 128, 128, 0.2);
      background-color: transparent;
      display: flex;
      align-items: center;
      justify-content: center;
  }

  /* 記憶卡片區塊 */
  .saved-card {
      background-color: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 0.5rem 0.8rem;
      margin-bottom: 0.5rem;
      border: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      align-items: center;
      justify-content: space-between;
  }
  .saved-info {
      font-size: 0.9rem;
      line-height: 1.3;
  }
  .saved-highlight {
      color: #FFD700;
      font-weight: bold;
  }

  /* 結果文字區：不換行 + 超出省略，避免擠爆 */
  .result-text {
      font-size: 1.2rem;
      font-weight: bold;
      text-align: right;
      color: #4CAF50;
      line-height: 1.1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
  }
  .rate-text-right {
      font-size: 0.8rem;
      color: rgba(255, 255, 255, 0.5);
      text-align: right;
      margin-top: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
  }

  /* ✅ 國旗圖片大小完全不動（依你要求） */
  .flag-img {
      width: 36px;
      height: 27px;
      object-fit: cover;
      border-radius: 4px;
      margin-right: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.3);
      flex: 0 0 auto;
  }

  /* 幣別文字區塊：不換行 + 省略 */
  .currency-name-block {
      line-height: 1.1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      min-width: 0;
  }
  .currency-code {
      font-weight: bold;
      font-size: 1.05rem;
      color: #FFF;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
  }
  .currency-zh {
      font-size: 0.85rem;
      color: rgba(255,255,255,0.6);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
  }

  .info-caption {
      font-size: 0.85rem;
      color: rgba(255, 255, 255, 0.6);
      margin-top: 0.5rem;
      margin-bottom: 0.2rem;
  }

  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  hr { margin: 0.3rem 0 !important; }

  /* ============================
     ✅ 核心：列表每列同一行固定，不上下錯位（參考 Mobile版）
     ============================ */
  .fx-row div[data-testid="stHorizontalBlock"]{
      flex-wrap: nowrap !important;
      gap: 0.45rem !important;
      align-items: center !important;   /* ✅ 垂直置中，解掉上下錯位 */
  }

  /* 第1欄：📌 固定寬 */
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(1){
      flex: 0 0 3.1rem !important;
      width: 3.1rem !important;
      min-width: 3.1rem !important;
  }
  /* 第2欄：⇅ 固定寬 */
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(2){
      flex: 0 0 3.1rem !important;
      width: 3.1rem !important;
      min-width: 3.1rem !important;
  }
  /* 第3欄：幣別資訊（允許縮） */
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(3){
      flex: 1 1 auto !important;
      min-width: 0 !important;
  }
  /* 第4欄：結果（固定比例 + 允許縮，避免擠爆） */
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(4){
      flex: 0 0 42% !important;
      width: 42% !important;
      min-width: 0 !important;
  }

  /* 手機更窄時：間距小一點、字稍縮，不動國旗 */
  @media (max-width: 420px){
      div[data-testid="stHorizontalBlock"] { gap: 0.25rem !important; }
      .fx-row div[data-testid="stHorizontalBlock"]{ gap: 0.28rem !important; }

      div.row-widget.stButton > button { height: 2.2rem !important; }

      .currency-code { font-size: 0.98rem; }
      .currency-zh { font-size: 0.78rem; }
      .result-text { font-size: 1.05rem; }
      .rate-text-right { font-size: 0.72rem; }

      /* 第4欄在超窄螢幕略縮一點，保住同列 */
      .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(4){
          flex: 0 0 40% !important;
          width: 40% !important;
      }
  }
</style>
""", unsafe_allow_html=True)

# ===== 標題 =====
st.markdown("<h2 style='margin:0; margin-bottom: 10px;'>多國匯率秒算</h2>", unsafe_allow_html=True)

# --- 2. 資料處理 ---
@st.cache_data(ttl=300)
def get_rates_data():
    url = "https://open.er-api.com/v6/latest/TWD"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data["rates"], datetime.now().strftime("%H:%M")
    except Exception:
        st.error("⚠️ 網路異常")
        return None, None

rates, update_time = get_rates_data()
if not rates:
    st.stop()

# --- 幣別與代碼設定 ---
DEFAULT_ORDER_TEMPLATE = ["TWD", "USD", "VND", "JPY", "EUR", "CNY", "KRW", "HKD", "AUD", "GBP"]

currency_names = {
    "TWD": "新台幣", "USD": "美金", "VND": "越盾", "JPY": "日圓", "EUR": "歐元",
    "CNY": "人民幣", "KRW": "韓元", "HKD": "港幣", "AUD": "澳幣", "GBP": "英鎊"
}

currency_flag_codes = {
    "TWD": "tw", "USD": "us", "VND": "vn", "JPY": "jp", "EUR": "eu",
    "CNY": "cn", "KRW": "kr", "HKD": "hk", "AUD": "au", "GBP": "gb"
}

currency_emojis = {
    "TWD": "🇹🇼", "USD": "🇺🇸", "VND": "🇻🇳", "JPY": "🇯🇵", "EUR": "🇪🇺",
    "CNY": "🇨🇳", "KRW": "🇰🇷", "HKD": "🇭🇰", "AUD": "🇦🇺", "GBP": "🇬🇧"
}

def format_currency_label(code):
    flag = currency_emojis.get(code, "🌐")
    return f"{flag} {code} {currency_names.get(code, '')}"

# --- 3. Session State ---
if 'base_currency' not in st.session_state:
    st.session_state['base_currency'] = "TWD"
if 'input_amount' not in st.session_state:
    st.session_state['input_amount'] = 1000.0
if 'display_order' not in st.session_state:
    current_base = st.session_state['base_currency']
    st.session_state['display_order'] = [x for x in DEFAULT_ORDER_TEMPLATE if x != current_base]
if 'saved_items' not in st.session_state:
    st.session_state['saved_items'] = []

# --- 邏輯函數 ---
def swap_currency_btn_click(target_curr):
    old_base = st.session_state['base_currency']
    current_list = st.session_state['display_order']
    if target_curr in current_list:
        idx = current_list.index(target_curr)
        current_list[idx] = old_base
    st.session_state['display_order'] = current_list
    st.session_state['base_currency'] = target_curr

def on_dropdown_change():
    new_base = st.session_state['base_currency']
    new_list = [x for x in DEFAULT_ORDER_TEMPLATE if x != new_base]
    st.session_state['display_order'] = new_list

def save_currency_direct(target_curr, current_rate):
    if len(st.session_state['saved_items']) >= 3:
        st.toast("⚠️ 最多記憶三組，請先刪除舊紀錄")
        return

    base_amt = st.session_state['input_amount']
    target_amt = base_amt * current_rate
    base = st.session_state['base_currency']

    new_item = {
        "base": base,
        "base_amt": base_amt,
        "target": target_curr,
        "target_amt": target_amt,
        "rate": current_rate
    }
    st.session_state['saved_items'].append(new_item)

def delete_saved_item(index):
    if 0 <= index < len(st.session_state['saved_items']):
        st.session_state['saved_items'].pop(index)

# --- 4. 主 UI：持有貨幣區塊 ---
st.caption(f"最後更新: {update_time}")

with st.container(border=True):
    st.caption("💰 目前持有 (Source)")

    col_sel, col_num = st.columns([4, 6], vertical_alignment="center")
    with col_sel:
        all_options = [c for c in DEFAULT_ORDER_TEMPLATE if c in rates]
        st.selectbox(
            "幣別",
            options=all_options,
            key="base_currency",
            format_func=format_currency_label,
            on_change=on_dropdown_change,
            label_visibility="collapsed"
        )
    with col_num:
        st.number_input(
            "金額",
            min_value=0.0,
            format="%.2f",
            key="input_amount",
            label_visibility="collapsed"
        )

    st.markdown(
        '<div class="info-caption">記憶功能說明: 點選貨幣左方📌訂選後進行記憶，最多記憶三組</div>',
        unsafe_allow_html=True
    )

# --- 5. 中間：已記憶列表區 ---
if st.session_state['saved_items']:
    st.markdown("---")
    st.caption("📌 記憶清單")

    for idx, item in enumerate(st.session_state['saved_items']):
        b_fmt = "{:,.2f}".format(item['base_amt'])
        if item['base_amt'] >= 10000 and item['base_amt'] % 1 == 0:
            b_fmt = "{:,.0f}".format(item['base_amt'])

        t_fmt = "{:,.2f}".format(item['target_amt'])
        if item['target'] in ["VND", "JPY", "KRW"] or item['target_amt'] >= 10000:
            t_fmt = "{:,.0f}".format(item['target_amt'])

        c_card, c_del = st.columns([8.5, 1.5], vertical_alignment="center")

        with c_card:
            flag_url = f"https://flagcdn.com/w40/{currency_flag_codes.get(item['target'], 'un')}.png"
            st.markdown(f"""
            <div class="saved-card">
                <div class="saved-info">
                    <span style="opacity:0.7">{item['base']} {b_fmt}</span> 
                    <span style="margin:0 4px">➝</span> 
                    <img src="{flag_url}" style="width:20px;height:15px;vertical-align:middle;margin-right:4px;">
                    <span class="saved-highlight">{item['target']} {t_fmt}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c_del:
            st.button("🗑️", key=f"del_saved_{idx}", on_click=delete_saved_item, args=(idx,))

# --- 6. 下方列表 UI（保留原本同列四欄，只修排版） ---
st.markdown("---")
st.caption("🌍 即時換算 (Target)")

base_curr = st.session_state['base_currency']
base_amount = st.session_state['input_amount']
display_list = st.session_state['display_order']
base_rate_to_twd = rates.get(base_curr, 1)

for target_curr in display_list:
    if target_curr not in rates:
        continue

    target_rate_to_twd = rates.get(target_curr, 1)
    cross_rate = target_rate_to_twd / base_rate_to_twd
    converted_amount = base_amount * cross_rate

    # ✅ 用 wrapper 套用 Mobile版的固定欄寬/nowrap/對齊策略
    st.markdown('<div class="fx-row">', unsafe_allow_html=True)

    c_pin, c_swap, c_info, c_res = st.columns([1, 1, 4, 4], vertical_alignment="center")

    # 1) 訂選按鈕
    with c_pin:
        st.button(
            "📌",
            key=f"pin_{target_curr}",
            on_click=save_currency_direct,
            args=(target_curr, cross_rate),
            help="訂選"
        )

    # 2) 交換按鈕
    with c_swap:
        st.button(
            "⇅",
            key=f"swap_{target_curr}",
            on_click=swap_currency_btn_click,
            args=(target_curr,),
            help="交換"
        )

    # 3) 幣別資訊
    with c_info:
        flag_code = currency_flag_codes.get(target_curr, "un")
        flag_url = f"https://flagcdn.com/w80/{flag_code}.png"
        c_name = currency_names.get(target_curr, target_curr)

        st.markdown(f"""
        <div style="display:flex; align-items:center; min-width:0;">
            <img src="{flag_url}" class="flag-img" alt="{target_curr}">
            <div class="currency-name-block">
                <div class="currency-code">{target_curr}</div>
                <div class="currency-zh">{c_name}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4) 結果區（同列，靠右，不上下錯位）
    with c_res:
        fmt_str = "{:,.2f}" if converted_amount < 10000 else "{:,.1f}"
        if target_curr in ["VND", "KRW", "JPY"]:
            fmt_str = "{:,.0f}"
        val_str = fmt_str.format(converted_amount)

        st.markdown(f"""
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:flex-end; height:100%; min-width:0;">
            <div class="result-text">{val_str}</div>
            <div class="rate-text-right">匯率: {cross_rate:,.4f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin: 0.35rem 0; opacity: 0.12;'>", unsafe_allow_html=True)
