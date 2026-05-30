# -*- coding: utf-8 -*-

import unittest
from japanesformer import transform

class TestCoreTransform(unittest.TestCase):
    """
    japanesformer.core モジュールの transform 関数に関する単体テスト
    """

    def test_identity_transform(self):
        """
        base_shift=0、かつ波状変換オフの場合、文字列が変化しない（恒等変換）ことを検証します。
        """
        inputs = [
            "しんかんせんがはやい",
            "あいうえお",
            "カキクケコ",
            "こんにちは、世界！ 123",
        ]
        for text in inputs:
            with self.subTest(text=text):
                encrypted = transform(text, shift=0, decrypt=False, use_wave=False)
                self.assertEqual(encrypted, text)
                decrypted = transform(encrypted, shift=0, decrypt=True, use_wave=False)
                self.assertEqual(decrypted, text)

    def test_basic_transform_wave(self):
        """
        base_shift=1、波状変換オンでの基本変換を検証します。
        """
        original = "しんかんせんがはやい"
        expected_encrypted = "ちんたんへんぱがばり"
        
        # 1. 暗号化の検証
        encrypted = transform(original, shift=1, decrypt=False, use_wave=True)
        self.assertEqual(encrypted, expected_encrypted)
        
        # 2. 復号化の検証（元に戻るか）
        decrypted = transform(encrypted, shift=1, decrypt=True, use_wave=True)
        self.assertEqual(decrypted, original)

    def test_basic_transform_no_wave(self):
        """
        base_shift=1、波状変換オフでの基本変換を検証します（固定シフト）。
        """
        original = "あかさたな"
        # 各母音グループ A でインデックスが 1 ずつ右にシフトする
        # あ(0)->か(1), か(1)->さ(2), さ(2)->た(3), た(3)->な(4), な(4)->は(5)
        # 期待値: "かさたなは"
        expected = "かさたなは"
        
        encrypted = transform(original, shift=1, decrypt=False, use_wave=False)
        self.assertEqual(encrypted, expected)
        
        decrypted = transform(encrypted, shift=1, decrypt=True, use_wave=False)
        self.assertEqual(decrypted, original)

    def test_katakana_preservation(self):
        """
        カタカナが変換されつつ、カタカナの属性が維持されることを検証します。
        """
        original = "シンカンセンがハヤイ"
        # 'しんかんせんがはやい' が 'ちんたんへんぱがばり' になるので、
        # カタカナの部分がカタカナで維持されれば 'チンタンヘンぱガバリ' になるはず
        expected_encrypted = "チンタンヘンぱガバリ"
        
        encrypted = transform(original, shift=1, decrypt=False, use_wave=True)
        self.assertEqual(encrypted, expected_encrypted)
        
        decrypted = transform(encrypted, shift=1, decrypt=True, use_wave=True)
        self.assertEqual(decrypted, original)

    def test_special_chars_transparency(self):
        """
        記号、数字、アルファベット、空白などの特殊文字が変換されずに透過し、
        かつ position_counter のインクリメントに影響しない（全単射が崩れない）ことを検証します。
        """
        # "し"、"ん"（透過）、"か"、"ん"（透過）、"せ"、"ん"（透過）、"が"、"は"、"や"、"い"
        # 途中にスペースや記号を挟んでも、カウントの同期が取れて正しく暗号化・復号できるか
        original = "しん！かん？せん   が はやい"
        
        encrypted = transform(original, shift=1, decrypt=False, use_wave=True)
        # 期待値:
        # "し" -> "ち"
        # "ん！" -> "ん！"
        # "か" -> "た" (counter=1)
        # "ん？" -> "ん？"
        # "せ" -> "へ" (counter=2)
        # "ん   " -> "ん   "
        # "が" -> "ぱ" (counter=3)
        # " " -> " "
        # "は" -> "が" (counter=4)
        # "や" -> "ば" (counter=5)
        # "い" -> "り" (counter=6)
        # 結果: "ちん！たん？へん   ぱ がばり"
        expected_encrypted = "ちん！たん？へん   ぱ がばり"
        self.assertEqual(encrypted, expected_encrypted)
        
        decrypted = transform(encrypted, shift=1, decrypt=True, use_wave=True)
        self.assertEqual(decrypted, original)

if __name__ == "__main__":
    unittest.main()
