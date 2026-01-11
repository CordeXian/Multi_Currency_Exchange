import streamlit as st
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # ✅ 台灣時區

# --- 1. 設定網頁 ---
st.set_page_config(
    page_title="多國匯率計算器",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ✨ CSS：Source 選單加寬 + 金額變窄 + 列間距縮小到約 1/3 ---
st.markdown(r"""
<style>
  /* ===== 全域容器 ===== */
  .block-container{
      max-width: 520px !important;
      padding-left: 0.5rem !important;
      padding-right: 0.5rem !important;
      padding-top: 1rem !important;
      padding-bottom: 1rem !important;
  }
  html { font-size: 16px; }

  /* ✅ flex 佈局允許縮（避免擠爆） */
  * { min-width: 0 !important; }

  /* ===== ✅ 讓 Streamlit 元件之間不要留太多「預設空白」(列間距縮小的關鍵) ===== */
  div[data-testid="stVerticalBlock"] { gap: 0.10rem !important; }
  .element-container { margin-bottom: 0.10rem !important; }
  div[data-testid="stMarkdownContainer"] { margin-bottom: 0.05rem !important; }

  /* Streamlit columns 更乾淨 */
  div[data-testid="column"]{
      padding: 0 !important;
      min-width: 0 !important;
  }

  /* 讓 columns 間距一致 */
  div[data-testid="stHorizontalBlock"]{
      gap: 0.45rem !important;
      align-items: center !important;
  }

  /* ===== ✅ Source：左邊加寬，右邊變窄 ===== */
  .source-row div[data-testid="stHorizontalBlock"]{
      flex-wrap: nowrap !important;
      gap: 0.6rem !important;
      align-items: center !important;
  }

  /* 🔥 selectbox：關閉省略號、允許換行、取消 text-overflow 相關限制 */
  .source-row div[data-baseweb="select"]{
      width: 100% !important;
      max-width: 100% !important;
  }
  .source-row div[data-baseweb="select"] > div{
      white-space: normal !important;
      overflow: visible !important;
      text-overflow: clip !important;
      height: auto !important;
      max-width: none !important;
  }
  .source-row div[data-baseweb="select"] span{
      white-space: normal !important;
      overflow: visible !important;
      text-overflow: clip !important;
  }

  /* selectbox / numberinput 外觀 */
  .stSelectbox div[data-baseweb="select"] > div{
      padding: 0.30rem 0.55rem !important;
      min-height: 2.55rem !important;
      display: flex !important;
      align-items: center !important;
      font-size: 1.05rem !important;
      line-height: 1.2 !important;
  }
  .stNumberInput input{
      padding: 0.30rem 0.55rem !important;
      min-height: 2.55rem !important;
      font-size: 1.05rem !important;
      line-height: 1.2 !important;
  }
  div[data-testid="stNumberInput"] button{ display: none !important; }
  div[data-testid="InputInstructions"]{ display: none !important; }

  /* ===== fx-row：列表同列穩定 + 大按鈕 + 更緊列間距 ===== */
  .fx-row div[data-testid="stHorizontalBlock"]{
      flex-wrap: nowrap !important;
      align-items: center !important;
      gap: 0.45rem !important;
  }

  /* 第1/2欄固定寬（按鈕） */
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(1){
      flex: 0 0 3.2rem !important;
      width: 3.2rem !important;
      min-width: 3.2rem !important;
  }
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(2){
      flex: 0 0 3.2rem !important;
      width: 3.2rem !important;
      min-width: 3.2rem !important;
  }

  /* 第3欄：幣別資訊 */
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(3){
      flex: 1 1 auto !important;
      min-width: 0 !important;
  }
  /* 第4欄：結果 */
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(4){
      flex: 0 0 42% !important;
      width: 42% !important;
      min-width: 0 !important;
  }

  /* ✅ 大顆按鈕 */
  div.row-widget.stButton > button{
      width: 100% !important;
      height: 2.6rem !important;
      padding: 0 !important;
      border: 1px solid rgba(255,255,255,0.22) !important;
      background: transparent !important;
      display:flex !important;
      align-items:center !important;
      justify-content:center !important;
      font-size: 1.15rem !important;
      border-radius: 10px !important;
  }

  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(1) div.row-widget.stButton,
  .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(2) div.row-widget.stButton{
      margin-top: 3px !important;
  }

  /* 國旗 */
  .flag-img{
      width: 36px;
      height: 27px;
      object-fit: cover;
      border-radius: 4px;
      margin-right: 8px;
      flex: 0 0 auto;
  }

  /* 幣別文字 */
  .currency-code{
      font-weight: 700;
      font-size: calc(1.05rem + 1px);
      color: #fff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
  }
  .currency-zh{
      font-size: calc(0.85rem + 1px);
      color: rgba(255,255,255,0.6);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
  }

  /* ✅ 結果文字：不要省略號（避免 VND 超大金額出現 ...） */
  .result-text{
      font-size: calc(1.2rem + 1px);
      font-weight: 800;
      color: #4CAF50;
      white-space: nowrap;
      overflow: visible !important;
      text-overflow: clip !important;
  }
  /* ✅ 太長自動縮字（不換行、不省略） */
  .result-text.tight{
      font-size: calc(1.05rem + 1px) !important;
      letter-spacing: -0.3px;
  }
  .result-text.tighter{
      font-size: calc(0.95rem + 1px) !important;
      letter-spacing: -0.5px;
  }

  .rate-text{
      font-size: 0.8rem;
      color: rgba(255,255,255,0.55);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
  }

  /* ✅ 列與列之間空隙：縮小到約 1/3 */
  .fx-hr{
      margin: 0.06rem 0 !important;
      opacity: 0.14 !important;
      border: none !important;
      border-top: 1px solid rgba(255,255,255,0.12) !important;
  }

  /* 隱藏 Streamlit 右上角 menu/footer */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}

  /* 手機超窄時微調 */
  @media (max-width: 420px){
      div[data-testid="stHorizontalBlock"]{ gap: 0.30rem !important; }
      .fx-row div[data-testid="stHorizontalBlock"]{ gap: 0.30rem !important; }
      div.row-widget.stButton > button{ height: 2.45rem !important; font-size: 1.12rem !important; }
      .fx-row div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(4){
          flex: 0 0 40% !important;
          width: 40% !important;
      }
  }
</style>
""", unsafe_allow_html=True)

# ===== 標題 =====
st.markdown("<h2 style='margin:0; margin-bottom: 10px;'>多國匯率計算器</h2>", unsafe_allow_html=True)

# --- 2. 資料處理 ---
@st.cache_data(ttl=300)
def get_rates_data():
    url = "https://open.er-api.com/v6/latest/TWD"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        # ✅ 匯率「資料更新時間」：用 API 的 time_last_update_unix
        ts = data.get("time_last_update_unix")
        if ts:
            tw_tz = ZoneInfo("Asia/Taipei")
            update_time = (
                datetime.fromtimestamp(ts, tz=timezone.utc)
                .astimezone(tw_tz)
                .strftime("%Y/%m/%d %H:%M")
            )
        else:
            update_time = "未知"

        return data["rates"], update_time

    except Exception:
        st.error("⚠️ 網路異常")
        return None, None

rates, update_time = get_rates_data()
if not rates:
    st.stop()

# --- 幣別設定 ---
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

# --- 4. Source 區塊 ---
st.caption(f"匯率最後更新時間: {update_time}")

with st.container(border=True):
    st.caption("💰 目前持有 (Source)")

    st.markdown('<div class="source-row">', unsafe_allow_html=True)

    # ✅ 你要的平衡點 [6,4]
    c1, c2 = st.columns([6, 4], vertical_alignment="center")

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

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="opacity:0.65; font-size:0.85rem; margin-top:0.4rem;">'
        '記憶功能說明: 點選貨幣左方📌訂選後進行記憶，最多記憶三組</div>',
        unsafe_allow_html=True
    )

# --- 5. 記憶清單 ---
if st.session_state["saved_items"]:
    st.markdown("---")
    st.caption("📌 記憶清單")

    for idx, item in enumerate(st.session_state["saved_items"]):
        b_fmt = f"{item['base_amt']:,.2f}"
        t_fmt = f"{item['target_amt']:,.0f}" if item["target"] in ["VND", "JPY", "KRW"] else f"{item['target_amt']:,.2f}"

        c_card, c_del = st.columns([8.5, 1.5], vertical_alignment="center")
        with c_card:
            flag_url = f"https://flagcdn.com/w40/{currency_flag_codes.get(item['target'], 'un')}.png"
            st.markdown(f"""
            <div style="
              background: rgba(255,255,255,0.05);
              border: 1px solid rgba(255,255,255,0.1);
              border-radius: 10px;
              padding: 0.55rem 0.8rem;
              display:flex; align-items:center; justify-content:space-between;">
              <div style="opacity:0.85;">
                {item['base']} {b_fmt} ➝
                <img src="{flag_url}" style="width:20px;height:15px;vertical-align:middle;margin:0 4px;">
                <span style="color:#FFD700;font-weight:700;">{item['target']} {t_fmt}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        with c_del:
            st.button("🗑️", key=f"del_saved_{idx}", on_click=delete_saved_item, args=(idx,))

# --- 6. Target 列表 ---
st.markdown("---")
st.caption("🌍 即時換算 (Target)")

base = st.session_state["base_currency"]
base_amount = st.session_state["input_amount"]
display_list = st.session_state["display_order"]
base_rate_to_twd = rates.get(base, 1)

for i, target_curr in enumerate(display_list):
    if target_curr not in rates:
        continue

    target_rate_to_twd = rates.get(target_curr, 1)
    cross_rate = target_rate_to_twd / base_rate_to_twd
    converted_amount = base_amount * cross_rate

    st.markdown('<div class="fx-row">', unsafe_allow_html=True)

    c_pin, c_swap, c_info, c_res = st.columns([1, 1, 4, 4], vertical_alignment="center")

    with c_pin:
        st.button(
            "📌",
            key=f"pin_{target_curr}",
            on_click=save_currency_direct,
            args=(target_curr, cross_rate),
            help="訂選"
        )

    with c_swap:
        st.button(
            "⇅",
            key=f"swap_{target_curr}",
            on_click=swap_currency_btn_click,
            args=(target_curr,),
            help="交換"
        )

    with c_info:
        flag_url = f"https://flagcdn.com/w80/{currency_flag_codes.get(target_curr, 'un')}.png"
        c_name = currency_names.get(target_curr, target_curr)
        st.markdown(f"""
        <div style="display:flex; align-items:center; min-width:0;">
            <img src="{flag_url}" class="flag-img" alt="{target_curr}">
            <div style="min-width:0;">
                <div class="currency-code">{target_curr}</div>
                <div class="currency-zh">{c_name}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_res:
        fmt = "{:,.2f}" if converted_amount < 10000 else "{:,.1f}"
        if target_curr in ["VND", "JPY", "KRW"]:
            fmt = "{:,.0f}"
        val_str = fmt.format(converted_amount)

        # ✅ 太長就縮字（不省略、不換行）
        n = len(val_str)
        extra_cls = ""
        if n >= 16:
            extra_cls = "tighter"
        elif n >= 13:
            extra_cls = "tight"

        st.markdown(f"""
        <div style="text-align:right; min-width:0;">
            <div class="result-text {extra_cls}">{val_str}</div>
            <div class="rate-text">匯率: {cross_rate:,.4f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if i != len(display_list) - 1:
        st.markdown("<hr class='fx-hr'/>", unsafe_allow_html=True)
