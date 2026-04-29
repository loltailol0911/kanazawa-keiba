import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

# --- 1. 設定エリア（Secretsから読み込み） ---
try:
    # Streamlit Cloudの「Settings > Secrets」に設定したキーを読み込む
    API_KEY = st.secrets["AIzaSyDuEemiGKUS8owTApI4vHdXYzmuQw_BBMU"]
except Exception:
    st.error("エラー: Secretsに 'GEMINI_API_KEY' が設定されていません。")
    st.info("Streamlit Cloudの管理画面 > Settings > Secrets に GEMINI_API_KEY = 'あなたのキー' を登録してください。")
    st.stop()

# 最新SDKクライアント初期化（v1安定版を指定）
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(api_version="v1")
)

# --- 2. UI構築（Xiaomi POCO 視認性重視） ---
st.set_page_config(page_title="S-Analyzer v2.2", page_icon="🏇", layout="centered")
st.title("🏇 金沢競馬投資解析 v2.2")
st.caption("最新のGemini 2.0 Flashエンジンでプロトコルを実行します")

target_url = st.text_input("レースURLを入力", placeholder="https://www.nankanske.or.jp/...")

# --- 3. メインロジック ---
if st.button("解析実行", type="primary"):
    if not target_url:
        st.warning("解析対象のURLを入力してください。")
    else:
        with st.spinner("データの取得とAI解析を行っています..."):
            try:
                # A. スクレイピング
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(target_url, headers=headers, timeout=10)
                res.encoding = res.apparent_encoding
                
                if res.status_code != 200:
                    st.error(f"サイトにアクセスできません (Status: {res.status_code})")
                    st.stop()

                soup = BeautifulSoup(res.text, 'html.parser')
                # 軽量化処理
                for s in soup(["script", "style"]):
                    s.decompose()
                race_text = soup.get_text(separator="\n", strip=True)

                # B. プロトコル（指示書）
                instruction = """
                あなたはS-Analyzer v2.2として、提供された競馬データから
                【金沢競馬 EV最大化・投資プロトコル v2.2】を厳守して投資パケットを出力せよ。
                
                【厳守ルール】
                1. 結論（買い目）を冒頭に書く「結論ファースト」を徹底すること。
                2. 1点100円固定、総額1,500円〜3,600円。
                3. 比率：コア(60%)、攻め(30%)、ボーナス(10%)。
                4. 根拠は簡潔に箇条書きで示すこと。
                """

                # C. 404回避のためのフォールバック解析
                response = None
                # 404が出にくい順に試行
                for model_id in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        response = client.models.generate_content(
                            model=model_id,
                            contents=[instruction, race_text]
                        )
                        if response: break
                    except Exception as e:
                        if "404" in str(e): continue
                        else: raise e

                # D. 結果表示
                if response:
                    st.success(f"解析完了 (使用モデル: {model_id})")
                    st.markdown("---")
                    st.markdown(response.text)
                else:
                    st.error("モデルの呼び出しに失敗しました。")

            except Exception as e:
                st.error(f"システムエラーが発生しました: {str(e)}")

# フッター
st.markdown("---")
st.caption("S-Analyzer v2.2 | Optimized for Xiaomi POCO | Power Saving Mode Active")
