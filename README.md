# 名刺OCRアプリ

名刺画像から情報を抽出し、整理して保存するWebアプリケーションです。

## 機能

- 名刺画像のアップロード
- OCRによるテキスト抽出
- OpenCVによるQRコード検出・読み取り（警告抑制機能付き）
- Gemini AIによる情報の構造化（OCRテキストとQRコード情報の統合）
- 抽出データの編集機能（インライン編集可能なテーブル）
- 結果の表示（表形式）
- CSVファイルとしてのエクスポート

## データ項目

- 名前
- 会社名
- 職業
- メールアドレス
- 電話番号
- 郵便番号
- 住所
- HP URL
- sasaeai URL（QRコードから自動検出）
- その他

## 技術スタック

- フロントエンド: Streamlit
- OCR: pytesseract (Tesseract OCR)
- QRコード検出: OpenCV QRCodeDetector（警告抑制機能付き）
- テキスト解析: Gemini API
- データ処理: pandas
- データ編集: Streamlit Data Editor

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

1. 名刺画像をアップロード（QRコードを含む画像の場合は自動的に検出）
2. 「データ抽出」ボタンをクリック
3. 抽出結果を確認（OCRテキストとQRコード情報の両方が表示）
4. テーブル内のデータを直接編集（各セルをクリックして編集可能）
5. 「データを保存」ボタンをクリックして編集結果を保存
6. 必要に応じてCSVダウンロードを実行

## 注意事項

- Tesseract OCRの精度は画像の品質に大きく依存します
- QRコード検出はOpenCVの機能を使用し、警告メッセージは自動的に抑制されます
- 一部のQRコードタイプでは認識精度が異なる場合があります
- Gemini APIの利用にはクォータ制限があります
- 名前フィールドは必須項目として設定されています

## 将来的な拡張予定

- 複数画像の一括処理
- タグ付け機能
- 検索・フィルター機能
- 複数QRコードの同時検出対応
- 編集履歴の保存と復元機能 