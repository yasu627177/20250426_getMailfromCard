import pandas as pd
import io
from .constants import LEGACY_FIELDS

def process_legacy_fields(df):
    """
    繝ｬ繧ｬ繧ｷ繝ｼ繝輔ぅ繝ｼ繝ｫ繝会ｼ医ヵ繧｣繝ｼ繝ｫ繝・縲・・峨ｒ繝｡繝｢繝輔ぅ繝ｼ繝ｫ繝峨↓繝槭・繧ｸ縺吶ｋ
    
    Args:
        df (pandas.DataFrame): 蜃ｦ逅・☆繧九ョ繝ｼ繧ｿ繝輔Ξ繝ｼ繝
    
    Returns:
        pandas.DataFrame: 蜃ｦ逅・ｾ後・繝・・繧ｿ繝輔Ξ繝ｼ繝
    """
    # 繝ｬ繧ｬ繧ｷ繝ｼ繝輔ぅ繝ｼ繝ｫ繝峨′蜷ｫ縺ｾ繧後※縺・ｋ縺狗｢ｺ隱・
    legacy_fields_present = any(field in df.columns for field in LEGACY_FIELDS)
    
    if not legacy_fields_present:
        # 繝ｬ繧ｬ繧ｷ繝ｼ繝輔ぅ繝ｼ繝ｫ繝峨′縺ｪ縺代ｌ縺ｰ縺昴・縺ｾ縺ｾ霑斐☆
        return df
    
    # 繧ｳ繝斐・繧剃ｽ懈・
    result_df = df.copy()
    
    # 蜷・｡後↓蟇ｾ縺励※蜃ｦ逅・
    for idx, row in result_df.iterrows():
        memo_parts = []
        
        # 譌｢蟄倥・繝｡繝｢縺後≠繧後・霑ｽ蜉
        if '繝｡繝｢' in row and pd.notna(row['繝｡繝｢']) and row['繝｡繝｢']:
            memo_parts.append(str(row['繝｡繝｢']))
        
        # 繝ｬ繧ｬ繧ｷ繝ｼ繝輔ぅ繝ｼ繝ｫ繝峨・蛟､繧定ｿｽ蜉
        for field in LEGACY_FIELDS:
            if field in row and pd.notna(row[field]) and row[field]:
                memo_parts.append(f"{field}: {row[field]}")
        
        # 繝｡繝｢繝輔ぅ繝ｼ繝ｫ繝峨ｒ譖ｴ譁ｰ
        if memo_parts:
            result_df.at[idx, '繝｡繝｢'] = '\n'.join(memo_parts)
        
        # 繝ｬ繧ｬ繧ｷ繝ｼ繝輔ぅ繝ｼ繝ｫ繝峨ｒ蜑企勁
        for field in LEGACY_FIELDS:
            if field in result_df.columns:
                result_df = result_df.drop(columns=[field])
    
    return result_df

def to_csv(df, encoding='utf-8'):
    """
    DataFrame繧辰SV蠖｢蠑上↓螟画鋤縺励※繝繧ｦ繝ｳ繝ｭ繝ｼ繝臥畑縺ｮ繝舌う繝医せ繝医Μ繝ｼ繝縺ｨ縺励※霑斐☆
    
    Args:
        df (pandas.DataFrame): 蜃ｺ蜉帙☆繧九ョ繝ｼ繧ｿ繝輔Ξ繝ｼ繝
        encoding (str, optional): CSV縺ｮ繧ｨ繝ｳ繧ｳ繝ｼ繝・ぅ繝ｳ繧ｰ縲ゅョ繝輔か繝ｫ繝医・UTF-8
    
    Returns:
        bytes: CSV繝・・繧ｿ縺ｮ繝舌う繝医せ繝医Μ繝ｼ繝
    """
    # 繝ｬ繧ｬ繧ｷ繝ｼ繝輔ぅ繝ｼ繝ｫ繝峨・蜃ｦ逅・
    processed_df = process_legacy_fields(df)
    
    csv_buffer = io.StringIO()
    processed_df.to_csv(csv_buffer, index=False, encoding=encoding)
    return csv_buffer.getvalue()
