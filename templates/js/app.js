const PROVIDER_LABELS = {
    anthropic: 'Claude',
    openai: 'GPT',
    gemini: 'Gemini',
    deepseek: 'DeepSeek'
};

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

async function analyzeReport() {
    const earningsText = document.getElementById('earnings-text').value;
    const companyName = document.getElementById('company-name').value;
    const provider = document.getElementById('provider').value;

    if (!earningsText.trim()) {
        showError('Please enter earnings report text');
        return;
    }

    document.getElementById('loading').classList.add('show');
    document.getElementById('results').classList.remove('show');
    document.getElementById('error').classList.remove('show');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                earnings_text: earningsText,
                company_name: companyName,
                provider: provider
            })
        });

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