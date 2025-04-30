import streamlit as st
import pandas as pd
from PIL import Image
import io
import os
import tempfile
import logging
from datetime import datetime
from modules import ocr, parser, exporter, constants, qr_reader
from dotenv import load_dotenv
import shutil

# 環境変数の読み込み
load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数の設定
SAVE_IMAGES = os.getenv('SAVE_IMAGES', 'false').lower() == 'true'

# Streamlit UI設定
st.set_page_config(
    page_title="名刺OCRアプリ",
    page_icon="📇",
    layout="wide"
)

def process_image(image_path):
    """
    画像を処理してデータを抽出する共通関数
    
    Args:
        image_path: 処理する画像のパス
        
    Returns:
        tuple: (成功したかどうか, エラーメッセージ, 抽出テキスト, QRコードテキスト, 構造化データ)
    """
    try:
        # 画像を読み込み
        pil_image = Image.open(image_path)
        
        # OCR処理
        ocr_text, processed_images = ocr.extract_text_from_image(image_path, save_processed_images=SAVE_IMAGES)
        
        # OCRエラーチェック
        if "エラー" in ocr_text or "失敗" in ocr_text:
            return False, ocr_text, None, None, None
        
        # QRコード読み取り
        qr_text = qr_reader.read_qr_from_image(pil_image)
        if qr_text:
            logger.info(f"QRコード検出: {qr_text[:50]}...")
            
            # sasaeai URLの特別処理
            if qr_reader.is_sasaeai_url(qr_text):
                logger.info("sasaeai URLを検出しました")
        
        # Gemini APIでテキスト構造化
        try:
            # QRコード情報も含めて構造化
            structured_data = parser.parse_text(ocr_text, qr_text)
            
            # 予備メールアドレスと予備電話番号を「その他」に移動
            if structured_data:
                other_info = []
                if structured_data.get('メールアドレス（予備）'):
                    other_info.append(f"予備メールアドレス: {structured_data['メールアドレス（予備）']}")
                    del structured_data['メールアドレス（予備）']
                if structured_data.get('電話番号（予備）'):
                    other_info.append(f"予備電話番号: {structured_data['電話番号（予備）']}")
                    del structured_data['電話番号（予備）']
                
                if other_info:
                    if structured_data.get('その他'):
                        structured_data['その他'] += "\n" + "\n".join(other_info)
                    else:
                        structured_data['その他'] = "\n".join(other_info)
            
            return True, None, ocr_text, qr_text, structured_data
        except Exception as api_err:
            error_msg = str(api_err)
            # APIクォータエラーの特別処理
            if "429" in error_msg:
                return False, "Gemini APIのクォータ制限に達しました。しばらく待ってから再試行してください。", ocr_text, qr_text, None
            else:
                return False, f"Gemini APIエラー: {error_msg}", ocr_text, qr_text, None
    except Exception as e:
        return False, f"処理中にエラーが発生しました: {str(e)}", None, None, None

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
        uploaded_file = st.file_uploader("名刺画像を選択", type=["png", "jpg", "jpeg"])
        
        if uploaded_file:
            # 画像表示
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされた名刺", use_column_width=True)
            
            # OCR処理ボタン
            if st.button("🔍 データ抽出", key="extract_uploaded"):
                with st.spinner("画像を処理中..."):
                    # 一時ファイルとして保存
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name
                    
                    try:
                        # 画像処理
                        success, error_msg, ocr_text, qr_text, structured_data = process_image(temp_path)
                        
                        if success:
                            # テキスト情報の表示
                            st.text_area("OCRで抽出したテキスト", ocr_text, height=120)
                            
                            # QRコード情報があれば表示
                            if qr_text:
                                st.text_area("QRコードから抽出したリンク", qr_text, height=60)
                            
                            # DataFrameに追加
                            new_df = pd.DataFrame([structured_data])
                            st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                            
                            st.success("データ抽出に成功しました！")
                        else:
                            st.error(error_msg)
                            if ocr_text:
                                st.text_area("OCRで抽出したテキスト", ocr_text, height=120)
                                if qr_text:
                                    st.text_area("QRコードから抽出したリンク", qr_text, height=60)
                                st.info("テキストは抽出できましたが、Gemini APIでの解析に失敗しました。APIキーや接続を確認してください。")
                    finally:
                        # 一時ファイルの削除
                        os.unlink(temp_path)
    
    # 右カラム：データ表示と保存機能
    with col2:
        st.write("### 抽出された名刺データ")
        if not st.session_state.df.empty:
            # データ表示
            st.dataframe(st.session_state.df, use_container_width=True)
            
            # CSV保存ボタン
            csv = exporter.to_csv(st.session_state.df)
            st.download_button(
                label="📥 CSVダウンロード",
                data=csv,
                file_name=f"meishi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
            
            # データクリアボタン
            if st.button("🗑 データクリア"):
                st.session_state.df = pd.DataFrame(columns=constants.COLUMNS)
                st.experimental_rerun()
        else:
            st.info("名刺データがまだありません。左側から名刺画像をアップロードしてデータ抽出を行ってください。")

    # フッター
    st.markdown("---")
    st.markdown("© 2024 名刺OCRアプリ")

if __name__ == "__main__":
    main() 