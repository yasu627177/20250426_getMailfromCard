"""
名刺テキスト解析の動作確認スクリプト
"""

import os
import sys
import logging
import json
import argparse
from dotenv import load_dotenv

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# モジュールの検索パスにカレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 環境変数の読み込み
load_dotenv()

# parserモジュールのインポート
from modules.parser import parse_text

# テストケース
TEST_CASES = {
    "standard": """
株式会社サンプルテクノロジー
SAMPLE TECHNOLOGY INC.

山田 太郎
Taro Yamada

取締役 技術部長
Director, CTO

〒100-0001
東京都千代田区丸の内1-1-1
サンプルビル8F

TEL: 03-1234-5678
FAX: 03-1234-5679
Email: yamada@example.com
https://www.example.com
    """,
    
    "minimal": """
山田太郎
株式会社サンプル
営業部
03-1234-5678
yamada@example.com
    """,
    
    "english": """
ACME Corporation
123 Main Street
New York, NY 10001

John Smith
Senior Sales Manager

Phone: +1 (212) 555-1234
Email: john.smith@acme.com
Website: https://www.acme.com
    """,
    
    "complex": """
AIテクノロジー株式会社
AI Technology Co., Ltd.

佐藤 健太 / Kenta Sato
代表取締役CEO / CEO & Founder

〒150-0002 東京都渋谷区渋谷3-10-15
渋谷MIビル5F

固定：03-1234-5678
携帯：080-1234-5678
メール：sato.k@ai-tech.co.jp
ウェブ：https://www.ai-tech.co.jp
Twitter: @kentasato
LinkedIn: /in/kentasato
    """
}

def main():
    """
    メイン処理関数
    """
    parser = argparse.ArgumentParser(description='名刺テキスト解析のテスト')
    parser.add_argument('--case', choices=list(TEST_CASES.keys()) + ['all'], default='all',
                        help='実行するテストケース（デフォルト: all）')
    args = parser.parse_args()
    
    logger.info("名刺テキスト解析のテスト開始")
    
    # APIキーの確認
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")
        return
    
    # テストケースの実行
    test_cases = [args.case] if args.case != 'all' else TEST_CASES.keys()
    
    for case in test_cases:
        if case not in TEST_CASES:
            logger.warning(f"不明なテストケース: {case}")
            continue
            
        logger.info(f"=== テストケース '{case}' の実行 ===")
        ocr_text = TEST_CASES[case]
        
        logger.info("テスト用OCRテキスト:")
        logger.info(ocr_text)
        
        try:
            # テキスト解析の実行
            result = parse_text(ocr_text)
            
            # 結果の表示
            logger.info("解析結果:")
            logger.info(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 期待する主要情報が含まれているか確認
            expected_keys = ["名前", "会社名", "職業", "住所", "電話番号", "メールアドレス", "HP URL"]
            missing_keys = [key for key in expected_keys if not result.get(key)]
            
            if missing_keys:
                logger.warning(f"以下の情報が抽出されていません: {', '.join(missing_keys)}")
            else:
                logger.info("主要情報はすべて抽出されています")
                
            logger.info(f"=== テストケース '{case}' 完了 ===\n")
        
        except Exception as e:
            logger.exception(f"テスト '{case}' 中にエラーが発生しました: {e}")
    
    logger.info("名刺テキスト解析のテスト完了")

if __name__ == "__main__":
    main() 