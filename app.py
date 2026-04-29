import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- 1. 設定エリア ---
# ※ここに新しいキーを貼り付けてください
API_KEY = "AIzaSyDuEemiGKUS8owTApI4vHdXYzmuQw_BBMU" 

genai.configure(api_key=API_KEY)

# 404エラーを回避するための最も汎用的なモデル指定
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. UI構築 ---
st.set_page_config(page_title="S-Analyzer v2.2", page_icon="🏇")
st.title("🏇 金沢競馬投資解析 v2.2")

target_url = st.text_input("レースURLを入力")

if st.button("解析実行", type="primary"):
    if not target_url or "http" not in target_url:
        st.error("有効なURLを入力してください。")
    else:
        with st.spinner("解析中..."):
            try:
                # データ取得
                res = requests.get(target_url, timeout=10)
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, 'html.parser')
                race_text = soup.get_text()

                # 解析実行
                instruction = "金沢競馬投資プロトコル v2.2に従い、結論ファーストで買い目を提案せよ。1点100円、総額1500-3600円、比率6:3:1を厳守。"
                response = model.generate_content([instruction, race_text])
                
                st.success("解析完了")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"エラー内容: {str(e)}")
