# Japanesformer

**Japanesformer**（ジャパニーズフォーマー）は、日本語の母音を固定したまま子音のみを循環させることで、元のリズム（音節数と母音構造）を完全に維持しつつ、直感的な意味を不可視化（暗号化）する可逆変換ライブラリです。

---

## 🌐 Webアプリで今すぐ遊ぶ

スマートフォンやPCのブラウザから、インストール不要で今すぐ体験できます。

👉 **[Japanesformer WebApp を起動する](https://yanagi-jabee-28.github.io/Japanesformer-1/)**

---

## 🌟 主な特徴

1. **母音固定（音韻・リズムの維持）**: あ・い・う・え・おの各母音は変換前後で不変。元の日本語文のリズムがそのまま保持されます。
2. **位置依存の波状シフト（Pattern Avoidance）**: 同じ文字の連続によるパターン解析を防ぐため、変換対象文字の出現順にシフト量を動的に増やします（波状変換）。
3. **前処理モジュール搭載（漢字・カタカナ対応）**: `pykakasi` 連携により、漢字交じり文も自動的にひらがなに開いて暗号化・復号が可能。カタカナ属性も維持・復元されます。
4. **数学的・全単射の保証**: どのような複雑な文字・空白・記号の組み合わせでも、全く同一のパラメータ（`base_shift`）によって一意に元の文字列（読みレベル）へと復号できます。

---

## 🛠 インストール

プロジェクトのルートディレクトリで以下のコマンドを実行します。

```bash
# 依存ライブラリ (pykakasi) のインストール
pip install -r requirements.txt

# ローカルパッケージとしてのインストール
pip install -e .
```

---

## 📖 変換ルールとアルゴリズム

### 1. 文字グループ定義（最終版）
同じ母音を持つ清音・濁音・半濁音をまとめたグループ内で循環シフトします。

- **グループ A（母音 a）- 15文字**:  
  `あ, か, さ, た, な, は, ま, や, ら, わ, が, ざ, だ, ば, ぱ`
- **グループ I（母音 i）- 13文字**:  
  `い, き, し, ち, に, ひ, mi, り, ぎ, じ, ぢ, び, ぴ`
- **グループ U（母音 u）- 14文字**:  
  `う, く, す, つ, ぬ, ふ, む, ゆ, る, ぐ, ず, づ, ぶ, ぷ`
- **グループ E（母音 e）- 13文字**:  
  `え, け, せ, て, ね, へ, め, れ, げ, ぜ, で, べ, ぺ`
- **グループ O（母音 o）- 15文字**:  
  `お, こ, そ, と, の, ほ, も, よ, ろ, を, ご, ぞ, ど, ぼ, ぽ`

### 2. 特殊文字の透過
促音「っ」、撥音「ん」、長音「ー」、小書き拗音（ゃ、ゅ、ょ）、小書き母音（ぁ、ぃ、ぅ、ぇ、ぉ）、および記号、数字、アルファベット、空白は一切変換されずに透過します。  
※透過された文字は出現位置カウンター（`position_counter`）を加算しないため、暗号化と復号化で同期がズレません。

---

## 🚀 使い方

### 1. Python API

```python
from japanesformer import transform
from japanesformer.text_utils import TextNormalizer

# --- ひらがな単体のシンプルな変換 ---
original = "しんかんせんがはやい"

# 暗号化 (shift=1, 波状変換オン)
# 結果: "ちんたんへんぱがばり"
encrypted = transform(original, shift=1, decrypt=False, use_wave=True)
print(f"暗号文: {encrypted}")

# 復号化
decrypted = transform(encrypted, shift=1, decrypt=True, use_wave=True)
print(f"復号文: {decrypted}")


# --- 漢字・カタカナ交じり文の変換 (TextNormalizer 連携) ---
normalizer = TextNormalizer()
text = "新幹線が速い！"

# 1. ひらがなへ正規化し、元の文字種メタデータを抽出
meta = normalizer.normalize(text)
normalized_text = "".join([item["char"] for item in meta])

# 2. 暗号化コア実行と文字種（カタカナ等）の復元
encrypted_hira = transform(normalized_text, shift=1, use_wave=True)
encrypted_result = normalizer.restore_types(encrypted_hira, meta)
print(f"漢字暗号化: {encrypted_result}") # 結果: チンタンヘンぱガバリ！

# 3. 復号処理
meta_dec = normalizer.normalize(encrypted_result)
normalized_dec = "".join([item["char"] for item in meta_dec])
decrypted_hira = transform(normalized_dec, shift=1, decrypt=True, use_wave=True)
decrypted_result = normalizer.restore_types(decrypted_hira, meta_dec)
print(f"復号化結果: {decrypted_result}") # 結果: しんかんせんがはやい！ (表記は読みのひらがな)
```

### 2. CLI（コマンドラインツール）

インストールすると、ターミナルから `japanesformer` コマンドが使用可能になります。

```bash
# 基本的な暗号化 (shift=1)
japanesformer "しんかんせんがはやい"
# 出力: ちんたんへんぱがばり

# 復号化 (-d または --decrypt オプション)
japanesformer "ちんたんへんぱがばり" -d -s 1
# 出力: しんかんせんがはやい

# 漢字・カタカナ交じり文の暗号化
japanesformer "新幹線が速い！"
# 出力: チンタンヘンぱガバリ！

# 波状シフトをオフにする (--no-wave)
japanesformer "あああああ" --no-wave
# 出力: かかかかか

# パイプ（標準入力）からの入力
echo "新幹線が速い" | japanesformer
```

---

## ⚠️ 制限事項とリスク

- **漢字の表記復元不可避（非対称性）**:  
  漢字を「読み（ひらがな）」に正規化して暗号化を行うため、復号時には元の漢字表記（例: `新幹線`）に戻すことはできず、ひらがな（例: `しんかんせん`）になります。可逆性は「音韻・情報レベル」で保証され、「漢字表記レベル」では非対称となります。

---

## ⚖️ ライセンス

[MIT License](LICENSE)
