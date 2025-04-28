"""
定数とデフォルト値を定義するモジュール
"""

import os
import logging
import re

# ロギング設定
logger = logging.getLogger(__name__)

# 共通定数の定義

# 抽出するデータ列（日本語キー）
COLUMNS = [
    "名前", "会社名", "職業", "住所", "郵便", 
    "電話番号", "メールアドレス", "メールアドレス(予備)",
    "HP URL", "sasaeai URL", "その他"
]

# 必須のキー（すべての結果に必ず含める必要があるキー）
REQUIRED_KEYS = [
    "名前", "会社名", "職業", "住所", "郵便", 
    "電話番号", "メールアドレス", "メールアドレス(予備)",
    "HP URL", "sasaeai URL", "その他"
]

# 出力用キー（英語）
OUTPUT_KEYS = [
    "name", "company", "title", "address", "postal_code", 
    "phone", "email", "email_secondary",
    "website", "sasaeai_url", "other"
]

# 日本語キーと英語キーのマッピング
KEY_MAPPING = {
    "名前": "name",
    "会社名": "company",
    "職業": "title",
    "住所": "address",
    "郵便": "postal_code",
    "電話番号": "phone",
    "メールアドレス": "email",
    "メールアドレス(予備)": "email_secondary",
    "HP URL": "website",
    "sasaeai URL": "sasaeai_url",  # sasaeai URLは https://sasaeai.link-platform.jp/ を含むURL
    "その他": "other"
}

# デモデータ（APIが利用できない場合のフォールバック）
DEMO_DATA = {
    "名前": "山田 太郎",
    "会社名": "サンプル株式会社",
    "職業": "営業部長",
    "住所": "東京都千代田区1-1-1",
    "郵便": "100-0001",
    "電話番号": "03-1234-5678",
    "メールアドレス": "yamada@example.com",
    "メールアドレス(予備)": "",
    "HP URL": "https://example.com",
    "sasaeai URL": "https://sasaeai.link-platform.jp/sample",
    "その他": "デモデータです"
}

# 使用するGeminiモデル
gemini_model = os.getenv("GEMINI_MODEL")

# 環境変数から読み込めない場合、.envファイルから直接読み込む
if not gemini_model and os.path.exists('.env'):
    try:
        logger.info("環境変数GEMINI_MODELの読み込み: .envファイルから直接読み込みます")
        env_file_path = os.path.join(os.getcwd(), '.env')
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # BOMを除去
                if line.startswith('\ufeff'):
                    line = line[1:]
                # コメント行やスペースのみの行をスキップ
                if line.strip() == '' or line.startswith('#'):
                    continue
                # キーと値のペアを抽出
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key == "GEMINI_MODEL":
                        gemini_model = value.strip()
                        logger.info(f"GEMINI_MODELを.envファイルから直接読み込みました: {gemini_model}")
                        break
    except Exception as e:
        logger.error(f".envファイルからGEMINI_MODELの読み込みエラー: {e}")

if not gemini_model:
    logger.error("環境変数GEMINI_MODELが設定されていません。.envファイルで設定してください。")
    raise ValueError("環境変数GEMINI_MODELが設定されていません")

GEMINI_MODEL = gemini_model
logger.info(f"使用するGeminiモデル: {GEMINI_MODEL}")

# Tesseractコマンドのパス
TESSERACT_CMD_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# APIリクエストタイムアウト（秒）
API_TIMEOUT = 30

# プロンプトテンプレートファイルのパス
PROMPT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "prompt_template.txt")

# アップロードされた画像を保存するためのディレクトリ
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 処理済み画像を保存するためのディレクトリ（デバッグ用）
PROCESSED_IMAGES_DIR = "processed_images"
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True) 