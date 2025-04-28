import pandas as pd
import io

def to_csv(df, encoding='utf-8'):
    """
    DataFrameをCSV形式に変換してダウンロード用のバイトストリームとして返す
    
    Args:
        df (pandas.DataFrame): 出力するデータフレーム
        encoding (str, optional): CSVのエンコーディング。デフォルトはUTF-8
    
    Returns:
        bytes: CSVデータのバイトストリーム
    """
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding=encoding)
    return csv_buffer.getvalue()

def to_excel(df):
    """
    DataFrameをExcel形式に変換してダウンロード用のバイトストリームとして返す
    
    Args:
        df (pandas.DataFrame): 出力するデータフレーム
    
    Returns:
        bytes: Excelデータのバイトストリーム
    """
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='名刺データ', index=False)
    
    excel_buffer.seek(0)
    return excel_buffer.getvalue()

def translate_keys_for_export(df):
    """
    日本語キーを英語キーに変換してエクスポート用のDataFrameを作成する
    
    Args:
        df (pandas.DataFrame): 日本語キーのデータフレーム
    
    Returns:
        pandas.DataFrame: 英語キーに変換されたデータフレーム
    """
    # 新しい空のDataFrameを作成
    export_df = pd.DataFrame()
    
    # 日本語キーから英語キーへの変換
    for jp_key, eng_key in KEY_MAPPING.items():
        if jp_key in df.columns:
            export_df[eng_key] = df[jp_key]
    
    # OUTPUT_KEYSの順序に合わせてカラムを並び替え
    ordered_columns = [col for col in OUTPUT_KEYS if col in export_df.columns]
    export_df = export_df[ordered_columns]
    
    return export_df
