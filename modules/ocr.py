"""
OCR処理を行うモジュール：
- 画像から文字を抽出する機能を提供
- 複数の前処理と言語設定を適用し、名刺の認識精度を向上
"""

import os
import logging
import cv2
import numpy as np
import pytesseract
from datetime import datetime
from .constants import PROCESSED_IMAGES_DIR, SAVE_IMAGES

# Tesseractコマンドのパスを環境変数から取得
TESSERACT_CMD_PATH = os.getenv('TESSERACT_CMD_PATH', '/usr/bin/tesseract')
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH

# ロガーを設定
logger = logging.getLogger(__name__)

def preprocess_image(image):
    """
    OCR認識精度向上のための画像前処理を実行
    
    Args:
        image (numpy.ndarray): 入力画像
        
    Returns:
        dict: 処理済み画像の辞書
    """
    try:
        # 元の画像のコピーを作成
        original = image.copy()
        
        # グレースケールに変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # ノイズ除去（バイラテラルフィルタ）
        denoise = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # 二値化（通常の閾値処理）
        _, binary = cv2.threshold(denoise, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 適応的二値化（局所的な閾値を使用）
        adaptive_binary = cv2.adaptiveThreshold(
            denoise, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # モルフォロジー演算（ノイズ除去とテキスト領域の強調）
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(adaptive_binary, cv2.MORPH_CLOSE, kernel)
        
        return {
            "original": original,
            "gray": gray,
            "denoise": denoise,
            "binary": binary,
            "adaptive": adaptive_binary,
            "morph": morph
        }
    except Exception as e:
        logger.error(f"画像の前処理中にエラーが発生しました: {str(e)}")
        return {"original": image}

def extract_text_from_image(image_path, save_processed_images=False):
    """
    画像から文字を抽出する
    
    Args:
        image_path (str): 画像ファイルのパス
        save_processed_images (bool): 処理済み画像を保存するかどうか
        
    Returns:
        tuple: (抽出されたテキスト, 処理済み画像の辞書)
    """
    try:
        # 画像を読み込み
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"画像の読み込みに失敗しました: {image_path}")
            return "画像の読み込みに失敗しました", {}
        
        # 画像を前処理
        processed_images = preprocess_image(image)
        
        # OCR設定
        configs = [
            # 日本語+英語（縦書き・横書き両方）
            "--psm 3 --oem 3 -l jpn+eng",
            # 日本語のみ
            "--psm 3 --oem 3 -l jpn",
            # 英語のみ
            "--psm 3 --oem 3 -l eng",
            # 複数ブロックとして処理（レイアウト分析あり）
            "--psm 1 --oem 3 -l jpn+eng",
            # 単一ブロックとして処理
            "--psm 6 --oem 3 -l jpn+eng"
        ]
        
        # 処理済み画像ごとにOCRを実行し、結果を結合
        all_text = []
        
        # 処理済み画像を保存（デバッグ用）
        if SAVE_IMAGES and save_processed_images:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            save_processed_images_to_disk(processed_images, os.path.basename(image_path), timestamp)
        
        # 各前処理画像に対してOCR実行
        for img_name, proc_img in processed_images.items():
            if img_name == "original":
                continue  # オリジナル画像はスキップ（カラー画像のため）
                
            for config in configs:
                try:
                    text = pytesseract.image_to_string(proc_img, config=config)
                    if text.strip():
                        all_text.append(text)
                except Exception as e:
                    logger.warning(f"OCR実行中にエラー（設定: {config}, 画像: {img_name}）: {str(e)}")
        
        # 結果をまとめる
        combined_text = "\n".join(all_text)
        
        # 結果がない場合
        if not combined_text.strip():
            logger.warning("OCRから有効なテキストが抽出できませんでした。")
            return "テキスト抽出に失敗しました。別の画像を試してください。", processed_images
            
        return combined_text, processed_images
        
    except Exception as e:
        logger.error(f"OCR処理中にエラーが発生しました: {str(e)}")
        return f"エラー: {str(e)}", {}

def save_processed_images_to_disk(processed_images, original_filename, timestamp):
    """
    処理済み画像を保存する（デバッグ用）
    
    Args:
        processed_images (dict): 処理済み画像の辞書
        original_filename (str): 元の画像ファイル名
        timestamp (str): タイムスタンプ
    """
    try:
        # ファイル名から拡張子を取り除く
        filename_base = os.path.splitext(original_filename)[0]
        
        # 保存ディレクトリが存在しない場合は作成
        save_dir = os.path.join(PROCESSED_IMAGES_DIR, f"{filename_base}_{timestamp}")
        os.makedirs(save_dir, exist_ok=True)
        
        # 各処理済み画像を保存
        for img_name, img in processed_images.items():
            if img_name == "original":
                # カラー画像はそのまま保存
                save_path = os.path.join(save_dir, f"{img_name}.jpg")
                cv2.imwrite(save_path, img)
            else:
                # グレースケール画像を保存
                save_path = os.path.join(save_dir, f"{img_name}.jpg")
                cv2.imwrite(save_path, img)
                
        logger.debug(f"処理済み画像を保存しました: {save_dir}")
    except Exception as e:
        logger.error(f"処理済み画像の保存中にエラーが発生しました: {str(e)}") 