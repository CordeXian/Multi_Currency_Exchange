import streamlit as st
import requests
from datetime import datetime

# --- Page config ---
st.set_page_config(
    page_title="多國匯率秒算",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS ---
st.markdown("""
<style>
  .block-container{
      max-width: 520px !important;
      padding: 0.75rem !important;
  }

  html { font-size: 16px; }
  * { min-width: 0 !important; }

  /* =====================
     Source 區塊（50 / 50，不准縮寫）
     ===================== */
  .source-row div[data-testid="stHorizontalBlock"]{
      flex-wrap: nowrap !important;
      gap: 0.6rem !important;
      align-items: center !important;
  }

  .source-row div[data-testid="column"]:nth-child(1),
  .source-row div[data-testid="column"]:nth-child(2){
      flex: 0 0 50% !important;
      width: 50% !important;
      min-width: 50% !important;
  }

  /* 🔥 selectbox 文字不准縮寫 */
  .source-row div[data-baseweb="select"] > div{
      white-space: nowrap !important;
      overflow: visible !important;
      text-overflow: clip !important;
  }

  /* =====================
     Select / Input 外觀
     ===================== */
  .stSelectbox div[data-baseweb="select"] > div,
  .stNumberInput input{
      padding: 0.3rem 0.55rem !important;
      min-height: 2.5rem !important;
      font-size: 1.05rem !important;
      display: flex;
      align-items: center;
  }

  div[data-testid="stNumberInput"] button,
  div[data-testid="InputInstructions"]{
      display: none !important;
  }

  /* =====================
     fx-row：列與列間距縮減 2/3
     ===================== */
  .fx-row{
      margin-top: 0.2rem !important;
      margin-bottom: 0.2rem !important;
  }

  .fx-row div[data-testid="stHorizontalBlock"]{
      flex-wrap: nowrap !important;
      align-items: center !important;
      gap: 0.45rem !important;
  }

  /* 📌 */
  .fx-row div[data-testid="column"]:nth-child(1){
      flex: 0 0 3.2rem !important;
      margin-top: 3px !important;   /* 微下移 */
  }

  /* ⇅ */
  .fx-row div[data-testid="column"]:nth-child(2){
      flex: 0 0 3.2rem !important;
      margin-top: 3px !important;   /* 微下移 */
  }

  /* 幣別 */
  .fx-row div[data-testid="column"]:nth-child(3){
      flex: 1 1 auto !important;
      min-width: 0 !important;
  }

  /* 金額 */
  .fx-row div[data-testid="column"]:nth-child(4){
      flex: 0 0 42% !important;
      min-width: 0 !important;
  }

  /* 按鈕 */
  div.row-widget.stButton > button{
      height: 2.4rem !important;
      padding: 0 !important;
      border: 1px solid rgba(255,255,255,0.2);
      background: transparent;
      display:flex;
      align-items:center;
      justify-content:center;
  }

  /* 國旗 */
  .flag-img{
      width: 36px;
      height: 27px;
      margin-right: 8px;
      border-radius: 4px;
      flex: 0 0 auto;
  }

  /* 幣別文字（+1px） */
  .currency-code{
      font-size: calc(1.05rem + 1px);
      font-weight: bold;
  }
  .currency-zh{
      font-size: calc(0.85rem + 1px);
      opacity: 0.65;
  }

  /* 金額（+1px） */
  .result-text{
      font-size: calc(1.2rem + 1px);
      font-weight: bold;
      color: #4CAF50;
      white-space: nowrap;
  }

  .rate-text{
      font-size: 0.8rem;
      opacity: 0.55;
      white-space: nowrap;
  }

  #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h2>多國匯率秒算</h2>", unsafe_allow_html=True)

# --- Data ---
@st.cache_data(ttl=300)
def get_rates():
    r = requests.get("https://open.er-api.com/v6/latest/TWD", timeout=10).json()
    return r["rates"], datetime.now().strftime("%H:%M")

rates, update_time = get_rates()

# --- Config ---
currency_names = {
    "TWD": "新台幣", "USD": "美金", "VND": "越盾", "JPY": "日圓", "EUR": "歐元",
    "CNY": "人民幣", "KRW": "韓元", "HKD": "港幣", "AUD": "澳幣", "GBP": "英鎊"
}
currency_flags = {
    "TWD": "tw", "USD": "us", "VND": "vn", "JPY": "jp", "EUR": "eu",
    "CNY": "cn", "KRW": "kr", "HKD": "hk", "AUD": "au", "GBP": "gb"
}
DEFAULT_ORDER_TEMPLATE = list(currency_names.keys())

# --- State ---
st.session_state.setdefault("base_currency", "TWD")
st.session_state.setdefault("input_amount", 1000.0)
st.session_state.setdefault("display_order", [x for x in DEFAULT_ORDER_TEMPLATE if x != st.session_state["base_currency"]])
st.session_state.setdefault("saved_items", [])

def on_dropdown_change():
    base = st.session_state["base_currency"]
    st.session_state["display_order"] = [x for x in DEFAULT_ORDER_TEMPLATE if x != base]

def swap_currency_btn_click(target_curr):
    old_base = st.session_state["base_currency"]
    current_list = st.session_state["display_order"]
    if target_curr in current_list:
        idx = current_list.index(target_curr)
        current_list[idx] = old_base
    st.session_state["display_order"] = current_list
    st.session_state["base_currency"] = target_curr

def save_currency_direct(target_curr, current_rate):
    if len(st.session_state["saved_items"]) >= 3:
        st.toast("⚠️ 最多記憶三組，請先刪除舊紀錄")
        return

    base = st.session_state["base_currency"]
    base_amt = st.session_state["input_amount"]
    target_amt = base_amt * current_rate

    st.session_state["saved_items"].append({
        "base": base,
        "base_amt": base_amt,
        "target": target_curr,
        "target_amt": target_amt,
        "rate": current_rate
    })

def delete_saved_item(index):
    if 0 <= index < len(st.session_state["saved_items"]):
        st.session_state["saved_items"].pop(index)

def format_currency_label(code: str) -> str:
    # 用 emoji 國旗，避免 selectbox 內使用外部圖片造成顯示問題
    emoji = {
        "TWD": "🇹🇼", "USD": "🇺🇸", "VND": "🇻🇳", "JPY": "🇯🇵", "EUR": "🇪🇺",
        "CNY": "🇨🇳", "KRW": "🇰🇷", "HKD": "🇭🇰", "AUD": "🇦🇺", "GBP": "🇬🇧"
    }.get(code, "🌐")
    return f"{emoji} {code} {currency_names.get(code, '')}"

# --- Source UI ---
st.caption(f"最後更新: {update_time}")

with st.container(border=True):
    st.caption("💰 目前持有 (Source)")
    st.markdown('<div class="source-row">', unsafe_allow_html=True)

    c1, c2 = st.columns(2, vertical_alignment="center")
    with c1:
        st.selectbox(
            "幣別",
            options=[c for c in DEFAULT_ORDER_TEMPLATE if c in rates],
            key="base_currency",
            format_func=format_currency_label,
            on_change=on_dropdown_change,
            label_visibility="collapsed"
        )
    with c2:
        st.number_input(
            "金額",
            min_value=0.0,
            format="%.2f",
            key="input_amount",
            label_visibility="collapsed"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="opacity:0.65; font-size:0.85rem; margin-top:0.4rem;">'
        '記憶功能說明: 點選貨幣左方📌訂選後進行記憶，最多記憶三組</div>',
        unsafe_allow_html=True
    )

# --- Saved list ---
if st.session_state["saved_items"]:
    st.markdown("---")
    st.caption("📌 記憶清單")

    for idx, item in enumerate(st.session_state["saved_items"]):
        b_fmt = f"{item['base_amt']:,.2f}"
        if item["base_amt"] >= 10000 and item["base_amt"] % 1 == 0:
            b_fmt = f"{item['base_amt']:,.0f}"

        t_fmt = f"{item['target_amt']:,.2f}"
        if item["target"] in ["VND", "JPY", "KRW"] or item["target_amt"] >= 10000:
            t_fmt = f"{item['target_amt']:,.0f}"

        c_card, c_del = st.columns([8.5, 1.5], vertical_alignment="center")
        with c_card:
            flag_code = currency_flags.get(item["target"], "un")
            flag_url = f"https://flagcdn.com/w40/{flag_code}.png"
            st.markdown(f"""
            <div style="
              background: rgba(255,255,255,0.05);
              border: 1px solid rgba(255,255,255,0.1);
              border-radius: 10px;
              padding: 0.55rem 0.8rem;
              display:flex; align-items:center; justify-content:space-between;">
              <div style="opacity:0.8;">
                {item['base']} {b_fmt} ➝
                <img src="{flag_url}" style="width:20px;height:15px;vertical-align:middle;margin:0 4px;">
                <span style="color:#FFD700;font-weight:700;">{item['target']} {t_fmt}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with c_del:
            st.button("🗑️", key=f"del_saved_{idx}", on_click=delete_saved_item, args=(idx,))

# --- Target list ---
st.markdown("---")
st.caption("🌍 即時換算 (Target)")

base = st.session_state["base_currency"]
base_amount = st.session_state["input_amount"]
display_list = st.session_state["display_order"]
base_rate_to_twd = rates.get(base, 1)

for target_curr in display_list:
    if target_curr not in rates:
        continue

    target_rate_to_twd = rates.get(target_curr, 1)
    cross_rate = target_rate_to_twd / base_rate_to_twd
    converted_amount = base_amount * cross_rate

    st.markdown('<div class="fx-row">', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([1, 1, 4, 4], vertical_alignment="center")

    # ✅ 重點：每顆按鈕都加唯一 key（避免 DuplicateElementId）
    with c1:
        st.button(
            "📌",
            key=f"pin_{target_curr}",
            on_click=save_currency_direct,
            args=(target_curr, cross_rate),
            help="訂選"
        )
    with c2:
        st.button(
            "⇅",
            key=f"swap_{target_curr}",
            on_click=swap_currency_btn_click,
            args=(target_curr,),
            help="交換"
        )

    with c3:
        flag_code = currency_flags.get(target_curr, "un")
        flag_url = f"https://flagcdn.com/w80/{flag_code}.png"
        c_name = currency_names.get(target_curr, target_curr)
        st.markdown(f"""
        <div style="display:flex;align-items:center; min-width:0;">
          <img class="flag-img" src="{flag_url}" alt="{target_curr}">
          <div style="min-width:0; overflow:hidden;">
            <div class="currency-code">{target_curr}</div>
            <div class="currency-zh">{c_name}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        fmt = "{:,.2f}" if converted_amount < 10000 else "{:,.1f}"
        if target_curr in ["VND", "JPY", "KRW"]:
            fmt = "{:,.0f}"
        val_str = fmt.format(converted_amount)

        st.markdown(f"""
        <div style="text-align:right; min-width:0;">
          <div class="result-text">{val_str}</div>
          <div class="rate-text">匯率: {cross_rate:,.4f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
