import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

# --- 1. 設定エリア ---
API_KEY = "AIzaSyDuEemiGKUS8owTApI4vHdXYzmuQw_BBMU" 

# 新世代SDKのクライアント作成（v1安定版を明示的に指定）
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(api_version="v1")
)

# --- 2. UI構築（Xiaomi POCO 最適化） ---
st.set_page_config(page_title="S-Analyzer v2.2", layout="centered")
st.title("🏇 金沢競馬投資解析 v2.2")

target_url = st.text_input("レースURLを入力", placeholder="https://...")

if st.button("解析実行", type="primary"):
    if not target_url:
        st.error("URLを入力してください。")
    else:
        with st.spinner("最新モデルで解析中..."):
            try:
                # A. データ取得
                res = requests.get(target_url, timeout=10)
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, 'html.parser')
                race_text = soup.get_text()

                # B. 解析実行 (最新の gemini-2.0-flash または 1.5-flash)
                # 404を避けるため、最も標準的な 'gemini-1.5-flash' を指定
                instruction = "金沢競馬投資プロトコル v2.2に従い、結論ファーストで買い目を提案せよ。1点100円、総額1500-3600円、比率6:3:1を厳守。"
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[instruction, race_text]
                )
                
                st.success("解析完了")
                st.markdown("---")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"システムエラー: {str(e)}")
