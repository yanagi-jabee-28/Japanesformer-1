import { pyodideManager } from './pyodide-core.js';

document.addEventListener('DOMContentLoaded', () => {
    // DOM要素の取得
    const elements = {
        statusDot: document.getElementById('status-dot'),
        statusText: document.getElementById('status-text'),
        btnEncrypt: document.getElementById('btn-encrypt'),
        btnDecrypt: document.getElementById('btn-decrypt'),
        btnCopy: document.getElementById('btn-copy'),
        inputText: document.getElementById('input-text'),
        shiftAmount: document.getElementById('shift-amount'),
        waveToggle: document.getElementById('wave-toggle'),
        outputDisplay: document.getElementById('output-display')
    };

    /**
     * UIのステータスインジケーター表示を更新します。
     * @param {string} state ステータス状態 ('loading', 'ready', 'error')
     * @param {string} message 表示メッセージ
     */
    function updateStatus(state, message) {
        if (state === 'ready') {
            elements.statusDot.className = "status-dot ready";
            elements.statusText.innerText = message;
            elements.btnEncrypt.disabled = false;
            elements.btnDecrypt.disabled = false;
            elements.outputDisplay.innerText = "準備完了。入力して「暗号化」または「復号化」ボタンを押してください。";
        } else if (state === 'error') {
            elements.statusDot.style.backgroundColor = "#ef4444";
            elements.statusDot.style.boxShadow = "0 0 8px #ef4444";
            elements.statusDot.className = "status-dot";
            elements.statusText.innerText = message;
        } else {
            elements.statusDot.className = "status-dot loading";
            elements.statusText.innerText = message;
        }
    }

    /**
     * ボタン押下時の変換処理ハンドラー。
     * @param {boolean} decrypt 復号化するかどうか
     */
    async function handleTransformation(decrypt) {
        const text = elements.inputText.value;
        const shift = parseInt(elements.shiftAmount.value) || 0;
        const useWave = elements.waveToggle.checked;

        if (!text) {
            elements.outputDisplay.innerText = "入力テキストが空です。";
            return;
        }

        try {
            const result = await pyodideManager.transformText(text, shift, useWave, decrypt);
            elements.outputDisplay.innerText = result;
            elements.btnCopy.style.display = "inline-block";
            elements.btnCopy.innerText = "コピー";
        } catch (error) {
            console.error("Execution failed:", error);
            elements.outputDisplay.innerText = "エラーが発生しました:\n" + error.message;
        }
    }

    // イベントリスナーの登録
    elements.btnEncrypt.addEventListener('click', () => handleTransformation(false));
    elements.btnDecrypt.addEventListener('click', () => handleTransformation(true));
    
    // コピーボタンのアクション
    elements.btnCopy.addEventListener('click', () => {
        const text = elements.outputDisplay.innerText;
        navigator.clipboard.writeText(text).then(() => {
            elements.btnCopy.innerText = "コピーしました！";
            setTimeout(() => {
                elements.btnCopy.innerText = "コピー";
            }, 2000);
        }).catch(err => {
            console.error('Could not copy text: ', err);
        });
    });

    // Pyodideランタイムの初期化を開始
    pyodideManager.initialize(updateStatus).catch(err => {
        elements.outputDisplay.innerText = "初期化中に致命的なエラーが発生しました:\n" + err.message;
    });
});
