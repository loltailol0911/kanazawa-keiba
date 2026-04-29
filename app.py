import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- 設定エリア ---
genai.configure(api_key="AIzaSyC2QURLKQk3krzFzqn2tCHPAO8A6DoM_4w")
model = model = genai.GenerativeModel('gemini-1.5-flash-latest') # 高速・低コスト版

# --- UI構築（Xiaomi POCO 視認性重視） ---
st.set_page_config(page_title="S-Analyzer v2.2", layout="centered")
st.title("🏇 金沢競馬投資解析 v2.2")
st.caption("URLを貼るだけでプロトコルに基づいた買い目を算出します")

# URL入力
target_url = st.text_input("レースURL（nankanske.or.jp等）を入力")

if st.button("解析実行"):
    if not target_url:
        st.error("URLを入力してください")
    else:
        with st.spinner("データを取得・解析中..."):
            try:
                # 1. スクレイピング実行
                res = requests.get(target_url)
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 不要なタグを削ぎ落としてテキスト化
                for script in soup(["script", "style"]):
                    script.decompose()
                race_text = soup.get_text()

                # 2. プロトコルをシステムプロンプトとして注入
                instruction = """
                あなたはS-Analyzer v2.2として、提供された競馬データから
                【金沢競馬 EV最大化・投資プロトコル v2.2】を厳守して投資パケットを出力せよ。
                1点100円、総額1,500円〜3,600円、比率6:3:1を絶対守ること。
                """
                
                # 3. Geminiに投げる
                response = model.generate_content([instruction, race_text])
                
                # 4. 結果表示
                st.success("解析完了")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
