// DOM Elements
const sourceText = document.getElementById('sourceText');
const targetText = document.getElementById('targetText');
const translateBtn = document.getElementById('translateBtn');
const clearBtn = document.getElementById('clearBtn');
const copyBtn = document.getElementById('copyBtn');
const swapBtn = document.getElementById('swapBtn');
const autoDetect = document.getElementById('autoDetect');
const sourceLang = document.getElementById('sourceLang');
const targetLang = document.getElementById('targetLang');
const charCount = document.getElementById('charCount');
const statusMessage = document.getElementById('statusMessage');

// State
let currentSrcLang = 'en';
let currentTgtLang = 'ko';
let isTranslating = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    updateCharCount();
});

// Character count update
sourceText.addEventListener('input', () => {
    updateCharCount();
    hideStatus();
});

function updateCharCount() {
    const count = sourceText.value.length;
    charCount.textContent = count;
}

// Translate button
translateBtn.addEventListener('click', async () => {
    await performTranslation();
});

// Enter key to translate (Ctrl+Enter or Cmd+Enter)
sourceText.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        performTranslation();
    }
});

// Clear button
clearBtn.addEventListener('click', () => {
    sourceText.value = '';
    targetText.value = '';
    updateCharCount();
    sourceLang.textContent = 'Auto-detect';
    targetLang.textContent = '-';
    hideStatus();
});

// Copy button
copyBtn.addEventListener('click', async () => {
    const text = targetText.value;
    if (!text) {
        showStatus('No translation to copy', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        copyBtn.textContent = '✓ Copied!';
        copyBtn.classList.add('copy-success');
        showStatus('Translation copied to clipboard', 'success');

        setTimeout(() => {
            copyBtn.textContent = 'Copy';
            copyBtn.classList.remove('copy-success');
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
        showStatus('Failed to copy to clipboard', 'error');
    }
});

// Swap button
swapBtn.addEventListener('click', () => {
    // Swap text
    const temp = sourceText.value;
    sourceText.value = targetText.value;
    targetText.value = temp;

    // Swap languages
    const tempLang = currentSrcLang;
    currentSrcLang = currentTgtLang;
    currentTgtLang = tempLang;

    updateCharCount();
    hideStatus();
});

// Perform translation
async function performTranslation() {
    const text = sourceText.value.trim();

    if (!text) {
        showStatus('Please enter text to translate', 'error');
        return;
    }

    if (isTranslating) {
        return;
    }

    setTranslating(true);
    hideStatus();

    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                auto_detect: autoDetect.checked,
                src_lang: currentSrcLang,
                tgt_lang: currentTgtLang
            })
        });

        const data = await response.json();

        if (data.success) {
            targetText.value = data.translation;

            // Update language badges
            if (data.detected_lang) {
                sourceLang.textContent = data.src_lang === 'ko' ? '한국어 (Korean)' : 'English';
                targetLang.textContent = data.tgt_lang === 'ko' ? '한국어 (Korean)' : 'English';
            } else {
                sourceLang.textContent = currentSrcLang === 'ko' ? '한국어 (Korean)' : 'English';
                targetLang.textContent = currentTgtLang === 'ko' ? '한국어 (Korean)' : 'English';
            }

            // Update current languages
            currentSrcLang = data.src_lang;
            currentTgtLang = data.tgt_lang;

            showStatus('Translation completed successfully', 'success');
        } else {
            throw new Error(data.error || 'Translation failed');
        }
    } catch (error) {
        console.error('Translation error:', error);
        showStatus(`Error: ${error.message}`, 'error');
        targetText.value = '';
    } finally {
        setTranslating(false);
    }
}

// Set translating state
function setTranslating(translating) {
    isTranslating = translating;
    translateBtn.disabled = translating;

    const btnText = translateBtn.querySelector('.btn-text');
    const btnLoading = translateBtn.querySelector('.btn-loading');

    if (translating) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline-flex';
    } else {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// Show status message
function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;

    // Auto hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(hideStatus, 3000);
    }
}

// Hide status message
function hideStatus() {
    statusMessage.className = 'status-message';
    statusMessage.style.display = 'none';
}

// Check server health
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (!data.success || !data.translator_loaded) {
            showStatus('Server is not ready. Please wait...', 'info');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        showStatus('Cannot connect to server', 'error');
    }
}

// Auto-detect toggle
autoDetect.addEventListener('change', () => {
    if (autoDetect.checked) {
        sourceLang.textContent = 'Auto-detect';
        targetLang.textContent = '-';
    }
});
