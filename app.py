import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

# --- 1. 設定エリア ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secretsに 'GEMINI_API_KEY' が未設定です。")
    st.stop()

# クライアント初期化
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(api_version="v1")
)

# --- 2. UI構築 ---
st.set_page_config(page_title="S-Analyzer v2.2", page_icon="🏇")
st.title("🏇 金沢競馬投資解析 v2.2")
st.caption("v1 API 安定稼働パッチ適用済")

target_url = st.text_input("レースURLを入力", placeholder="https://...")

# --- 3. メインロジック ---
if st.button("解析実行", type="primary"):
    if not target_url:
        st.warning("URLを入力してください。")
    else:
        with st.spinner("解析中..."):
            try:
                # A. データ取得
                res = requests.get(target_url, timeout=10)
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(["script", "style"]): s.decompose()
                race_text = soup.get_text(separator="\n", strip=True)[:15000]

                # B. 解析実行
                response = client.models.generate_content(
                    model="gemini-2.0-flash",  # ✅ ここを修正
                    contents=[
                        "金沢競馬投資プロトコル v2.2に従い、結論ファーストで買い目を提案せよ。1点100円、総額1500-3600円、比率6:3:1を厳守。",
                        race_text
                    ]
                )
                if response:
                    st.success("解析完了")
                    st.markdown("---")
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"システムエラー: {str(e)}")

# フッター
st.markdown("---")
st.caption("S-Analyzer v2.2 | Final Production Build")
