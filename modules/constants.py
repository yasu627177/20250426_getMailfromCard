"""
定数とデフォルト値を定義するモジュール
"""

import os
import logging
import re

# ロギング設定
logger = logging.getLogger(__name__)

# 環境変数の設定
SAVE_IMAGES = os.getenv('SAVE_IMAGES', 'false').lower() == 'true'

# Tesseract OCRのパス設定
TESSERACT_CMD_PATH = os.getenv('TESSERACT_CMD_PATH', '/usr/bin/tesseract')

# 共通定数の定義

# データ項目の定義
COLUMNS = [
    "名前",
    "会社名",
    "職業",
    "メールアドレス",
    "電話番号",
    "郵便番号",
    "住所",
    "HP URL",
    "sasaeai URL",
    "その他"
]

# 必須項目の定義
REQUIRED_KEYS = [
    "名前",
    "会社名",
    "職業",
    "メールアドレス",
    "電話番号",
    "郵便番号",
    "住所",
    "HP URL",
    "sasaeai URL",
    "その他"
]

# 出力用のキー順序
OUTPUT_KEYS = [
    "名前",
    "会社名",
    "職業",
    "メールアドレス",
    "電話番号",
    "郵便番号",
    "住所",
    "HP URL",
    "sasaeai URL",
    "その他"
]

# キーマッピング（日本語→英語）
KEY_MAPPING = {
    "名前": "name",
    "会社名": "company",
    "職業": "occupation",
    "メールアドレス": "email",
    "電話番号": "phone",
    "郵便番号": "postal_code",
    "住所": "address",
    "HP URL": "website",
    "sasaeai URL": "sasaeai_url",
    "その他": "other"
}

# デモデータ
DEMO_DATA = {
    "名前": "山田太郎",
    "会社名": "株式会社サンプル",
    "職業": "営業部長",
    "メールアドレス": "yamada@example.com",
    "電話番号": "03-1234-5678",
    "郵便番号": "100-0001",
    "住所": "東京都千代田区丸の内1-1-1",
    "HP URL": "https://www.example.com",
    "sasaeai URL": "https://sasaeai.link-platform.jp/123456",
    "その他": "備考情報等"
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

# APIリクエストタイムアウト（秒）
API_TIMEOUT = 30

# プロンプトテンプレートファイルのパス
PROMPT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "prompt_template.txt")

# アップロードされた画像を保存するためのディレクトリ
UPLOAD_DIR = "uploads"
if SAVE_IMAGES:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# 処理済み画像を保存するためのディレクトリ（デバッグ用）
PROCESSED_IMAGES_DIR = "processed_images"
if SAVE_IMAGES:
    os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True) 