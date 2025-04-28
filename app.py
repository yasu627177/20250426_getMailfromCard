import streamlit as st
import pandas as pd
from PIL import Image
import io
import os
import cv2
import numpy as np
import tempfile
import logging
from datetime import datetime
from modules import ocr, parser, exporter, constants

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Streamlit UI設定
st.set_page_config(page_title="名刺OCRアプリ", layout="wide")

def save_uploaded_file(uploaded_file):
    """
    アップロードされたファイルを一時ファイルとして保存
    
    Args:
        uploaded_file: Streamlitのファイルオブジェクト
        
    Returns:
        str: 保存された一時ファイルのパス
    """
    try:
        # アップロードディレクトリを作成
        os.makedirs(constants.UPLOAD_DIR, exist_ok=True)
        
        # ファイル名を生成（元の名前＋タイムスタンプ）
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(constants.UPLOAD_DIR, file_name)
        
        # ファイルを保存
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path
    except Exception as e:
        logger.error(f"ファイル保存エラー: {str(e)}")
        return None

def process_image(image_path):
    """
    画像を処理してデータを抽出する共通関数
    
    Args:
        image_path: 処理する画像のパス
        
    Returns:
        tuple: (成功したかどうか, エラーメッセージ, 抽出テキスト, 構造化データ)
    """
    try:
        # OCR処理
        ocr_text, processed_images = ocr.extract_text_from_image(image_path)
        
        # OCRエラーチェック
        if "エラー" in ocr_text or "失敗" in ocr_text:
            return False, ocr_text, None, None
        
        # Gemini APIでテキスト構造化
        try:
            structured_data = parser.parse_text(ocr_text)
            return True, None, ocr_text, structured_data
        except Exception as api_err:
            error_msg = str(api_err)
            # APIクォータエラーの特別処理
            if "429" in error_msg:
                return False, "Gemini APIのクォータ制限に達しました。しばらく待ってから再試行してください。", ocr_text, None
            else:
                return False, f"Gemini APIエラー: {error_msg}", ocr_text, None
    except Exception as e:
        return False, f"処理中にエラーが発生しました: {str(e)}", None, None

def main():
    st.title("名刺OCRアプリ")
    st.subheader("名刺画像から情報を抽出・整理・保存")
    
    # セッション状態の初期化
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame(columns=constants.COLUMNS)
    
    # 左カラム：画像アップロード
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### 名刺画像をアップロード")
        
        # タブで「アップロード」と「サンプル」を切り替え
        tab1, tab2 = st.tabs(["📷 アップロード", "📊 サンプル"])
        
        with tab1:
            uploaded_file = st.file_uploader("名刺画像を選択", type=["png", "jpg", "jpeg"])
            
            if uploaded_file:
                # 画像表示
                image = Image.open(uploaded_file)
                st.image(image, caption="アップロードされた名刺", use_column_width=True)
                
                # OCR処理ボタン
                if st.button("🔍 データ抽出", key="extract_uploaded"):
                    with st.spinner("画像を処理中..."):
                        # 画像を一時ファイルとして保存
                        temp_image_path = save_uploaded_file(uploaded_file)
                        if not temp_image_path:
                            st.error("画像の保存に失敗しました。再度アップロードしてください。")
                        else:
                            # 画像処理
                            success, error_msg, ocr_text, structured_data = process_image(temp_image_path)
                            
                            if success:
                                st.text_area("抽出テキスト", ocr_text, height=150)
                                
                                # DataFrameに追加
                                new_df = pd.DataFrame([structured_data])
                                st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                                
                                st.success("データ抽出に成功しました！")
                            else:
                                st.error(error_msg)
                                if ocr_text:
                                    st.text_area("抽出テキスト", ocr_text, height=150)
                                    st.info("OCRでテキストは抽出できましたが、Gemini APIでの解析に失敗しました。APIキーや接続を確認してください。")
        
        with tab2:
            st.write("サンプル名刺を選択してテスト")
            
            # サンプルディレクトリの確認とサンプル表示
            samples_dir = "samples"
            if os.path.exists(samples_dir) and os.listdir(samples_dir):
                sample_files = [f for f in os.listdir(samples_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
                
                if sample_files:
                    sample_choice = st.selectbox(
                        "サンプル名刺を選択",
                        options=sample_files,
                        format_func=lambda x: x.replace('_', ' ').replace('.png', '').replace('.jpg', '')
                    )
                    
                    sample_path = os.path.join(samples_dir, sample_choice)
                    
                    # サンプル画像表示
                    sample_image = Image.open(sample_path)
                    st.image(sample_image, caption=f"サンプル: {sample_choice}", use_column_width=True)
                    
                    # 処理ボタン
                    if st.button("🔍 サンプルを処理", key="process_sample"):
                        with st.spinner("サンプル画像を処理中..."):
                            # 画像処理
                            success, error_msg, ocr_text, structured_data = process_image(sample_path)
                            
                            if success:
                                st.text_area("抽出テキスト", ocr_text, height=150)
                                
                                # DataFrameに追加
                                new_df = pd.DataFrame([structured_data])
                                st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                                
                                st.success("サンプルデータの抽出に成功しました！")
                            else:
                                st.error(error_msg)
                                if ocr_text:
                                    st.text_area("抽出テキスト", ocr_text, height=150)
                else:
                    st.warning("サンプル名刺が見つかりません。サンプル生成スクリプトを実行してください。")
                    if st.button("サンプル名刺を生成"):
                        try:
                            import subprocess
                            result = subprocess.run(["python", "generate_sample_card.py"], capture_output=True, text=True)
                            if result.returncode == 0:
                                st.success("サンプル名刺を生成しました！ページを更新してください。")
                            else:
                                st.error(f"サンプル生成エラー: {result.stderr}")
                        except Exception as e:
                            st.error(f"サンプル生成中にエラーが発生しました: {str(e)}")
            else:
                st.warning("サンプルディレクトリが見つかりません。サンプル生成スクリプトを実行してください。")
                if st.button("サンプル名刺を生成"):
                    try:
                        import subprocess
                        result = subprocess.run(["python", "generate_sample_card.py"], capture_output=True, text=True)
                        if result.returncode == 0:
                            st.success("サンプル名刺を生成しました！ページを更新してください。")
                        else:
                            st.error(f"サンプル生成エラー: {result.stderr}")
                    except Exception as e:
                        st.error(f"サンプル生成中にエラーが発生しました: {str(e)}")
    
    # 右カラム：データ表示と保存機能
    with col2:
        st.write("### 抽出された名刺データ")
        if not st.session_state.df.empty:
            st.dataframe(st.session_state.df, use_container_width=True)
            
            # 保存ボタン
            st.write("### データを保存")
            
            st.download_button(
                "💾 CSVとして保存",
                exporter.to_csv(st.session_state.df),
                file_name="meishi_data.csv",
                mime="text/csv"
            )
            
            # データのクリア
            if st.button("🗑️ データをクリア"):
                st.session_state.df = pd.DataFrame(columns=constants.COLUMNS)
                st.experimental_rerun()
        else:
            st.info("名刺をアップロードして「データ抽出」ボタンを押すと、ここに結果が表示されます。")
    
    # アプリの説明
    with st.expander("📖 このアプリについて"):
        st.markdown("""
        ### 名刺OCRアプリ
        
        このアプリは、名刺画像から情報を自動的に抽出し、整理・保存する機能を提供します。
        
        **機能：**
        - 名刺画像のOCR処理による文字認識
        - Google Gemini APIを使用した情報の構造化
        - CSV形式でのデータ保存
        
        **使い方：**
        1. 左側の「アップロード」タブで名刺画像をアップロード、または「サンプル」タブでサンプル名刺を選択
        2. 「データ抽出」ボタンをクリックして処理を開始
        3. 抽出されたデータは右側の表に表示されます
        4. 必要に応じてCSVに保存
        
        **注意事項：**
        - APIの利用制限により、短時間に多数のリクエストを行うとエラーが発生することがあります
        - 名刺の品質や記載方法によっては、認識精度が低下する場合があります
        """)

if __name__ == "__main__":
    main() 