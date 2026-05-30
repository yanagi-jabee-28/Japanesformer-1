# -*- coding: utf-8 -*-

import unittest
import random
from japanesformer import transform
from japanesformer.text_utils import TextNormalizer
from japanesformer.constants import VOWEL_GROUPS

class TestRoundtrip(unittest.TestCase):
    """
    システムの全単射性（可逆性）を検証するための統合ラウンドトリップテスト
    """

    def setUp(self):
        self.normalizer = TextNormalizer()
        
        # テスト文字プールを作成
        # ひらがな、カタカナ、透過文字、数字、アルファベット、記号
        self.hiragana_pool = []
        for chars in VOWEL_GROUPS.values():
            self.hiragana_pool.extend(chars)
            
        # カタカナプール
        self.katakana_pool = [chr(ord(c) + 0x60) for c in self.hiragana_pool if 0x3041 <= ord(c) <= 0x3096]
        
        # 特殊文字、記号、英数字プール
        self.special_pool = list("っんーゃゅょぁぃぅぇぉ !?123ABCabc　\n")
        
        # すべての文字をマージしたプール
        self.all_pool = self.hiragana_pool + self.katakana_pool + self.special_pool

    def _generate_random_sentence(self, length):
        """
        ランダムな文字列（ひらがな、カタカナ、特殊文字の混合）を生成します。
        """
        return "".join(random.choice(self.all_pool) for _ in range(length))

    def test_random_hiragana_katakana_roundtrip(self):
        """
        ランダムに生成されたひらがな・カタカナ交じり文に対し、
        様々なシフト量で 暗号化 -> 復号化 を行い、完全に元に戻ることを1000パターンで検証します。
        """
        random.seed(42)  # 再現性のためのシード固定
        
        for i in range(1000):
            # 長さは5から100文字
            length = random.randint(5, 100)
            original = self._generate_random_sentence(length)
            
            # シフト量は0から100
            shift = random.randint(0, 100)
            use_wave = random.choice([True, False])
            
            with self.subTest(i=i, length=length, shift=shift, use_wave=use_wave):
                # 1. 暗号化
                encrypted = transform(original, shift=shift, decrypt=False, use_wave=use_wave)
                
                # 2. 復号化
                decrypted = transform(encrypted, shift=shift, decrypt=True, use_wave=use_wave)
                
                # 3. アサーション
                self.assertEqual(decrypted, original)

    def test_kanji_normalization_roundtrip(self):
        """
        漢字を含む入力に対して、暗号化 -> 復号化を行った際、
        漢字がひらがな（読み）になった状態で正しく復元されることを検証します。
        （表記レベルは非対称だが、情報・意味レベルで可逆であることを確認）
        """
        original = "吾輩は猫である。名前はまだ無い。"
        
        # 漢字をあらかじめひらがなに開いた期待値の復号結果
        # 「わがはいはねこである。なまえはまだない。」
        # 吾輩 -> わがはい, 猫 -> ねこ, 名前 -> なまえ, 無い -> ない
        expected_decrypted = "わがはいはねこである。なまえはまだない。"
        
        # 1. 前処理による正規化と文字種抽出
        meta = self.normalizer.normalize(original)
        normalized_text = "".join([item["char"] for item in meta])
        
        # 2. 暗号化
        encrypted_hira = transform(normalized_text, shift=3, decrypt=False, use_wave=True)
        encrypted = self.normalizer.restore_types(encrypted_hira, meta)
        
        # 3. 復号化
        meta_dec = self.normalizer.normalize(encrypted)
        normalized_dec_text = "".join([item["char"] for item in meta_dec])
        decrypted_hira = transform(normalized_dec_text, shift=3, decrypt=True, use_wave=True)
        decrypted = self.normalizer.restore_types(decrypted_hira, meta_dec)
        
        # 4. 検証（漢字部分がひらがな（読み）の状態で戻る）
        self.assertEqual(decrypted, expected_decrypted)

if __name__ == "__main__":
    unittest.main()
