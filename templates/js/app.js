const PROVIDER_LABELS = {
    anthropic: 'Claude',
    openai: 'GPT',
    gemini: 'Gemini',
    deepseek: 'DeepSeek'
};

let currentInputMethod = 'paste';
let selectedFile = null;

function switchTab(tabName) {
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');

    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(tabName + '-tab').classList.add('active');

    if (tabName === 'history') {
        loadHistory();
    }
}

function updateProviderBadge() {
    const provider = document.getElementById('provider').value;
    document.getElementById('provider-badge').textContent = PROVIDER_LABELS[provider] || provider;
}

/* ── Input method switching ─────────────────────────────────────── */

function switchInputMethod(method) {
    currentInputMethod = method;

    document.querySelectorAll('.input-tab').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');

    document.querySelectorAll('.input-panel').forEach(p => p.classList.remove('active'));
    document.getElementById('input-' + method).classList.add('active');
}

/* ── File upload handling ───────────────────────────────────────── */

function initFileUpload() {
    const zone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    if (!zone || !fileInput) return;

    zone.addEventListener('click', () => fileInput.click());

    zone.addEventListener('dragover', e => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('drag-over');
    });

    zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFileSelection(fileInput.files[0]);
        }
    });
}

function handleFileSelection(file) {
    const allowed = ['.pdf', '.docx', '.txt'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!allowed.includes(ext)) {
        showError('Unsupported file type. Please upload a PDF, DOCX, or TXT file.');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showError('File too large. Maximum size is 10 MB.');
        return;
    }

    selectedFile = file;
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-preview').style.display = '';
}

function clearFileSelection() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-preview').style.display = 'none';
    document.getElementById('file-name').textContent = '';
}

/* ── Analysis ───────────────────────────────────────────────────── */

async function analyzeReport() {
    const companyName = document.getElementById('company-name').value;
    const provider = document.getElementById('provider').value;

    let fetchOptions;

    if (currentInputMethod === 'paste') {
        const earningsText = document.getElementById('earnings-text').value;
        if (!earningsText.trim()) {
            showError('Please enter earnings report text');
            return;
        }
        fetchOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                earnings_text: earningsText,
                company_name: companyName,
                provider: provider
            })
        };
    } else if (currentInputMethod === 'upload') {
        if (!selectedFile) {
            showError('Please select a file to upload');
            return;
        }
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('company_name', companyName);
        formData.append('provider', provider);
        fetchOptions = {
            method: 'POST',
            body: formData
        };
    } else if (currentInputMethod === 'gdocs') {
        const gdocsUrl = document.getElementById('gdocs-url').value;
        if (!gdocsUrl.trim()) {
            showError('Please enter a Google Docs URL');
            return;
        }
        fetchOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                google_docs_url: gdocsUrl,
                company_name: companyName,
                provider: provider
            })
        };
    }

    document.getElementById('loading').classList.add('show');
    document.getElementById('results').classList.remove('show');
    document.getElementById('error').classList.remove('show');

    try {
        const response = await fetch('/api/analyze', fetchOptions);
        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            showError(data.error || 'Analysis failed');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        document.getElementById('loading').classList.remove('show');
    }
}

function displayResults(data) {
    // Model badge
    const model = data.metadata?.model_used || '';
    const providerName = data.metadata?.provider || '';
    const badge = document.getElementById('results-model');
    if (model) {
        badge.textContent = (PROVIDER_LABELS[providerName] || providerName) + ' \u00b7 ' + model;
        badge.style.display = '';
    } else {
        badge.style.display = 'none';
    }

    // Sentiment
    const sentimentScore = data.sentiment_analysis?.sentiment_score || 0;
    document.getElementById('sentiment-score').textContent = sentimentScore + '/100';
    document.getElementById('sentiment-score').className = 'metric-value ' +
        (sentimentScore > 70 ? 'sentiment-positive' :
         sentimentScore > 40 ? 'sentiment-neutral' : 'sentiment-negative');

    // Overall tone
    const tone = data.sentiment_analysis?.overall_tone || 'N/A';
    document.getElementById('overall-tone').textContent = tone.charAt(0).toUpperCase() + tone.slice(1);

    // EPS
    const epsResult = data.financial_metrics?.earnings?.beat_miss || 'N/A';
    document.getElementById('eps-result').textContent = epsResult.toUpperCase();

    // Revenue growth
    document.getElementById('revenue-growth').textContent =
        data.financial_metrics?.revenue?.yoy_growth || 'N/A';

    // Highlights
    const highlightsList = document.getElementById('highlights-list');
    highlightsList.innerHTML = '';
    (data.key_highlights || []).forEach(h => {
        const li = document.createElement('li');
        li.textContent = h;
        highlightsList.appendChild(li);
    });

    // Concerns
    const concernsList = document.getElementById('concerns-list');
    concernsList.innerHTML = '';
    (data.concerns_risks || []).forEach(c => {
        const li = document.createElement('li');
        li.textContent = c;
        concernsList.appendChild(li);
    });

    // Summary
    document.getElementById('summary').textContent =
        data.analyst_summary || 'No summary available';

    document.getElementById('results').classList.add('show');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    setTimeout(() => errorDiv.classList.remove('show'), 5000);
}

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();

        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';

        if (history.length === 0) {
            historyList.innerHTML = '<div class="history-empty">No analysis history yet.</div>';
            return;
        }

        [...history].reverse().forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-card';

            const date = new Date(item.timestamp);
            const formatted = date.toLocaleDateString(undefined, {
                month: 'short', day: 'numeric', year: 'numeric'
            }) + ' at ' + date.toLocaleTimeString(undefined, {
                hour: '2-digit', minute: '2-digit'
            });

            card.innerHTML =
                '<div class="history-info">' +
                    '<h3>' + escapeHtml(item.company) + '</h3>' +
                    '<span class="history-meta">' + formatted + '</span>' +
                '</div>' +
                '<div class="history-score">' + (item.sentiment_score || 0) + '</div>';

            historyList.appendChild(card);
        });
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* ── Init ────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    initFileUpload();
});
