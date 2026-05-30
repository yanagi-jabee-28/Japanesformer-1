# -*- coding: utf-8 -*-

import sys
from japanesformer import transform
from japanesformer.text_utils import TextNormalizer

def run_demo():
    print("==================================================")
    print("        Japanesformer デモンストレーション        ")
    print("==================================================")
    
    # Windowsの文字化け防止対策
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # 1. 基本的な変換（ひらがなのみ、base_shift=1、波状変換オン）
    print("\n--- 1. 基本的なひらがな変換 (base_shift=1, 波状オン) ---")
    original_hira = "しんかんせんがはやい"
    encrypted_hira = transform(original_hira, shift=1, decrypt=False, use_wave=True)
    decrypted_hira = transform(encrypted_hira, shift=1, decrypt=True, use_wave=True)
    
    print(f"入力テキスト: {original_hira}")
    print(f"暗号化結果  : {encrypted_hira}")
    print(f"復号化結果  : {decrypted_hira}")

    # 2. カタカナと特殊文字の透過・属性保持
    print("\n--- 2. カタカナと特殊文字・スペースの混在 ---")
    original_mixed = "シンカンセン！が、ハヤイ。"
    encrypted_mixed = transform(original_mixed, shift=1, decrypt=False, use_wave=True)
    decrypted_mixed = transform(encrypted_mixed, shift=1, decrypt=True, use_wave=True)
    
    print(f"入力テキスト: {original_mixed}")
    print(f"暗号化結果  : {encrypted_mixed}")
    print(f"復号化結果  : {decrypted_mixed}")

    # 3. 漢字の前処理モジュールを用いた暗号化・復号
    print("\n--- 3. 漢字の前処理と復号 (TextNormalizer 連携) ---")
    original_kanji = "新幹線が速い"
    normalizer = TextNormalizer()
    
    # 3-1. 前処理による正規化とメタデータ抽出
    meta = normalizer.normalize(original_kanji)
    normalized_text = "".join([item["char"] for item in meta])
    
    # 3-2. 暗号化
    encrypted_hira2 = transform(normalized_text, shift=1, decrypt=False, use_wave=True)
    encrypted_result = normalizer.restore_types(encrypted_hira2, meta)
    
    # 3-3. 復号化（暗号化テキストを再度正規化し、元のメタデータを適用して復号）
    meta_dec = normalizer.normalize(encrypted_result)
    normalized_dec_text = "".join([item["char"] for item in meta_dec])
    decrypted_hira2 = transform(normalized_dec_text, shift=1, decrypt=True, use_wave=True)
    decrypted_result = normalizer.restore_types(decrypted_hira2, meta_dec)
    
    print(f"入力テキスト (漢字): {original_kanji}")
    print(f"ひらがな正規化結果 : {normalized_text}")
    print(f"暗号化結果 (外観)  : {encrypted_result}")
    print(f"復号化結果 (読み)  : {decrypted_result}  ※仕様上、表記はひらがな(読み)になります")

    # 4. 波状変換の有無による違い
    print("\n--- 4. 波状変換 (use_wave=False vs True) ---")
    original_repeat = "あああああ"
    # 波状変換なし（すべての「あ」が同じ文字にシフト）
    no_wave_encrypted = transform(original_repeat, shift=1, decrypt=False, use_wave=False)
    # 波状変換あり（出現位置によってシフト量が増えるため、連続文字が回避される）
    wave_encrypted = transform(original_repeat, shift=1, decrypt=False, use_wave=True)
    
    print(f"入力テキスト           : {original_repeat}")
    print(f"波状変換オフ (固定)    : {no_wave_encrypted}")
    print(f"波状変換オン (位置依存): {wave_encrypted}")

if __name__ == "__main__":
    run_demo()
