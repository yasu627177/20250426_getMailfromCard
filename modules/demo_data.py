"""
デモデータを提供するモジュール
APIが利用できない、または解析に失敗した場合のフォールバックとして使用
"""

from .constants import DEMO_DATA

def get_demo_data():
    """
    デモデータを返す関数
    
    Returns:
        dict: サンプルの名刺データ
    """
    return DEMO_DATA.copy()  # 常に新しいコピーを返して元のデータが変更されないようにする 