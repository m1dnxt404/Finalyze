"""
Simple Web Dashboard for Earnings Report Analyzer
Run with: python web_dashboard.py
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import json
from datetime import datetime
from earnings_analyzer import EarningsReportAnalyzer, PROVIDERS

app = Flask(__name__)

# Store analysis history in memory (in production, use a database)
analysis_history = []

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files from templates/css"""
    return send_from_directory('templates/css', filename)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Return available AI providers"""
    return jsonify({key: val["name"] for key, val in PROVIDERS.items()})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint for analyzing earnings reports"""
    try:
        data = request.get_json()
        earnings_text = data.get('earnings_text', '')
        company_name = data.get('company_name', '')
        provider = data.get('provider', 'anthropic')

        if not earnings_text:
            return jsonify({'error': 'No earnings text provided'}), 400

        # Perform analysis with selected provider
        analyzer = EarningsReportAnalyzer(provider=provider)
        result = analyzer.analyze_earnings(earnings_text, company_name)
        
        # Add to history
        history_entry = {
            'id': len(analysis_history),
            'timestamp': datetime.now().isoformat(),
            'company': company_name or result.get('company_info', {}).get('name', 'Unknown'),
            'sentiment_score': result.get('sentiment_analysis', {}).get('sentiment_score', 0),
            'analysis': result
        }
        analysis_history.append(history_entry)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get analysis history"""
    return jsonify(analysis_history)

@app.route('/api/export/<int:analysis_id>', methods=['GET'])
def export_analysis(analysis_id):
    """Export specific analysis as JSON"""
    if analysis_id >= len(analysis_history):
        return jsonify({'error': 'Analysis not found'}), 404
    
    analysis = analysis_history[analysis_id]
    
    # Create temporary file
    filename = f"analysis_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = f"/tmp/{filename}"
    
    with open(filepath, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/api/compare', methods=['POST'])
def compare_reports():
    """Compare two earnings reports"""
    try:
        data = request.get_json()
        current_text = data.get('current_report', '')
        previous_text = data.get('previous_report', '')
        company_name = data.get('company_name', '')
        
        provider = data.get('provider', 'anthropic')

        if not current_text or not previous_text:
            return jsonify({'error': 'Both reports required'}), 400

        analyzer = EarningsReportAnalyzer(provider=provider)
        comparison = analyzer.compare_earnings(current_text, previous_text, company_name)
        return jsonify(comparison)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Starting Earnings Report Analyzer Web Dashboard")
    print("="*70)
    print("\n📍 Access the dashboard at: http://localhost:5000")
    print("\n💡 Set API keys for your providers as environment variables:")
    print("   ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY")
    print("\nPress CTRL+C to stop the server\n")
    
    app.run(debug=True, port=5000)
