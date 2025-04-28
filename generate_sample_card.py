import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# サンプルディレクトリの作成
SAMPLES_DIR = 'samples'
os.makedirs(SAMPLES_DIR, exist_ok=True)

def create_sample_card(filename, name, company, position, address, phone, email, website, is_jp=True):
    """
    サンプル名刺を生成して保存する
    
    Args:
        filename (str): 保存するファイル名
        name (str): 名前
        company (str): 会社名
        position (str): 役職
        address (str): 住所
        phone (str): 電話番号
        email (str): メールアドレス
        website (str): ウェブサイト
        is_jp (bool): 日本語かどうか
    """
    # 名刺サイズ (91mm x 55mm at 300dpi)
    width, height = 1075, 650
    # 背景色（白）
    background = (255, 255, 255)
    # テキスト色（黒）
    text_color = (0, 0, 0)
    
    # 名刺イメージを作成
    img = Image.new('RGB', (width, height), color=background)
    draw = ImageDraw.Draw(img)
    
    # フォント選択
    # 注意: フォントファイルはシステムにインストールされたものを使用
    try:
        if is_jp:
            name_font = ImageFont.truetype('msgothic.ttc', 40)
            company_font = ImageFont.truetype('msgothic.ttc', 36)
            detail_font = ImageFont.truetype('msgothic.ttc', 24)
        else:
            name_font = ImageFont.truetype('arial.ttf', 40)
            company_font = ImageFont.truetype('arial.ttf', 36)
            detail_font = ImageFont.truetype('arial.ttf', 24)
    except IOError:
        # フォントが見つからない場合はデフォルトフォントを使用
        name_font = ImageFont.load_default()
        company_font = ImageFont.load_default()
        detail_font = ImageFont.load_default()
    
    # 会社ロゴ（単純な長方形として描画）
    draw.rectangle([(40, 40), (200, 90)], fill=(200, 200, 200))
    
    # 情報を描画
    draw.text((40, 120), company, font=company_font, fill=text_color)
    draw.text((40, 180), name, font=name_font, fill=text_color)
    draw.text((40, 240), position, font=detail_font, fill=text_color)
    draw.text((40, 300), address, font=detail_font, fill=text_color)
    draw.text((40, 360), f"TEL: {phone}", font=detail_font, fill=text_color)
    draw.text((40, 400), f"Email: {email}", font=detail_font, fill=text_color)
    draw.text((40, 440), website, font=detail_font, fill=text_color)
    
    # 名刺の枠線を描画
    draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 200, 200))
    
    # 画像を保存
    img.save(os.path.join(SAMPLES_DIR, filename))
    print(f"サンプル名刺を保存しました: {filename}")

# 日本語サンプル名刺
create_sample_card(
    'japanese_card.png',
    '山田 太郎',
    '株式会社サンプルテクノロジー',
    '取締役 技術部長',
    '東京都千代田区丸の内1-1-1 サンプルビル8F',
    '03-1234-5678',
    'yamada@example.com',
    'https://www.example.com',
    is_jp=True
)

# 英語サンプル名刺
create_sample_card(
    'english_card.png',
    'John Smith',
    'ACME Corporation',
    'Senior Sales Manager',
    '123 Main Street, New York, NY 10001',
    '+1 (212) 555-1234',
    'john.smith@acme.com',
    'https://www.acme.com',
    is_jp=False
)

print("サンプル名刺の生成が完了しました。") 