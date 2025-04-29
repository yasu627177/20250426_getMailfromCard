# modules/qr_reader.py

import logging
import re
import cv2
import numpy as np
from PIL import Image
from typing import Optional, List, Dict, Any, Tuple

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenCVの警告を抑制
cv2.setLogLevel(0)  # 0: 警告を抑制

def read_qr_from_image(image: Image.Image) -> Optional[str]:
    """
    PIL画像からQRコードを読み取る（前処理も自動で試行）
    """
    logger.info("QRコードの読み取りを開始（元画像→前処理画像の順で試行）")
    try:
        # 1. 元画像で検出
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 画像の前処理を強化
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # QRコード検出器の設定
        qr_detector = cv2.QRCodeDetector()
        
        # 二値化画像で検出を試みる
        value, points, straight_qrcode = qr_detector.detectAndDecode(binary)
        if value:
            logger.info(f"QRコードを二値化画像で検出: {value[:30]}...")
            return value
            
        # 2. 前処理画像で再試行
        pre_image = preprocess_image_for_qr(image)
        pre_cv_image = np.array(pre_image)
        if len(pre_cv_image.shape) == 2:
            pre_cv_image = cv2.cvtColor(pre_cv_image, cv2.COLOR_GRAY2BGR)
            
        # 前処理画像で検出を試みる
        value2, points2, straight_qrcode2 = qr_detector.detectAndDecode(pre_cv_image)
        if value2:
            logger.info(f"QRコードを前処理画像で検出: {value2[:30]}...")
            # テスト用に前処理画像を保存
            pre_image.save("output_qr_preprocessed.png")
            with open("output_report.txt", "a", encoding="utf-8") as f:
                f.write("前処理画像でQR検出成功\n")
            return value2
            
        # 3. 最後の試み：元画像を拡大して検出
        height, width = cv_image.shape[:2]
        resized = cv2.resize(cv_image, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
        value3, points3, straight_qrcode3 = qr_detector.detectAndDecode(resized)
        if value3:
            logger.info(f"QRコードを拡大画像で検出: {value3[:30]}...")
            return value3
            
        # 4. 失敗時のレポート
        pre_image.save("output_qr_preprocessed.png")
        with open("output_report.txt", "a", encoding="utf-8") as f:
            f.write("QRコード検出失敗\n")
        logger.info("QRコードは元画像・前処理画像・拡大画像ともに検出されませんでした")
        return None
    except Exception as e:
        logger.error(f"QRコードの読み取り中にエラーが発生しました: {str(e)}")
        return None

def detect_multiple_qr_codes(image: Image.Image) -> List[Dict[str, Any]]:
    """
    画像から複数のQRコードを検出する
    """
    try:
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        qr_detector = cv2.QRCodeDetector()
        value, points, straight_qrcode = qr_detector.detectAndDecodeMulti(cv_image)
        
        if not value:
            return []
            
        results = []
        for i, (v, p) in enumerate(zip(value, points)):
            if v:
                results.append({
                    'value': v,
                    'points': p.tolist(),
                    'index': i
                })
        return results
    except Exception as e:
        logger.error(f"複数QRコードの検出中にエラーが発生しました: {str(e)}")
        return []

def preprocess_image_for_qr(image: Image.Image) -> Image.Image:
    """
    QRコード検出用に画像を前処理する
    """
    try:
        # PIL画像をOpenCV形式に変換
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # グレースケール変換
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # ノイズ除去
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # コントラスト強調
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # 二値化
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # モルフォロジー処理
        kernel = np.ones((3,3), np.uint8)
        morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # OpenCV画像をPIL形式に戻す
        return Image.fromarray(morphed)
    except Exception as e:
        logger.error(f"画像の前処理中にエラーが発生しました: {str(e)}")
        return image

def is_sasaeai_url(text: str) -> bool:
    """
    テキストがささえあいのURLかどうかを判定する
    """
    pattern = r'https://sasaeai\.com/.*'
    return bool(re.match(pattern, text))

def extract_qr_info(qr_text: str) -> Dict[str, str]:
    """
    QRコードのテキストから情報を抽出する
    """
    try:
        if is_sasaeai_url(qr_text):
            return {
                'type': 'sasaeai',
                'url': qr_text
            }
        return {
            'type': 'unknown',
            'text': qr_text
        }
    except Exception as e:
        logger.error(f"QRコード情報の抽出中にエラーが発生しました: {str(e)}")
        return {
            'type': 'error',
            'error': str(e)
        }

def read_qr_from_image_with_fallback(pil_image: Image.Image) -> Optional[str]:
    """
    QRコードの読み取りを試み、失敗した場合は前処理を試行する
    """
    try:
        # まず通常の読み取りを試みる
        result = read_qr_from_image(pil_image)
        if result:
            return result
            
        # 前処理を試行
        preprocessed = preprocess_image_for_qr(pil_image)
        return read_qr_from_image(preprocessed)
    except Exception as e:
        logger.error(f"QRコードの読み取り（フォールバック）中にエラーが発生しました: {str(e)}")
        return None 