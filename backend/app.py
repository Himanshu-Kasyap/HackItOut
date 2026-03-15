import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from data_loader import (load_dataset, get_available_variables, get_year_range,
                         get_cities, get_lat_lon_samples, has_city_data)
from climate_analysis import get_heatmap_data, get_time_series, get_comparison_data, get_ai_insights
from ml_model import predict_future

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
DATASETS_DIR = os.path.join(BASE_DIR, '..', 'datasets')

app = Flask(__name__, static_folder=os.path.normpath(FRONTEND_DIR), static_url_path='')
CORS(app)
ALLOWED_EXTENSIONS = {'csv', 'nc', 'nc4'}

# Always start with the sample dataset — never inherit a stale uploaded file
_state = {'active_file': None}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_df():
    return load_dataset(_state.get('active_file'))


# ── Serve frontend ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(os.path.normpath(FRONTEND_DIR), 'index.html')

@app.route('/<path:path>')
def static_files(path):
    full = os.path.join(os.path.normpath(FRONTEND_DIR), path)
    if os.path.exists(full):
        return send_from_directory(os.path.normpath(FRONTEND_DIR), path)
    return send_from_directory(os.path.normpath(FRONTEND_DIR), 'index.html')


# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type. Use CSV or NetCDF.'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(DATASETS_DIR, filename)
    file.save(save_path)
    _state['active_file'] = filename

    try:
        df = get_df()
        variables = get_available_variables(df)
        year_min, year_max = get_year_range(df)
        cities = get_cities(df)
        lat_lon_points = get_lat_lon_samples(df) if not cities else []
        return jsonify({
            'message': f'Dataset "{filename}" loaded successfully.',
            'rows': len(df),
            'variables': variables,
            'year_min': year_min,
            'year_max': year_max,
            'cities': cities,
            'lat_lon_points': lat_lon_points,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reset_dataset', methods=['POST'])
def reset_dataset():
    _state['active_file'] = None
    try:
        df = get_df()
        variables = get_available_variables(df)
        year_min, year_max = get_year_range(df)
        cities = get_cities(df)
        return jsonify({
            'message': 'Reset to sample dataset.',
            'variables': variables,
            'year_min': year_min,
            'year_max': year_max,
            'cities': cities,
            'lat_lon_points': [],
            'active_file': 'sample_climate_data_part1.csv + part2.csv',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_dataset_info', methods=['GET'])
def get_dataset_info():
    try:
        df = get_df()
        variables = get_available_variables(df)
        year_min, year_max = get_year_range(df)
        cities = get_cities(df)
        lat_lon_points = get_lat_lon_samples(df) if not cities else []
        return jsonify({
            'variables': variables,
            'year_min': year_min,
            'year_max': year_max,
            'cities': cities,
            'lat_lon_points': lat_lon_points,
            'active_file': _state.get('active_file') or 'sample_climate_data_part1.csv + part2.csv',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_heatmap_data', methods=['GET'])
def heatmap_data():
    variable = request.args.get('variable', 'temperature')
    year = request.args.get('year')
    month = request.args.get('month')
    try:
        df = get_df()
        data = get_heatmap_data(df, variable, year=year, month=month)
        return jsonify({'data': data, 'variable': variable})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_time_series', methods=['GET'])
def time_series():
    variable = request.args.get('variable', 'temperature')
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    try:
        df = get_df()
        data = get_time_series(df, variable, city=city, lat=lat, lon=lon)
        return jsonify({'data': data, 'variable': variable, 'location': city or f'{lat},{lon}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_ai_insights', methods=['GET'])
def ai_insights():
    variable = request.args.get('variable', 'temperature')
    city = request.args.get('city')
    try:
        df = get_df()
        insights = get_ai_insights(df, variable, city=city)
        return jsonify({'insights': insights, 'variable': variable, 'location': city or 'Global'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_comparison_data', methods=['GET'])
def comparison_data():
    variable = request.args.get('variable', 'temperature')
    year1 = request.args.get('year1')
    year2 = request.args.get('year2')
    if not year1 or not year2:
        return jsonify({'error': 'year1 and year2 are required'}), 400
    try:
        df = get_df()
        data = get_comparison_data(df, variable, year1, year2)
        return jsonify({'data': data, 'variable': variable, 'year1': year1, 'year2': year2})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_future_prediction', methods=['GET'])
def future_prediction():
    variable = request.args.get('variable', 'temperature')
    city = request.args.get('city')
    years_ahead = int(request.args.get('years_ahead', 10))
    try:
        df = get_df()
        result = predict_future(df, variable, city=city, years_ahead=years_ahead)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
