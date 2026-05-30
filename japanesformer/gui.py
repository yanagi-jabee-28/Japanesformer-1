# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from japanesformer.core import transform
from japanesformer.text_utils import TextNormalizer

class JapanesformerGUI:
    """
    Japanesformer 用の簡易 Tkinter GUI
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Japanesformer GUI")
        self.root.geometry("600x550")
        self.root.minsize(500, 450)
        
        self.normalizer = TextNormalizer()
        self._setup_style()
        self._create_widgets()

    def _setup_style(self):
        """
        GUIのウィジェットの見た目をクリーンに整えます。
        """
        style = ttk.Style()
        style.theme_use("clam")
        
        # フォントやパディングの設定
        style.configure(".", font=("Helvetica", 10))
        style.configure("TLabel", padding=5)
        style.configure("TButton", padding=5, font=("Helvetica", 10, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), padding=10)

    def _create_widgets(self):
        """
        ウィンドウ内のウィジェットを作成し、配置します。
        """
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ヘッダータイトル
        header = ttk.Label(main_frame, text="Japanesformer 可逆日本語暗号化ツール", style="Header.TLabel")
        header.pack(fill=tk.X)

        # ------------------ 入力エリア ------------------
        input_group = ttk.LabelFrame(main_frame, text=" 入力テキスト ", padding="10 10 10 10")
        input_group.pack(fill=tk.BOTH, expand=True, pady=5)

        self.input_text = tk.Text(input_group, height=6, wrap=tk.WORD, font=("Consolas", 11))
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.insert(tk.END, "しんかんせんがはやい (漢字: 新幹線が速い)")

        # ------------------ オプションエリア ------------------
        opt_frame = ttk.Frame(main_frame, padding="5 10 5 10")
        opt_frame.pack(fill=tk.X, pady=5)

        # シフト量
        ttk.Label(opt_frame, text="シフト量 (base_shift):").pack(side=tk.LEFT, padx=5)
        self.shift_var = tk.StringVar(value="1")
        shift_spin = ttk.Spinbox(
            opt_frame, 
            from_=0, 
            to=100, 
            width=5, 
            textvariable=self.shift_var,
            font=("Helvetica", 10)
        )
        shift_spin.pack(side=tk.LEFT, padx=5)

        # 波状変換チェックボックス
        self.wave_var = tk.BooleanVar(value=True)
        wave_check = ttk.Checkbutton(
            opt_frame, 
            text="波状変換 (位置依存シフト) を有効にする", 
            variable=self.wave_var
        )
        wave_check.pack(side=tk.LEFT, padx=20)

        # ------------------ ボタンエリア ------------------
        btn_frame = ttk.Frame(main_frame, padding=5)
        btn_frame.pack(fill=tk.X, pady=5)

        encrypt_btn = ttk.Button(btn_frame, text="🔒 暗号化 (変換)", command=self._encrypt)
        encrypt_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        decrypt_btn = ttk.Button(btn_frame, text="🔓 復号化 (戻す)", command=self._decrypt)
        decrypt_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # ------------------ 出力エリア ------------------
        output_group = ttk.LabelFrame(main_frame, text=" 変換結果 ", padding="10 10 10 10")
        output_group.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = tk.Text(
            output_group, 
            height=6, 
            wrap=tk.WORD, 
            font=("Consolas", 11),
            bg="#f0f0f0"
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def _get_inputs(self):
        """
        入力テキストとシフト量を取得し、バリデーションを行います。
        """
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "入力テキストが空です。")
            return None, None, None

        try:
            shift = int(self.shift_var.get())
            if shift < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("エラー", "シフト量には0以上の整数を指定してください。")
            return None, None, None

        use_wave = self.wave_var.get()
        return text, shift, use_wave

    def _encrypt(self):
        """
        暗号化処理を実行し、結果を表示します。
        """
        text, shift, use_wave = self._get_inputs()
        if text is None:
            return

        try:
            # 漢字ひらがな正規化とメタデータ抽出
            meta = self.normalizer.normalize(text)
            normalized_text = "".join([item["char"] for item in meta])
            
            # 暗号化
            encrypted_hira = transform(
                normalized_text,
                shift=shift,
                decrypt=False,
                use_wave=use_wave
            )
            
            # 文字種復元
            result = self.normalizer.restore_types(encrypted_hira, meta)
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("エラー", f"変換中にエラーが発生しました:\n{str(e)}")

    def _decrypt(self):
        """
        復号化処理を実行し、結果を表示します。
        """
        text, shift, use_wave = self._get_inputs()
        if text is None:
            return

        try:
            # 入力文字列をひらがな正規化（復元用メタデータ取得のため）
            meta = self.normalizer.normalize(text)
            normalized_text = "".join([item["char"] for item in meta])
            
            # 復号化
            decrypted_hira = transform(
                normalized_text,
                shift=shift,
                decrypt=True,
                use_wave=use_wave
            )
            
            # 文字種復元
            result = self.normalizer.restore_types(decrypted_hira, meta)
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("エラー", f"復号中にエラーが発生しました:\n{str(e)}")

def main():
    root = tk.Tk()
    app = JapanesformerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
