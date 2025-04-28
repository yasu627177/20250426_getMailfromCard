"""
OCRモジュールの重複テキスト除去機能のテスト
"""

import os
import sys
import logging
from modules import ocr
from pprint import pprint

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_duplicate_removal():
    """
    重複テキスト除去機能のテスト
    """
    # テストデータ
    test_cases = [
        # ケース1: 完全に同一のテキスト
        {
            "input": [
                "株式会社サンプル\n山田太郎\n営業部",
                "株式会社サンプル\n山田太郎\n営業部"
            ],
            "expected_count": 1,
            "name": "完全一致"
        },
        # ケース2: 少し異なるテキスト（空白や改行の違い）
        {
            "input": [
                "株式会社サンプル\n山田 太郎\n営業部",
                "株式会社サンプル 山田太郎 営業部"
            ],
            "expected_count": 1,
            "name": "空白・改行の違い"
        },
        # ケース3: 部分的に重複するテキスト
        {
            "input": [
                "株式会社サンプル\n山田太郎\n営業部",
                "山田太郎\n営業部\n電話: 03-1234-5678",
                "電話: 03-1234-5678\nFAX: 03-1234-5679"
            ],
            "expected_count": 2,  # 「山田太郎 営業部」と「電話...FAX...」が残るはず
            "name": "部分重複"
        },
        # ケース4: 少しだけ似ているテキスト
        {
            "input": [
                "株式会社サンプルA\n山田太郎\n営業部",
                "株式会社サンプルB\n山田太郎\n営業部"
            ],
            "expected_count": 2,
            "name": "少し似ているテキスト"
        },
        # ケース5: 実際のOCR出力を模擬したケース
        {
            "input": [
                "株式会社サンプル\n代表取締役社長\n山田太郎\n〒123-4567 東京都新宿区...",
                "株式会社サンプル\n代表取締役社長\n山田 太郎",
                "TEL: 03-1234-5678\nFAX: 03-1234-5679\nEmail: yamada@sample.co.jp",
                "TEL：03-1234-5678\nFAX：03-1234-5679\nメール：yamada@sample.co.jp"
            ],
            "expected_count": 2,  # 住所付きの会社情報と連絡先情報
            "name": "OCR模擬出力"
        }
    ]
    
    # 各テストケースを実行
    for i, case in enumerate(test_cases):
        logger.info(f"テストケース {i+1}: {case['name']}")
        print(f"\n===== テストケース {i+1}: {case['name']} =====")
        
        print("\n入力テキスト:")
        for j, text in enumerate(case['input']):
            print(f"\n--- テキスト {j+1} ---")
            print(text)
        
        # 重複除去関数を実行
        result = ocr.remove_duplicate_blocks(case['input'])
        
        print("\n結果:")
        for j, text in enumerate(result):
            print(f"\n--- 結果テキスト {j+1} ---")
            print(text)
        
        # 期待値と比較
        success = len(result) == case['expected_count']
        status = "成功" if success else "失敗"
        print(f"\n結果数: {len(result)}, 期待値: {case['expected_count']}, テスト{status}")
        
        if not success:
            logger.warning(f"テストケース {i+1} 失敗: 結果数 {len(result)} != 期待値 {case['expected_count']}")

def test_ocr_with_sample():
    """
    サンプル画像を使ったOCRテスト
    """
    samples_dir = "samples"
    if not os.path.exists(samples_dir):
        logger.error(f"サンプルディレクトリが見つかりません: {samples_dir}")
        return
    
    # サンプル画像を取得
    sample_files = [f for f in os.listdir(samples_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if not sample_files:
        logger.error("サンプル画像が見つかりません")
        return
    
    for sample_file in sample_files:
        sample_path = os.path.join(samples_dir, sample_file)
        logger.info(f"サンプル画像 {sample_file} でOCRテスト実行")
        print(f"\n===== サンプル画像: {sample_file} =====")
        
        # OCR実行
        ocr_text, _ = ocr.extract_text_from_image(sample_path)
        
        print("\nOCR結果:")
        print(ocr_text)
        
        print("\n文字数:", len(ocr_text))
        print("行数:", ocr_text.count('\n') + 1)

if __name__ == "__main__":
    print("===== 重複テキスト除去機能のテスト =====\n")
    test_duplicate_removal()
    
    print("\n\n===== サンプル画像OCRテスト =====\n")
    test_ocr_with_sample() 