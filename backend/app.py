import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from data_loader import (load_dataset, get_available_variables, get_year_range,
                         get_cities, get_lat_lon_samples, has_city_data)
from climate_analysis import get_heatmap_data, get_time_series, get_comparison_data, get_ai_insights
from ml_model import predict_future

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'frontend'))
DATASETS_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'datasets'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

ALLOWED_EXTENSIONS = {'csv', 'nc', 'nc4'}

# ── DataFrame cache ───────────────────────────────────────────────────────────
# Loaded once at startup; replaced only when user uploads a new file.
_cache = {'df': None, 'active_file': None}

def _load_cache(filename=None):
    log.info(f"Loading dataset: {filename or 'sample (both parts)'}")
    _cache['df'] = load_dataset(filename)
    _cache['active_file'] = filename
    log.info(f"Dataset loaded — {len(_cache['df']):,} rows")

def get_df():
    if _cache['df'] is None:
        _load_cache()
    return _cache['df']

# Pre-load sample data at startup so first request is fast
with app.app_context():
    try:
        _load_cache()
    except Exception as e:
        log.warning(f"Could not pre-load sample data: {e}")

# ── Helpers ───────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def active_file_label():
    return _cache['active_file'] or 'sample_climate_data (part1 + part2)'

# ── Frontend ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(target):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ── API ───────────────────────────────────────────────────────────────────────

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type. Use CSV or NetCDF.'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(DATASETS_DIR, filename)
    file.save(save_path)

    try:
        _load_cache(filename)
        df = get_df()
        return jsonify({
            'message': f'Dataset "{filename}" loaded successfully.',
            'rows': len(df),
            'variables': get_available_variables(df),
            'year_min': get_year_range(df)[0],
            'year_max': get_year_range(df)[1],
            'cities': get_cities(df),
            'lat_lon_points': get_lat_lon_samples(df) if not get_cities(df) else [],
        })
    except Exception as e:
        log.exception("upload_dataset error")
        return jsonify({'error': str(e)}), 500


@app.route('/reset_dataset', methods=['POST'])
def reset_dataset():
    try:
        _load_cache(None)
        df = get_df()
        return jsonify({
            'message': 'Reset to sample dataset.',
            'variables': get_available_variables(df),
            'year_min': get_year_range(df)[0],
            'year_max': get_year_range(df)[1],
            'cities': get_cities(df),
            'lat_lon_points': [],
            'active_file': active_file_label(),
        })
    except Exception as e:
        log.exception("reset_dataset error")
        return jsonify({'error': str(e)}), 500


@app.route('/get_dataset_info', methods=['GET'])
def get_dataset_info():
    try:
        df = get_df()
        return jsonify({
            'variables': get_available_variables(df),
            'year_min': get_year_range(df)[0],
            'year_max': get_year_range(df)[1],
            'cities': get_cities(df),
            'lat_lon_points': get_lat_lon_samples(df) if not get_cities(df) else [],
            'active_file': active_file_label(),
        })
    except Exception as e:
        log.exception("get_dataset_info error")
        return jsonify({'error': str(e)}), 500


@app.route('/get_heatmap_data', methods=['GET'])
def heatmap_data():
    variable = request.args.get('variable', 'temperature')
    year     = request.args.get('year')
    month    = request.args.get('month')
    try:
        data = get_heatmap_data(get_df(), variable, year=year, month=month)
        return jsonify({'data': data, 'variable': variable})
    except Exception as e:
        log.exception("get_heatmap_data error")
        return jsonify({'error': str(e)}), 500


@app.route('/get_time_series', methods=['GET'])
def time_series():
    variable = request.args.get('variable', 'temperature')
    city     = request.args.get('city')
    lat      = request.args.get('lat')
    lon      = request.args.get('lon')
    try:
        data = get_time_series(get_df(), variable, city=city, lat=lat, lon=lon)
        return jsonify({'data': data, 'variable': variable, 'location': city or f'{lat},{lon}'})
    except Exception as e:
        log.exception("get_time_series error")
        return jsonify({'error': str(e)}), 500


@app.route('/get_ai_insights', methods=['GET'])
def ai_insights():
    variable = request.args.get('variable', 'temperature')
    city     = request.args.get('city')
    try:
        insights = get_ai_insights(get_df(), variable, city=city)
        return jsonify({'insights': insights, 'variable': variable, 'location': city or 'Global'})
    except Exception as e:
        log.exception("get_ai_insights error")
        return jsonify({'error': str(e)}), 500


@app.route('/get_comparison_data', methods=['GET'])
def comparison_data():
    variable = request.args.get('variable', 'temperature')
    year1    = request.args.get('year1')
    year2    = request.args.get('year2')
    if not year1 or not year2:
        return jsonify({'error': 'year1 and year2 are required'}), 400
    try:
        data = get_comparison_data(get_df(), variable, year1, year2)
        return jsonify({'data': data, 'variable': variable, 'year1': year1, 'year2': year2})
    except Exception as e:
        log.exception("get_comparison_data error")
        return jsonify({'error': str(e)}), 500


@app.route('/get_future_prediction', methods=['GET'])
def future_prediction():
    variable   = request.args.get('variable', 'temperature')
    city       = request.args.get('city')
    years_ahead = int(request.args.get('years_ahead', 10))
    try:
        result = predict_future(get_df(), variable, city=city, years_ahead=years_ahead)
        return jsonify(result)
    except Exception as e:
        log.exception("get_future_prediction error")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'rows': len(_cache['df']) if _cache['df'] is not None else 0})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
