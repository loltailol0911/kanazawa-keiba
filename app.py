import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- 1. 設定エリア（APIキーをここに貼り付け） ---
API_KEY = "AIzaSyC2QURLKQk3krzFzqn2tCHPAO8A6DoM_4w"  # ←取得したAPIキーに書き換えてください

# 安全な接続設定
genai.configure(api_key=API_KEY)

# 修正ポイント: 'models/' を外し、かつ最新の安定版名称に固定
# Google AI StudioのAPIキーで最も通りやすい表記です
try:
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
except:
    model = genai.GenerativeModel('gemini-1.5-pro')

# --- 2. UI構築（Xiaomi POCO 視認性・スマホ操作性重視） ---
st.set_page_config(
    page_title="S-Analyzer v2.2",
    page_icon="🏇",
    layout="centered"
)

st.title("🏇 金沢競馬投資解析 v2.2")
st.caption("URLを貼るだけでプロトコルに基づいた買い目を算出します")

# 入力欄
target_url = st.text_input("レースURL（nankanske.or.jp等）を入力", placeholder="https://...")

# --- 3. メインロジック ---
if st.button("解析実行", type="primary"):
    if not target_url:
        st.error("URLを入力してください。")
    elif API_KEY == "YOUR_API_KEY_HERE":
        st.error("APIキーが設定されていません。app.pyの10行目を確認してください。")
    else:
        with st.spinner("データを取得・解析中..."):
            try:
                # A. スクレイピング（出走表の取得）
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(target_url, headers=headers, timeout=10)
                res.encoding = res.apparent_encoding
                
                if res.status_code != 200:
                    st.error(f"サイトにアクセスできませんでした (Status: {res.status_code})")
                    st.stop()

                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 不要なタグを削除してテキストを軽量化
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                race_text = soup.get_text(separator="\n", strip=True)

                # B. プロトコル（指示書）の定義
                instruction = """
                あなたはS-Analyzer v2.2として、提供された競馬データから
                【金沢競馬 EV最大化・投資プロトコル v2.2】を厳守して投資パケットを出力せよ。
                
                【厳守ルール】
                1. 1点100円固定
                2. 1レース総額1,500円〜3,600円
                3. 比率：コア(60%)、攻め(30%)、ボーナス(10%)
                4. 結論ファーストで出力すること
                """
                
                # C. Geminiに解析を依頼
                response = model.generate_content([instruction, race_text])
                
                # D. 結果表示
                st.success("解析完了")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                # 詳細なエラー情報を表示してデバッグしやすくする
                st.error(f"エラーが発生しました: {str(e)}")
                if "404" in str(e):
                    st.info("モデル名が見つからないようです。APIキーの権限、またはモデル名の記述を再確認してください。")

# フッター
st.markdown("---")
st.caption("S-Analyzer v2.2 | Optimized for Xiaomi POCO")
