import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
import time

# --- 1. 設定エリア ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secretsに 'GEMINI_API_KEY' が未設定です。")
    st.stop()

# v1安定版エンドポイントを使用
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(api_version="v1")
)

# --- 2. UI構築（Xiaomi POCO 最適化） ---
st.set_page_config(page_title="S-Analyzer v2.2", page_icon="🏇")
st.title("🏇 金沢競馬投資解析 v2.2")
st.caption("安定性重視：Gemini 1.5 Flash 優先モード")

target_url = st.text_input("レースURLを入力", placeholder="https://...")

# --- 3. メインロジック ---
if st.button("解析実行", type="primary"):
    if not target_url:
        st.warning("URLを入力してください。")
    else:
        with st.spinner("サーバーの空きを待って解析中..."):
            try:
                # A. データ取得
                res = requests.get(target_url, timeout=10)
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(["script", "style"]): s.decompose()
                race_text = soup.get_text(separator="\n", strip=True)[:10000] # 文字数制限対策

                # B. プロトコル
                instruction = """
                あなたは金沢競馬投資解析AIです。
                【金沢競馬 EV最大化・投資プロトコル v2.2】を厳守せよ。
                1. 結論（買い目）を冒頭に。1点100円、総額1500-3600円。
                2. コア60%、攻め30%、ボーナス10%の比率。
                3. 根拠は簡潔に。
                """

                # C. 解析実行（1.5-flashをメインに据えて429を回避）
                # 無料枠で最も通りやすいモデルを選択
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[instruction, race_text]
                )

                if response:
                    st.success("解析完了")
                    st.markdown("---")
                    st.markdown(response.text)

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    st.error("【回線混雑】Google APIの無料枠制限に達しました。")
                    st.info("対策：30秒〜1分待ってから再度「解析実行」を押すか、別のAPIキーに差し替えてください。")
                else:
                    st.error(f"システムエラー: {error_msg}")

# フッター
st.markdown("---")
st.caption("S-Analyzer v2.2 | Infrastructure: Stable Mode")
