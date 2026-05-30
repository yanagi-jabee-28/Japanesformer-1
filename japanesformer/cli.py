# -*- coding: utf-8 -*-

import sys
import argparse
from japanesformer.core import transform
from japanesformer.text_utils import TextNormalizer

def parse_args(args=None):
    """
    コマンドライン引数を解析します。
    """
    parser = argparse.ArgumentParser(
        description="Japanesformer - 日本語の母音を固定したまま子音を循環させる可逆変換ツール"
    )
    parser.add_argument(
        "text",
        nargs="?",
        default=None,
        help="変換対象の日本語テキスト。省略された場合は標準入力から読み込みます。"
    )
    parser.add_argument(
        "-s", "--shift",
        type=int,
        default=1,
        help="基本シフト量（デフォルト: 1）。任意の非負の整数。"
    )
    parser.add_argument(
        "-d", "--decrypt",
        action="store_true",
        help="指定された場合、テキストの復号（逆変換）を行います。"
    )
    parser.add_argument(
        "--no-wave",
        action="store_true",
        help="指定された場合、位置依存の波状シフト（出現順カウンタの加算）を無効化します。"
    )
    return parser.parse_args(args)

def main():
    """
    CLIのメインエントリーポイント。
    """
    # Windows環境におけるコンソールの文字化け対策（標準出力・標準エラー出力をUTF-8に変更）
    # sys.stdout や sys.stderr のエンコーディングを上書きする
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
        
    try:
        args = parse_args()
        
        # 入力テキストの取得（引数がない場合は標準入力から）
        if args.text is not None:
            input_text = args.text
        else:
            if not sys.stdin.isatty():
                if hasattr(sys.stdin, "reconfigure"):
                    sys.stdin.reconfigure(encoding="utf-8")
                input_text = sys.stdin.read().strip()
            else:
                # 対話的実行で引数も標準入力もない場合はヘルプを表示して終了
                print("エラー: 変換対象のテキストが指定されていません。", file=sys.stderr)
                print("使用方法: japanesformer [テキスト] [オプション] または パイプ経由での入力", file=sys.stderr)
                sys.exit(1)
                
        if not input_text:
            print("", end="")
            sys.exit(0)
            
        # シフト量の妥当性検証
        if args.shift < 0:
            print("エラー: シフト量（--shift）は0以上の整数である必要があります。", file=sys.stderr)
            sys.exit(1)
            
        # 漢字やカタカナなどの前処理を適用
        normalizer = TextNormalizer()
        
        if args.decrypt:
            # 復号の場合：
            # 入力文字列はひらがな/カタカナ/特殊文字に変換された状態。
            # 復元用に文字種メタデータを一度抽出する。
            meta = normalizer.normalize(input_text)
            normalized_text = "".join([item["char"] for item in meta])
            
            # 復号コア変換
            decrypted_hira = transform(
                normalized_text,
                shift=args.shift,
                decrypt=True,
                use_wave=not args.no_wave
            )
            
            # メタデータに基づいて文字種を復元（カタカナなど）
            result = normalizer.restore_types(decrypted_hira, meta)
        else:
            # 暗号化の場合：
            # pykakasiを用いてひらがなに統一しながら文字種メタデータを取得
            meta = normalizer.normalize(input_text)
            normalized_text = "".join([item["char"] for item in meta])
            
            # 暗号化コア変換
            encrypted_hira = transform(
                normalized_text,
                shift=args.shift,
                decrypt=False,
                use_wave=not args.no_wave
            )
            
            # メタデータに基づいて文字種を復元（カタカナなど）
            result = normalizer.restore_types(encrypted_hira, meta)
            
        print(result)
        sys.exit(0)
        
    except Exception as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
