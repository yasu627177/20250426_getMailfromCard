"""
Gemini APIへのプロンプトを提供するモジュール
"""
from .constants import REQUIRED_KEYS, KEY_MAPPING

# デモデータの更新
DEMO_DATA = {
    "名前": "山田太郎",
    "会社名": "株式会社サンプル",
    "職業": "営業部長",
    "メールアドレス": "yamada@example.com",
    "電話番号": "03-1234-5678",
    "郵便番号": "100-0001",
    "住所": "東京都千代田区丸の内1-1-1",
    "HP URL": "https://www.example.com",
    "sasaeai URL": "",
    "その他": "備考情報等"
}

def get_gemini_prompt(ocr_text):
    """
    OCR抽出テキストを元にGemini APIへのプロンプトを生成する
    
    Args:
        ocr_text (str): OCRで抽出したテキスト
        
    Returns:
        str: Gemini APIへのプロンプト
    """
    # 必須キーの日本語名と英語名のマッピング説明を作成
    key_mapping_description = ""
    for jp_key, eng_key in KEY_MAPPING.items():
        key_mapping_description += f"- {jp_key} -> {eng_key}\n"
    
    prompt = f"""
あなたは名刺（ビジネスカード）の情報を抽出する専門アシスタントです。
OCRで抽出された以下のテキストから、人物情報を抽出してください。

###抽出するべき情報###
以下の情報を抽出してJSON形式で返してください：
{', '.join(REQUIRED_KEYS)}

###JSON出力形式###
以下のキーと完全に一致する1行のJSON形式で出力してください：
```
{{"名前": "山田太郎", "会社名": "株式会社サンプル", "職業": "営業部長", "メールアドレス": "yamada@example.com", "電話番号": "03-1234-5678", "郵便番号": "100-0001", "住所": "東京都千代田区丸の内1-1-1", "HP URL": "https://www.example.com", "sasaeai URL": "", "その他": "備考情報等"}}
```

###重要###
- 必ず完全に有効なJSON形式で出力してください。
- オブジェクトの前後に余分なテキスト、説明、マークダウンなどを含めないでください。
- 出力は単一行のJSONオブジェクトのみにしてください。
- キーの名前は上記の通り正確に使用してください。
- 抽出できない情報は空文字列""としてください。
- 日本語でも英語でも出力できますが、キー名は日本語で上記の通りにしてください。
- sasaeai URLは "https://sasaeai.link-platform.jp/" を含むURLです。
- その他の備考情報やメモ等はすべて「その他」フィールドにまとめてください。
- 予備のメールアドレスや電話番号、FAX等が見つかった場合は「その他」フィールドに含めてください。

###OCRテキスト###
{ocr_text}
"""
    return prompt 