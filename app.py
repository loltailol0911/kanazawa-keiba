import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

# --- 1. 設定エリア（セキュリティ・堅牢性重視） ---
try:
    # Streamlit Cloudの「Settings > Secrets」に設定したキーを読み込む
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("エラー: Secretsに 'GEMINI_API_KEY' が設定されていません。")
    st.info("Streamlit Cloud管理画面 > Settings > Secrets に GEMINI_API_KEY = 'あなたのキー' を登録してください。")
    st.stop()

# 最新SDKクライアント初期化（v1安定版を指定して404を回避）
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(api_version="v1")
)

# --- 2. UI構築（Xiaomi POCO 視認性・スマホ操作性最適化） ---
st.set_page_config(
    page_title="S-Analyzer v2.2", 
    page_icon="🏇", 
    layout="centered"
)

# カスタムCSSでスマホでの文字サイズを微調整
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .stTextInput>div>div>input { font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏇 金沢競馬投資解析 v2.2")
st.caption("Gemini 2.0 Flash / 1.5 Flash 併用型エンジン")

# 入力欄
target_url = st.text_input("レースURLを入力", placeholder="https://www.nankanske.or.jp/...")

# --- 3. メインロジック ---
if st.button("解析実行", type="primary"):
    if not target_url:
        st.warning("解析対象のURLを入力してください。")
    else:
        with st.spinner("データを取得・解析中..."):
            try:
                # A. スクレイピング（出走表の取得）
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(target_url, headers=headers, timeout=10)
                res.encoding = res.apparent_encoding
                
                if res.status_code != 200:
                    st.error(f"サイトにアクセスできません (Status: {res.status_code})")
                    st.stop()

                soup = BeautifulSoup(res.text, 'html.parser')
                # スクリプトやスタイルを削除してテキストを軽量化
                for s in soup(["script", "style", "nav", "footer"]):
                    s.decompose()
                race_text = soup.get_text(separator="\n", strip=True)

                # B. プロトコル（指示書）の定義
                instruction = """
                あなたはS-Analyzer v2.2として、提供された競馬データから
                【金沢競馬 EV最大化・投資プロトコル v2.2】を厳守して投資パケットを出力せよ。
                
                【厳守ルール】
                1. 結論（買い目）を冒頭に書く「結論ファースト」を徹底すること。
                2. 1点100円固定、総額1,500円〜3,600円。
                3. 比率：コア(60%)、攻め(30%)、ボーナス(10%)。
                4. なぜその馬を選んだかの根拠を簡潔に箇条書きで示すこと。
                """

                # C. 404回避のためのフォールバック解析
                response = None
                # モデル候補を順番に試行
                for model_id in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        response = client.models.generate_content(
                            model=model_id,
                            contents=[instruction, race_text]
                        )
                        if response:
                            used_model = model_id
                            break
                    except Exception as e:
                        if "404" in str(e):
                            continue
                        else:
                            raise e

                # D. 結果表示
                if response:
                    st.success(f"解析完了 (Model: {used_model})")
                    st.markdown("---")
                    st.markdown(response.text)
                else:
                    st.error("モデルの呼び出しに失敗しました。")

            except Exception as e:
                st.error(f"システムエラーが発生しました: {str(e)}")

# フッター
st.markdown("---")
st.caption("S-Analyzer v2.2 | Infrastructure Optimized | Night-time Saver Ready")
