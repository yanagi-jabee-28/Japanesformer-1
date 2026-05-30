# -*- coding: utf-8 -*-

import unittest
from japanesformer.text_utils import TextNormalizer, to_hiragana, to_katakana, is_katakana

class TestTextUtils(unittest.TestCase):
    """
    japanesformer.text_utils モジュールの単体テスト
    """

    def setUp(self):
        self.normalizer = TextNormalizer()

    def test_character_helpers(self):
        """
        文字変換ヘルパー関数が正しく動作することを検証します。
        """
        # 1. to_hiragana
        self.assertEqual(to_hiragana("ア"), "あ")
        self.assertEqual(to_hiragana("ア"), "あ")
        self.assertEqual(to_hiragana("あ"), "あ")
        self.assertEqual(to_hiragana("A"), "A")
        
        # 2. to_katakana
        self.assertEqual(to_katakana("あ"), "ア")
        self.assertEqual(to_katakana("ア"), "ア")
        self.assertEqual(to_katakana("A"), "A")
        
        # 3. is_katakana
        self.assertTrue(is_katakana("ア"))
        self.assertFalse(is_katakana("あ"))
        self.assertFalse(is_katakana("A"))

    def test_normalize_katakana(self):
        """
        カタカナ文字列がひらがなに正規化され、メタデータが正しく抽出されることを検証します。
        """
        text = "シンカンセン"
        meta = self.normalizer.normalize(text)
        
        # 全ての文字が "katakana" として認識されているか
        for item in meta:
            self.assertEqual(item["orig_type"], "katakana")
            
        # 正規化された文字がひらがなになっているか
        normalized_str = "".join([item["char"] for item in meta])
        self.assertEqual(normalized_str, "しんかんせん")

    def test_normalize_kanji(self):
        """
        漢字文字列が pykakasi によりひらがなに正規化され、漢字部分のメタデータが 'kanji' になることを検証します。
        """
        text = "新幹線が速い"
        meta = self.normalizer.normalize(text)
        
        # "新幹線" -> "しんかんせん" (kanji)
        # "が" -> "が" (hiragana)
        # "速" -> "はや" (kanji)
        # "い" -> "い" (hiragana)
        
        # 結果の文字列を確認
        normalized_str = "".join([item["char"] for item in meta])
        self.assertEqual(normalized_str, "しんかんせんがはやい")
        
        # 漢字部分の判定が 'kanji' になっているか
        # 最初の6文字（しんかんせん）は "kanji"
        for i in range(6):
            self.assertEqual(meta[i]["orig_type"], "kanji")
            
        # 7文字目（が）は "hiragana"
        self.assertEqual(meta[6]["orig_type"], "hiragana")
        
        # 8-9文字目（はや）は "kanji"
        self.assertEqual(meta[7]["orig_type"], "kanji")
        self.assertEqual(meta[8]["orig_type"], "kanji")
        
        # 10文字目（い）は "hiragana"
        self.assertEqual(meta[9]["orig_type"], "hiragana")

    def test_restore_types(self):
        """
        restore_types がメタデータに基づいて元の文字種（カタカナ）を正しく復元することを検証します。
        """
        original = "シンカンセンがハヤイ"
        meta = self.normalizer.normalize(original)
        
        # いったん適当なひらがな文字列にする
        # しんかんせんがはやい -> ちんたんへんぱがばり
        converted = "ちんたんへんぱがばり"
        
        # 復元処理
        restored = self.normalizer.restore_types(converted, meta)
        
        # 元の文字種（カタカナ）が維持され、カタカナになってほしい箇所が戻っているか
        # シンカンセンがハヤイ
        # 期待値: チンタンヘンぱガバリ （が->ぱ, はやい->がばり、カタカナ復元により チンタンヘンぱガバリ）
        self.assertEqual(restored, "チンタンヘンぱガバリ")

if __name__ == "__main__":
    unittest.main()
