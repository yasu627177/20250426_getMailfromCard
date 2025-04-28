import json
import os
import re
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from .prompts import get_gemini_prompt
from .constants import COLUMNS, REQUIRED_KEYS, DEMO_DATA, KEY_MAPPING, GEMINI_MODEL
from .demo_data import get_demo_data

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()

# 環境変数の読み込み状況をログに出力
logger.info(f"環境変数の読み込み: .env ファイルのパス: {os.path.abspath('.env') if os.path.exists('.env') else '.env ファイルが見つかりません'}")
logger.info(f"現在の作業ディレクトリ: {os.getcwd()}")

# Gemini APIの設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# .envファイルを直接読み込む（環境変数が見つからない場合）
if not GEMINI_API_KEY and os.path.exists('.env'):
    try:
        logger.info("環境変数から読み込めないため、.envファイルを直接読み込みます")
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
                    if key == 'GEMINI_API_KEY':
                        GEMINI_API_KEY = value
                        logger.info("GEMINI_API_KEYを.envファイルから直接読み込みました")
                        break
    except Exception as e:
        logger.error(f".envファイルの直接読み込みエラー: {e}")

# API キーが設定されているかチェック
if not GEMINI_API_KEY:
    error_msg = "GEMINI_API_KEYが設定されていません。.envファイルで設定してください。"
    logger.error(error_msg)
    raise ValueError(error_msg)

logger.info(f"GEMINI_API_KEY の設定状況: {'設定済み' if GEMINI_API_KEY else '未設定'}")
MODEL_NAME = GEMINI_MODEL  # constants.pyで定義された環境変数から読み取ったモデル名を使用
logger.info(f"使用するモデル: {MODEL_NAME}")

def configure_genai():
    """
    Google Generative AI APIの設定
    """
    if not GEMINI_API_KEY:
        error_msg = "GEMINI_API_KEYが設定されていません"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except Exception as e:
        error_msg = f"Gemini APIの設定に失敗しました: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

def parse_text(ocr_text):
    """
    OCRで抽出したテキストをパースしてデータを返す
    
    Args:
        ocr_text (str): OCRで抽出したテキスト
        
    Returns:
        dict: 抽出したデータ
    """
    logger.info("テキストの解析を開始")
    
    # APIの設定
    configure_genai()
    
    try:
        # プロンプトの作成
        prompt = get_gemini_prompt(ocr_text)
        logger.debug(f"生成したプロンプト: {prompt[:100]}...")
        
        # モデルの設定 - JSON modeを有効化
        generation_config = {
            "temperature": 0.1,  # 低温度で厳密な応答を得る
            "top_p": 0.8,
            "top_k": 40
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        
        # APIリクエスト
        try:
            model = genai.GenerativeModel(
                MODEL_NAME,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            logger.info(f"Gemini APIのレスポンス受信: {len(response_text)}文字")
            logger.debug(f"レスポンス: {response_text}")
            
            # JSONレスポンスのクリーニング
            # バッククォートやマークダウン記法の削除
            if "```" in response_text:
                # コードブロックから抽出
                cleaned_text = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
                if cleaned_text:
                    response_text = cleaned_text.group(1).strip()
                    logger.info("コードブロックからJSONを抽出しました")
            
            # JSONブロックの抽出（{...}で囲まれた部分）
            json_match = re.search(r'({.*})', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1).strip()
                logger.info("JSONブロックを抽出しました")
            
            response_text = response_text.strip()
        except Exception as e:
            error_msg = f"API呼び出しエラー: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # レスポンスのパース
        try:
            # 直接JSONをパース
            parsed_data = json.loads(response_text)
            logger.info("JSONとして直接パースに成功")
        except json.JSONDecodeError as e:
            logger.warning(f"JSONパースエラー: {e}")
            logger.warning("JSONパースに失敗、クリーニングと再パースを試みます")
            
            # JSON形式に変換するためのクリーニング
            cleaned_text = response_text
            
            # シングルクォートをダブルクォートに変換
            cleaned_text = re.sub(r"'([^']*)'(?=\s*:)", r'"\1"', cleaned_text)
            
            # 前後の余分なテキストを削除
            cleaned_text = re.sub(r'^[^{]*', '', cleaned_text)  # 先頭の不要なテキスト
            cleaned_text = re.sub(r'[^}]*$', '', cleaned_text)  # 末尾の不要なテキスト
            
            # JSONのキーと値を適切にフォーマット
            # キーをダブルクォートで囲む
            cleaned_text = re.sub(r'([{,])\s*([a-zA-Z0-9_\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+)\s*:', r'\1"\2":', cleaned_text)
            
            # エスケープされていないダブルクォートの処理
            cleaned_text = re.sub(r':\s*"([^"]*)"(?=[,}])', r':"\1"', cleaned_text)
            
            logger.debug(f"クリーニング後のテキスト: {cleaned_text}")
            
            try:
                parsed_data = json.loads(cleaned_text)
                logger.info("クリーニング後のJSONパースに成功")
            except json.JSONDecodeError as e2:
                error_msg = f"クリーニング後もJSONパースに失敗: {e2}"
                logger.error(error_msg)
                
                # 最終手段: 正規表現でキーと値のペアを抽出
                try:
                    # キーと値のペアを抽出
                    pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', cleaned_text)
                    if pairs:
                        parsed_data = {k: v for k, v in pairs}
                        logger.info("正規表現によるキーと値のペア抽出に成功")
                    else:
                        error_msg = "キーと値のペア抽出に失敗"
                        logger.error(error_msg)
                        raise RuntimeError(error_msg)
                except Exception as e3:
                    error_msg = f"正規表現によるパースに失敗: {e3}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
        
        # レスポンスデータのキーチェックと補完
        result = {}
        
        # 英語キーで返ってきた場合は日本語キーにマッピング
        if "name" in parsed_data:
            # 英語キーでのレスポンス
            reversed_mapping = {v: k for k, v in KEY_MAPPING.items()}
            for eng_key, jp_key in reversed_mapping.items():
                if eng_key in parsed_data:
                    result[jp_key] = parsed_data[eng_key]
        else:
            # 日本語キーでのレスポンス
            result = parsed_data
        
        # 旧フィールド（フィールド1～フィールド5、メモ）をその他にまとめる
        old_fields = ["フィールド1", "フィールド2", "フィールド3", "フィールド4", "フィールド5", "メモ"]
        other_content = []
        
        for field in old_fields:
            if field in parsed_data and parsed_data[field]:
                if field == "メモ":
                    other_content.append(f"{parsed_data[field]}")
                else:
                    other_content.append(f"{field}: {parsed_data[field]}")
        
        # すでに「その他」フィールドが存在する場合は、そのコンテンツも追加
        if "その他" in parsed_data and parsed_data["その他"]:
            other_content.append(parsed_data["その他"])
        
        # 「その他」フィールドを設定
        if other_content:
            result["その他"] = " / ".join(other_content)
        else:
            result["その他"] = ""
        
        # 必須キーの存在確認と欠損値の補完
        for key in REQUIRED_KEYS:
            if key not in result:
                result[key] = ""
        
        logger.info("テキストの解析が完了")
        return result
        
    except Exception as e:
        error_msg = f"テキスト解析中にエラーが発生: {e}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg)

def extract_contact_info(text):
    """
    テキストから連絡先情報を抽出する補助関数
    
    Args:
        text (str): 解析するテキスト
        
    Returns:
        tuple: (emails, phones, urls)
    """
    # メールアドレスの抽出
    email_pattern = r'[a-zA-Z0-9_.+-]+[@＠][a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+' 
    emails = re.findall(email_pattern, text)
    
    # 電話番号の抽出
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}'
    phones = re.findall(phone_pattern, text)
    
    # URLの抽出
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    urls = re.findall(url_pattern, text)
    
    return emails, phones, urls 