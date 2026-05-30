# -*- coding: utf-8 -*-

from japanesformer.constants import VOWEL_GROUPS, CHAR_TO_GROUP
from japanesformer.text_utils import to_hiragana, to_katakana, is_katakana

def transform(text: str, shift: int, decrypt: bool = False, use_wave: bool = True) -> str:
    """
    日本語テキストの母音を固定したまま子音を循環変換（または復号）します。

    Args:
        text (str): 変換対象の日本語文字列。
        shift (int): 基礎となるシフト量（base_shift）。任意の非負整数。
        decrypt (bool): True の場合は復号化（逆方向シフト）、False の場合は暗号化。
        use_wave (bool): True の場合は位置依存の波状シフト（position_counter を加算）を適用。

    Returns:
        str: 変換後の文字列。
    """
    # 負のシフト量が指定された場合は、エラーにせず正数に正規化して扱います
    base_shift = int(shift)
    
    position_counter = 0
    result = []
    
    for char in text:
        # カタカナ対策のため、一時的にひらがなに変換して判定を行う
        hira = to_hiragana(char)
        
        # 文字がどの母音グループにも属さない（特殊文字、記号、英数字、小書き文字など）場合はそのまま透過
        if hira not in CHAR_TO_GROUP:
            result.append(char)
            continue
        
        # 所属グループとインデックスをO(1)で特定
        vowel, idx = CHAR_TO_GROUP[hira]
        group = VOWEL_GROUPS[vowel]
        group_len = len(group)
        
        # 現在のシフト量を計算（波状変換がオンの場合は出現位置に応じて加算）
        current_shift = (base_shift + position_counter) if use_wave else base_shift
        current_shift = current_shift % group_len
        
        if decrypt:
            # 復号時は逆方向にシフト
            new_idx = (idx - current_shift) % group_len
        else:
            # 暗号化時は正方向にシフト
            new_idx = (idx + current_shift) % group_len
            
        new_char = group[new_idx]
        
        # 元の文字がカタカナだった場合はカタカナに戻す
        if is_katakana(char):
            new_char = to_katakana(new_char)
            
        result.append(new_char)
        
        # 変換対象文字を処理した場合のみ、カウンターをインクリメント
        position_counter += 1
        
    return "".join(result)
