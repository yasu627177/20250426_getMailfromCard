# 名刺OCRアプリ

名刺画像から情報を抽出し、整理して保存するWebアプリケーションです。

## 機能

- 名刺画像のアップロード
- OCRによるテキスト抽出
- Gemini AIによる情報の構造化
- 結果の表示（表形式）
- CSVファイルとしてのエクスポート

## データ項目

- 名前
- フリガナ
- 職業
- メールアドレス
- メールアドレス（予備）
- 電話番号
- 郵便番号
- 住所
- HP URL
- sasaeai URL
- その他

## 技術スタック

- フロントエンド: Streamlit
- OCR: pytesseract (Tesseract OCR)
- テキスト解析: Gemini API
- データ処理: pandas

## セットアップ手順

### 1. 必要なソフトウェアのインストール

**Tesseract OCR**のインストール:
- Windows: [インストーラ](https://github.com/UB-Mannheim/tesseract/wiki)からダウンロード
- Mac: `brew install tesseract tesseract-lang`
- Linux: `sudo apt install tesseract-ocr tesseract-ocr-jpn`

### 2. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境設定

1. `env_template.txt`を`.env`にコピーし、以下の設定を行います:
   - `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com/)から取得したAPIキー

### 4. アプリの起動

```bash
streamlit run app.py
```

## 使用方法

1. 名刺画像をアップロード
2. 「データ抽出」ボタンをクリック
3. 抽出結果を確認
4. 必要に応じてCSVダウンロードを実行

## 注意事項

- Tesseract OCRの精度は画像の品質に大きく依存します
- Gemini APIの利用にはクォータ制限があります

## 将来的な拡張予定

- 複数画像の一括処理
- 編集可能なテーブル表示
- タグ付け機能
- 検索・フィルター機能 