const PROVIDER_LABELS = {
    anthropic: 'Claude',
    openai: 'GPT',
    gemini: 'Gemini',
    deepseek: 'DeepSeek'
};

let currentInputMethod = 'paste';
let selectedFile = null;
let currentReportData = null;

/* ── Chart instances (destroy before re-creating) ─────────────── */

let revenueChart, epsChart, marginsChart, sentimentChart;

/* ── Chart.js dark theme defaults ─────────────────────────────── */

Chart.defaults.color = '#8b8fa3';
Chart.defaults.borderColor = '#2a2d3e';

const CHART_COLORS = {
    accent: '#6c5ce7',
    accentAlt: '#a855f7',
    green: '#10b981',
    yellow: '#f59e0b',
    red: '#ef4444',
    muted: '#8b8fa3'
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

/* ── Confidence badges ──────────────────────────────────────────── */

function setConfidence(elementId, boxElement, score) {
    const badge = document.getElementById(elementId);
    if (!badge || score == null) return;

    badge.textContent = score + '% confident';
    badge.classList.add('show');
    badge.classList.remove('confidence-high', 'confidence-medium', 'confidence-low');

    if (score >= 70) {
        badge.classList.add('confidence-high');
    } else if (score >= 40) {
        badge.classList.add('confidence-medium');
    } else {
        badge.classList.add('confidence-low');
    }

    if (boxElement) {
        boxElement.classList.toggle('low-confidence', score < 40);
    }
}

function resetConfidenceBadges() {
    document.querySelectorAll('.confidence-badge').forEach(b => {
        b.classList.remove('show', 'confidence-high', 'confidence-medium', 'confidence-low');
        b.textContent = '';
    });
    document.querySelectorAll('.metric-box').forEach(b => {
        b.classList.remove('low-confidence');
    });
}

function displayResults(data) {
    currentReportData = data;
    document.getElementById('export-btn').style.display = '';

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

    // Confidence badges
    const metricBoxes = document.querySelectorAll('.metric-box');
    resetConfidenceBadges();
    setConfidence('sentiment-confidence', metricBoxes[0], data.sentiment_analysis?.confidence);
    setConfidence('tone-confidence', metricBoxes[1], data.sentiment_analysis?.confidence);
    setConfidence('eps-confidence', metricBoxes[2], data.financial_metrics?.earnings?.confidence);
    setConfidence('revenue-confidence', metricBoxes[3], data.financial_metrics?.revenue?.confidence);

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

    // Render charts
    renderCharts(data);

    document.getElementById('results').classList.add('show');

    // Fetch historical trend data if company name is available
    const companyName = data.company_info?.name ||
        document.getElementById('company-name').value;
    if (companyName) {
        fetchAndOverlayHistory(companyName);
    }
}

/* ── Chart helpers ─────────────────────────────────────────────── */

function parseNumeric(str) {
    if (str == null) return null;
    if (typeof str === 'number') return str;
    const cleaned = String(str).replace(/[^0-9.\-]/g, '');
    const num = parseFloat(cleaned);
    return isNaN(num) ? null : num;
}

function destroyCharts() {
    [revenueChart, epsChart, marginsChart, sentimentChart].forEach(c => {
        if (c) c.destroy();
    });
    revenueChart = epsChart = marginsChart = sentimentChart = null;
}

/* ── Render all 4 charts ───────────────────────────────────────── */

function renderCharts(data) {
    destroyCharts();

    const fm = data.financial_metrics || {};
    const revenue = fm.revenue || {};
    const earnings = fm.earnings || {};
    const margins = fm.margins || {};
    const sentiment = data.sentiment_analysis || {};

    // 1. Revenue bar chart
    const revCurrent = parseNumeric(revenue.current);
    const revPrevious = parseNumeric(revenue.previous);
    const revCtx = document.getElementById('revenue-chart').getContext('2d');

    const revLabels = [];
    const revData = [];
    const revColors = [];
    if (revPrevious != null) {
        revLabels.push('Previous');
        revData.push(revPrevious);
        revColors.push(CHART_COLORS.muted);
    }
    if (revCurrent != null) {
        revLabels.push('Current');
        revData.push(revCurrent);
        revColors.push(CHART_COLORS.accent);
    }

    if (revData.length) {
        revenueChart = new Chart(revCtx, {
            type: 'bar',
            data: {
                labels: revLabels,
                datasets: [{
                    label: 'Revenue',
                    data: revData,
                    backgroundColor: revColors,
                    borderRadius: 6,
                    maxBarThickness: 60
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#2a2d3e' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 2. EPS bar chart
    const epsReported = parseNumeric(earnings.eps_reported);
    const epsExpected = parseNumeric(earnings.eps_expected);
    const epsCtx = document.getElementById('eps-chart').getContext('2d');

    const epsLabels = [];
    const epsDataArr = [];
    const epsColors = [];
    if (epsExpected != null) {
        epsLabels.push('Expected');
        epsDataArr.push(epsExpected);
        epsColors.push(CHART_COLORS.muted);
    }
    if (epsReported != null) {
        epsLabels.push('Reported');
        epsDataArr.push(epsReported);
        const beatColor = (earnings.beat_miss || '').toLowerCase() === 'beat'
            ? CHART_COLORS.green : CHART_COLORS.red;
        epsColors.push(epsExpected != null ? beatColor : CHART_COLORS.accent);
    }

    if (epsDataArr.length) {
        epsChart = new Chart(epsCtx, {
            type: 'bar',
            data: {
                labels: epsLabels,
                datasets: [{
                    label: 'EPS',
                    data: epsDataArr,
                    backgroundColor: epsColors,
                    borderRadius: 6,
                    maxBarThickness: 60
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: '#2a2d3e' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 3. Margins horizontal bar chart
    const grossMargin = parseNumeric(margins.gross_margin);
    const opMargin = parseNumeric(margins.operating_margin);
    const netMargin = parseNumeric(margins.net_margin);
    const marginsCtx = document.getElementById('margins-chart').getContext('2d');

    const mLabels = [];
    const mData = [];
    const mColors = [];
    if (grossMargin != null) {
        mLabels.push('Gross');
        mData.push(grossMargin);
        mColors.push(CHART_COLORS.green);
    }
    if (opMargin != null) {
        mLabels.push('Operating');
        mData.push(opMargin);
        mColors.push(CHART_COLORS.yellow);
    }
    if (netMargin != null) {
        mLabels.push('Net');
        mData.push(netMargin);
        mColors.push(CHART_COLORS.accent);
    }

    if (mData.length) {
        marginsChart = new Chart(marginsCtx, {
            type: 'bar',
            data: {
                labels: mLabels,
                datasets: [{
                    label: 'Margin %',
                    data: mData,
                    backgroundColor: mColors,
                    borderRadius: 6,
                    maxBarThickness: 40
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: '#2a2d3e' },
                        ticks: { callback: v => v + '%' }
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    // 4. Sentiment doughnut gauge
    const score = sentiment.sentiment_score || 0;
    const sentCtx = document.getElementById('sentiment-chart').getContext('2d');

    const gaugeColor = score > 70 ? CHART_COLORS.green
        : score > 40 ? CHART_COLORS.yellow
        : CHART_COLORS.red;

    sentimentChart = new Chart(sentCtx, {
        type: 'doughnut',
        data: {
            labels: ['Score', 'Remaining'],
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [gaugeColor, '#2a2d3e'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            rotation: -90,
            circumference: 180,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        },
        plugins: [{
            id: 'sentimentCenterText',
            afterDraw(chart) {
                const { ctx, chartArea } = chart;
                const cx = (chartArea.left + chartArea.right) / 2;
                const cy = chartArea.bottom - 10;
                ctx.save();
                ctx.font = 'bold 28px -apple-system, BlinkMacSystemFont, sans-serif';
                ctx.fillStyle = gaugeColor;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(score, cx, cy);
                ctx.font = '12px -apple-system, BlinkMacSystemFont, sans-serif';
                ctx.fillStyle = '#8b8fa3';
                ctx.fillText('/ 100', cx, cy + 20);
                ctx.restore();
            }
        }]
    });
}

/* ── Historical trend overlay ──────────────────────────────────── */

async function fetchAndOverlayHistory(companyName) {
    try {
        const res = await fetch('/api/company-history?company=' + encodeURIComponent(companyName));
        const history = await res.json();

        if (!Array.isArray(history) || history.length < 2) return;

        // Add trend line to revenue chart
        if (revenueChart) {
            const revPoints = history
                .map(h => ({ label: h.quarter || '', value: parseNumeric(h.revenue_current) }))
                .filter(p => p.value != null);

            if (revPoints.length >= 2) {
                revenueChart.data.labels = revPoints.map(p => p.label);
                revenueChart.data.datasets = [{
                    type: 'line',
                    label: 'Revenue Trend',
                    data: revPoints.map(p => p.value),
                    borderColor: CHART_COLORS.accent,
                    backgroundColor: CHART_COLORS.accent + '33',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: CHART_COLORS.accent,
                    pointRadius: 4
                }];
                revenueChart.update();
            }
        }

        // Add trend line to EPS chart
        if (epsChart) {
            const epsPoints = history
                .map(h => ({ label: h.quarter || '', value: parseNumeric(h.eps_reported) }))
                .filter(p => p.value != null);

            if (epsPoints.length >= 2) {
                epsChart.data.labels = epsPoints.map(p => p.label);
                epsChart.data.datasets = [{
                    type: 'line',
                    label: 'EPS Trend',
                    data: epsPoints.map(p => p.value),
                    borderColor: CHART_COLORS.green,
                    backgroundColor: CHART_COLORS.green + '33',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: CHART_COLORS.green,
                    pointRadius: 4
                }];
                epsChart.update();
            }
        }
    } catch (err) {
        console.error('Failed to load company history:', err);
    }
}

/* ── Load report from history ───────────────────────────────────── */

async function loadReport(reportId) {
    // Switch to analyze tab
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.nav-item').classList.add('active');
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById('analyze-tab').classList.add('active');

    document.getElementById('loading').classList.add('show');
    document.getElementById('results').classList.remove('show');
    document.getElementById('error').classList.remove('show');

    try {
        const res = await fetch('/api/report/' + encodeURIComponent(reportId));
        const data = await res.json();
        if (res.ok) {
            displayResults(data);
        } else {
            showError(data.error || 'Failed to load report');
        }
    } catch (err) {
        showError('Network error: ' + err.message);
    } finally {
        document.getElementById('loading').classList.remove('show');
    }
}

/* ── Export ─────────────────────────────────────────────────────── */

function toggleExportMenu() {
    const menu = document.getElementById('export-menu');
    menu.classList.toggle('show');
}

// Close menu when clicking outside
document.addEventListener('click', e => {
    const dropdown = document.getElementById('export-btn');
    const menu = document.getElementById('export-menu');
    if (dropdown && menu && !dropdown.contains(e.target)) {
        menu.classList.remove('show');
    }
});

function exportAs(format) {
    document.getElementById('export-menu').classList.remove('show');
    if (!currentReportData) return;
    if (format === 'txt') exportAsTxt();
    else if (format === 'pdf') exportAsPdf();
}

function getExportFilename(ext) {
    const name = currentReportData.company_info?.name || 'analysis';
    const quarter = currentReportData.company_info?.reporting_period || '';
    const safe = (name + (quarter ? '_' + quarter : '')).replace(/[^a-zA-Z0-9]/g, '_');
    return safe + '.' + ext;
}

function buildReportText() {
    const d = currentReportData;
    const ci = d.company_info || {};
    const fm = d.financial_metrics || {};
    const rev = fm.revenue || {};
    const earn = fm.earnings || {};
    const mar = fm.margins || {};
    const guid = fm.guidance || {};
    const sent = d.sentiment_analysis || {};
    const meta = d.metadata || {};

    const lines = [];
    const hr = '='.repeat(60);
    const sr = '-'.repeat(40);

    lines.push(hr);
    lines.push('EARNINGS ANALYSIS REPORT');
    lines.push(hr);
    lines.push('');

    // Company info
    if (ci.name) lines.push('Company:    ' + ci.name);
    if (ci.ticker) lines.push('Ticker:     ' + ci.ticker);
    if (ci.reporting_period) lines.push('Period:     ' + ci.reporting_period);
    if (ci.report_date) lines.push('Date:       ' + ci.report_date);
    if (meta.provider) lines.push('Provider:   ' + (meta.provider || '') + ' (' + (meta.model_used || '') + ')');
    lines.push('');

    // Financial metrics
    lines.push(sr);
    lines.push('FINANCIAL METRICS');
    lines.push(sr);
    lines.push('');
    if (rev.current) lines.push('Revenue (current):     ' + rev.current);
    if (rev.previous) lines.push('Revenue (previous):    ' + rev.previous);
    if (rev.yoy_growth) lines.push('YoY Growth:            ' + rev.yoy_growth);
    if (rev.confidence != null) lines.push('Revenue Confidence:    ' + rev.confidence + '%');
    lines.push('');
    if (earn.eps_reported) lines.push('EPS Reported:          ' + earn.eps_reported);
    if (earn.eps_expected) lines.push('EPS Expected:          ' + earn.eps_expected);
    if (earn.beat_miss) lines.push('Beat/Miss:             ' + earn.beat_miss);
    if (earn.net_income) lines.push('Net Income:            ' + earn.net_income);
    if (earn.confidence != null) lines.push('Earnings Confidence:   ' + earn.confidence + '%');
    lines.push('');
    if (mar.gross_margin) lines.push('Gross Margin:          ' + mar.gross_margin);
    if (mar.operating_margin) lines.push('Operating Margin:      ' + mar.operating_margin);
    if (mar.net_margin) lines.push('Net Margin:            ' + mar.net_margin);
    if (mar.confidence != null) lines.push('Margins Confidence:    ' + mar.confidence + '%');
    lines.push('');
    if (guid.provided != null) {
        lines.push('Guidance Provided:     ' + (guid.provided ? 'Yes' : 'No'));
        if (guid.next_quarter_revenue) lines.push('Next Q Revenue:        ' + guid.next_quarter_revenue);
        if (guid.next_quarter_eps) lines.push('Next Q EPS:            ' + guid.next_quarter_eps);
        if (guid.full_year) lines.push('Full Year:             ' + guid.full_year);
        lines.push('');
    }

    // Sentiment
    lines.push(sr);
    lines.push('SENTIMENT ANALYSIS');
    lines.push(sr);
    lines.push('');
    if (sent.overall_tone) lines.push('Overall Tone:          ' + sent.overall_tone);
    if (sent.management_confidence) lines.push('Mgmt Confidence:       ' + sent.management_confidence);
    if (sent.forward_outlook) lines.push('Forward Outlook:       ' + sent.forward_outlook);
    if (sent.sentiment_score != null) lines.push('Sentiment Score:       ' + sent.sentiment_score + ' / 100');
    if (sent.confidence != null) lines.push('Sentiment Confidence:  ' + sent.confidence + '%');
    lines.push('');

    // Key highlights
    if (d.key_highlights?.length) {
        lines.push(sr);
        lines.push('KEY HIGHLIGHTS');
        lines.push(sr);
        lines.push('');
        d.key_highlights.forEach((h, i) => lines.push((i + 1) + '. ' + h));
        lines.push('');
    }

    // Concerns
    if (d.concerns_risks?.length) {
        lines.push(sr);
        lines.push('CONCERNS & RISKS');
        lines.push(sr);
        lines.push('');
        d.concerns_risks.forEach((c, i) => lines.push((i + 1) + '. ' + c));
        lines.push('');
    }

    // Red flags
    if (d.red_flags?.length) {
        lines.push(sr);
        lines.push('RED FLAGS');
        lines.push(sr);
        lines.push('');
        d.red_flags.forEach((r, i) => lines.push((i + 1) + '. ' + r));
        lines.push('');
    }

    // Executive summary
    if (d.analyst_summary) {
        lines.push(sr);
        lines.push('EXECUTIVE SUMMARY');
        lines.push(sr);
        lines.push('');
        lines.push(d.analyst_summary);
        lines.push('');
    }

    lines.push(hr);
    lines.push('Generated by Finalyze');
    lines.push(hr);

    return lines.join('\n');
}

function exportAsTxt() {
    const text = buildReportText();
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = getExportFilename('txt');
    a.click();
    URL.revokeObjectURL(url);
}

function exportAsPdf() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });

    const d = currentReportData;
    const ci = d.company_info || {};
    const fm = d.financial_metrics || {};
    const rev = fm.revenue || {};
    const earn = fm.earnings || {};
    const mar = fm.margins || {};
    const sent = d.sentiment_analysis || {};
    const meta = d.metadata || {};

    const pageW = doc.internal.pageSize.getWidth();
    const margin = 20;
    const contentW = pageW - margin * 2;
    let y = 20;

    function checkPage(needed) {
        if (y + needed > 275) { doc.addPage(); y = 20; }
    }

    function heading(text) {
        checkPage(14);
        doc.setFontSize(13);
        doc.setFont(undefined, 'bold');
        doc.setTextColor(108, 92, 231);
        doc.text(text, margin, y);
        y += 4;
        doc.setDrawColor(108, 92, 231);
        doc.setLineWidth(0.4);
        doc.line(margin, y, margin + contentW, y);
        y += 8;
    }

    function label(lbl, val) {
        if (!val && val !== 0) return;
        checkPage(7);
        doc.setFontSize(9);
        doc.setFont(undefined, 'bold');
        doc.setTextColor(100);
        doc.text(lbl, margin, y);
        doc.setFont(undefined, 'normal');
        doc.setTextColor(40);
        doc.text(String(val), margin + 45, y);
        y += 6;
    }

    function bodyText(text) {
        doc.setFontSize(9);
        doc.setFont(undefined, 'normal');
        doc.setTextColor(40);
        const lines = doc.splitTextToSize(text, contentW);
        lines.forEach(line => {
            checkPage(6);
            doc.text(line, margin, y);
            y += 5;
        });
    }

    function bulletList(items) {
        doc.setFontSize(9);
        doc.setFont(undefined, 'normal');
        doc.setTextColor(40);
        items.forEach(item => {
            const lines = doc.splitTextToSize(item, contentW - 6);
            lines.forEach((line, i) => {
                checkPage(6);
                if (i === 0) doc.text('\u2022', margin, y);
                doc.text(line, margin + 6, y);
                y += 5;
            });
            y += 1;
        });
    }

    // Title
    doc.setFontSize(20);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(30);
    doc.text(ci.name || 'Earnings Analysis', margin, y);
    y += 8;

    if (ci.reporting_period || ci.ticker) {
        doc.setFontSize(11);
        doc.setFont(undefined, 'normal');
        doc.setTextColor(100);
        doc.text([ci.ticker, ci.reporting_period].filter(Boolean).join('  |  '), margin, y);
        y += 6;
    }
    if (meta.provider) {
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text('Analyzed with ' + meta.provider + ' (' + (meta.model_used || '') + ')', margin, y);
        y += 10;
    }

    // Financial Metrics
    heading('Financial Metrics');
    label('Revenue:', rev.current);
    label('Previous:', rev.previous);
    label('YoY Growth:', rev.yoy_growth);
    if (rev.confidence != null) label('Confidence:', rev.confidence + '%');
    y += 2;
    label('EPS Reported:', earn.eps_reported);
    label('EPS Expected:', earn.eps_expected);
    label('Beat/Miss:', earn.beat_miss);
    if (earn.confidence != null) label('Confidence:', earn.confidence + '%');
    y += 2;
    label('Gross Margin:', mar.gross_margin);
    label('Operating Margin:', mar.operating_margin);
    label('Net Margin:', mar.net_margin);
    if (mar.confidence != null) label('Confidence:', mar.confidence + '%');
    y += 4;

    // Sentiment
    heading('Sentiment Analysis');
    label('Overall Tone:', sent.overall_tone);
    label('Mgmt Confidence:', sent.management_confidence);
    label('Forward Outlook:', sent.forward_outlook);
    label('Score:', sent.sentiment_score != null ? sent.sentiment_score + ' / 100' : null);
    if (sent.confidence != null) label('Confidence:', sent.confidence + '%');
    y += 4;

    // Highlights
    if (d.key_highlights?.length) {
        heading('Key Highlights');
        bulletList(d.key_highlights);
        y += 4;
    }

    // Concerns
    if (d.concerns_risks?.length) {
        heading('Concerns & Risks');
        bulletList(d.concerns_risks);
        y += 4;
    }

    // Red flags
    if (d.red_flags?.length) {
        heading('Red Flags');
        bulletList(d.red_flags);
        y += 4;
    }

    // Summary
    if (d.analyst_summary) {
        heading('Executive Summary');
        bodyText(d.analyst_summary);
        y += 4;
    }

    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text('Generated by Finalyze', margin, 290);
        doc.text('Page ' + i + ' of ' + pageCount, pageW - margin - 20, 290);
    }

    doc.save(getExportFilename('pdf'));
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

            card.addEventListener('click', () => loadReport(item.id));
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
