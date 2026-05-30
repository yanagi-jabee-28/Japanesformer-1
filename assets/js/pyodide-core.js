/**
 * PyodideとPythonコアロジックの管理クラス
 */
class PyodideManager {
    constructor() {
        this.pyodideInstance = null;
    }

    /**
     * Pyodideの初期化とパッケージのインストールを行います。
     * @param {function} onStatusChange ステータス変更時に呼ばれるコールバック (state, message)
     */
    async initialize(onStatusChange) {
        try {
            console.log("Loading Pyodide...");
            onStatusChange('loading', 'Pyodide環境を初期化中...');
            this.pyodideInstance = await loadPyodide();
            
            console.log("Pyodide Loaded. Loading micropip...");
            onStatusChange('loading', '必要なパッケージ（micropip）をロード中...');
            await this.pyodideInstance.loadPackage("micropip");
            
            onStatusChange('loading', '依存パッケージ (pykakasi 等) をインストール中...');
            await this.pyodideInstance.runPythonAsync(`
                import micropip
                # pykakasi (Pure Python) のインストール
                await micropip.install("pykakasi")
                
                # 同一フォルダにある wheel を相対パスでインストール
                await micropip.install("./japanesformer-0.1.0-py3-none-any.whl")
            `);

            onStatusChange('loading', '変換モジュールをコンパイル中...');
            await this.pyodideInstance.runPythonAsync(`
                from japanesformer import transform
                from japanesformer.text_utils import TextNormalizer
                normalizer = TextNormalizer()
            `);

            console.log("Initialization complete!");
            onStatusChange('ready', 'Ready - ブラウザ上で実行中');
        } catch (error) {
            console.error("Pyodideの初期化に失敗しました:", error);
            onStatusChange('error', `エラー: 初期化に失敗しました。詳細: ${error.message}`);
            throw error;
        }
    }

    /**
     * 日本語の変換処理を行います。
     * @param {string} text 変換対象テキスト
     * @param {number} shift シフト量
     * @param {boolean} useWave 波状変換を適用するか
     * @param {boolean} decrypt 復号化するかどうか
     * @returns {Promise<string>} 変換後の文字列
     */
    async transformText(text, shift, useWave, decrypt) {
        if (!this.pyodideInstance) {
            throw new Error("Pyodideが初期化されていません。");
        }
        
        // パラメータを Python グローバル変数にバインド
        this.pyodideInstance.globals.set("input_str", text);
        this.pyodideInstance.globals.set("shift_val", shift);
        this.pyodideInstance.globals.set("use_wave", useWave);
        this.pyodideInstance.globals.set("is_decrypt", decrypt);

        // Pythonコードを実行して結果を返す
        return await this.pyodideInstance.runPythonAsync(`
            # テキストの正規化とメタデータ抽出
            meta = normalizer.normalize(input_str)
            normalized_text = "".join([item["char"] for item in meta])
            
            # コア変換処理
            transformed_hira = transform(
                normalized_text,
                shift=shift_val,
                decrypt=is_decrypt,
                use_wave=use_wave
            )
            
            # 文字種（カタカナ等）の復元
            normalizer.restore_types(transformed_hira, meta)
        `);
    }
}

export const pyodideManager = new PyodideManager();
