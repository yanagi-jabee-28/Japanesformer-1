# -*- coding: utf-8 -*-

import unicodedata

def to_hiragana(char: str) -> str:
    """
    指定された文字がカタカナの場合、ひらがなに変換します。
    """
    if len(char) != 1:
        return char
    code = ord(char)
    # カタカナのUnicode範囲（ァ U+30A1 から ヶ U+30F6）
    if 0x30A1 <= code <= 0x30F6:
        return chr(code - 0x60)
    return char

def to_katakana(char: str) -> str:
    """
    指定された文字がひらがなの場合、カタカナに変換します。
    """
    if len(char) != 1:
        return char
    code = ord(char)
    # ひらがなのUnicode範囲（ぁ U+3041 から ゖ U+3096）
    if 0x3041 <= code <= 0x3096:
        return chr(code + 0x60)
    return char

def is_katakana(char: str) -> bool:
    """
    指定された文字がカタカナかどうかを判定します。
    """
    if len(char) != 1:
        return False
    code = ord(char)
    return 0x30A1 <= code <= 0x30F6

def is_kanji(char: str) -> bool:
    """
    指定された文字が漢字かどうかを判定します。
    """
    if len(char) != 1:
        return False
    code = ord(char)
    return 0x4E00 <= code <= 0x9FFF

def is_hiragana(char: str) -> bool:
    """
    指定された文字がひらがなかどうかを判定します。
    """
    if len(char) != 1:
        return False
    code = ord(char)
    return 0x3041 <= code <= 0x3096

class TextNormalizer:
    """
    漢字・カタカナの前処理および、変換後の文字種（カタカナ等）の復元を管理するクラス。
    """
    def __init__(self):
        # pykakasi のインスタンスは必要に応じて遅延初期化します
        self._kakasi = None

    def _get_kakasi(self):
        if self._kakasi is None:
            import pykakasi
            self._kakasi = pykakasi.kakasi()
        return self._kakasi

    def normalize(self, text: str) -> list[dict]:
        """
        入力テキストを解析し、ひらがなに正規化した文字のリストと、元の文字種のメタデータを返します。
        """
        result = []
        try:
            # pykakasi を用いて漢字をひらがなに変換
            kakasi = self._get_kakasi()
            conversion = kakasi.convert(text)
            
            # pykakasi の変換結果（ひらがな化された単語）を1文字ずつ処理
            for item in conversion:
                orig = item['orig']
                hira_word = item['hira']
                
                # 単語の文字属性を分析
                has_kanji = any(is_kanji(c) for c in orig)
                all_katakana = all(is_katakana(c) or c == "ー" for c in orig)
                
                if has_kanji:
                    # 漢字を含む単語（例: '速い' -> 'はやい'）
                    # 末尾から一致する送り仮名（ひらがな）を判定し、属性を正しく分離します。
                    kanji_hira_len = len(hira_word)
                    orig_len = len(orig)
                    
                    matching_suffix_len = 0
                    while (matching_suffix_len < orig_len and 
                           matching_suffix_len < kanji_hira_len):
                        orig_char = orig[orig_len - 1 - matching_suffix_len]
                        hira_char = hira_word[kanji_hira_len - 1 - matching_suffix_len]
                        if orig_char == hira_char and is_hiragana(orig_char):
                            matching_suffix_len += 1
                        else:
                            break
                    
                    # 漢字部分（ひらがなに開かれたもの）は "kanji" と定義
                    kanji_part_hira = hira_word[:kanji_hira_len - matching_suffix_len]
                    for char in kanji_part_hira:
                        result.append({
                            "char": char,
                            "orig_type": "kanji"
                        })
                    
                    # 送り仮名部分は通常のひらがなまたは特殊文字として処理
                    suffix_part = hira_word[kanji_hira_len - matching_suffix_len:]
                    for char in suffix_part:
                        result.append({
                            "char": char,
                            "orig_type": "special" if char in "っんーゃゅょぁぃぅぇぉ" else "hiragana"
                        })
                elif all_katakana:
                    # カタカナのみで構成される単語は、ひらがな化した上で文字種 "katakana" を保持
                    for char in hira_word:
                        result.append({
                            "char": char,
                            "orig_type": "katakana"
                        })
                else:
                    # 通常のひらがな、またはその他の記号・英数字
                    for char in orig:
                        if char in "っんーゃゅょぁぃぅぇぉ":
                            result.append({
                                "char": char,
                                "orig_type": "special"
                            })
                        elif is_hiragana(char):
                            result.append({
                                "char": char,
                                "orig_type": "hiragana"
                            })
                        else:
                            result.append({
                                "char": char,
                                "orig_type": "special"
                            })
        except ImportError:
            # pykakasi がインストールされていない、またはフォールバック
            for char in text:
                if is_katakana(char):
                    result.append({
                        "char": to_hiragana(char),
                        "orig_type": "katakana"
                    })
                else:
                    result.append({
                        "char": char,
                        "orig_type": "hiragana" if char not in "っんーゃゅょぁぃぅぇぉ" else "special"
                    })
        return result

    def restore_types(self, converted_text: str, meta: list[dict]) -> str:
        """
        変換されたひらがなテキストに対し、元の文字種（カタカナ）を適用して復元します。
        """
        result_chars = []
        for char, info in zip(converted_text, meta):
            if info["orig_type"] == "katakana":
                result_chars.append(to_katakana(char))
            else:
                result_chars.append(char)
        return "".join(result_chars)
