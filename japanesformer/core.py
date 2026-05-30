# -*- coding: utf-8 -*-

from japanesformer.constants import VOWEL_GROUPS, CHAR_TO_GROUP
from japanesformer.text_utils import to_hiragana, to_katakana, is_katakana

def transform(text: str, shift: int, decrypt: bool = False, use_wave: bool = True) -> str:
    """
    日本語テキストの母音を固定したまま子音を循環変換し、
    同時に英数字（A-Z, a-z, 0-9）に対して独立したシーザー暗号を適用します。

    Args:
        text (str): 変換対象の文字列。
        shift (int): 基礎となるシフト量（base_shift）。任意の非負整数。
        decrypt (bool): True の場合は復号化（逆方向シフト）、False の場合は暗号化。
        use_wave (bool): True の場合は位置依存の波状シフト（position_counter を加算）を適用。

    Returns:
        str: 変換後の文字列。
    """
    base_shift = int(shift)
    position_counter = 0
    result = []
    
    for char in text:
        # 現在のシフト量を計算（波状変換がオンの場合は出現位置に応じて加算）
        current_shift = (base_shift + position_counter) if use_wave else base_shift
        
        # 1. アルファベット小文字 (a-z) のシーザー暗号処理
        if 'a' <= char <= 'z':
            idx = ord(char) - ord('a')
            if decrypt:
                new_idx = (idx - current_shift) % 26
            else:
                new_idx = (idx + current_shift) % 26
            result.append(chr(ord('a') + new_idx))
            position_counter += 1
            continue
            
        # 2. アルファベット大文字 (A-Z) のシーザー暗号処理
        if 'A' <= char <= 'Z':
            idx = ord(char) - ord('A')
            if decrypt:
                new_idx = (idx - current_shift) % 26
            else:
                new_idx = (idx + current_shift) % 26
            result.append(chr(ord('A') + new_idx))
            position_counter += 1
            continue
            
        # 3. 数字 (0-9) のシーザー暗号処理
        if '0' <= char <= '9':
            idx = ord(char) - ord('0')
            if decrypt:
                new_idx = (idx - current_shift) % 10
            else:
                new_idx = (idx + current_shift) % 10
            result.append(chr(ord('0') + new_idx))
            position_counter += 1
            continue

        # 4. 日本語（かな・カナ）の変換処理
        hira = to_hiragana(char)
        
        # どの母音グループにも属さない透過文字（記号、空白、っ、ん等）はそのまま出力
        if hira not in CHAR_TO_GROUP:
            result.append(char)
            continue
        
        vowel, idx = CHAR_TO_GROUP[hira]
        group = VOWEL_GROUPS[vowel]
        group_len = len(group)
        
        actual_shift = current_shift % group_len
        
        if decrypt:
            new_idx = (idx - actual_shift) % group_len
        else:
            new_idx = (idx + actual_shift) % group_len
            
        new_char = group[new_idx]
        
        # カタカナ属性の維持・復元
        if is_katakana(char):
            new_char = to_katakana(new_char)
            
        result.append(new_char)
        position_counter += 1
        
    return "".join(result)
