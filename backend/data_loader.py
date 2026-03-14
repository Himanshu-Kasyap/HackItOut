import pandas as pd
import numpy as np
import os

UPLOAD_FOLDER = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasets'))

def load_csv(filepath):
    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    return df

def load_dataset(filename=None):
    if filename:
        path = os.path.join(UPLOAD_FOLDER, filename)
        ext = os.path.splitext(path)[1].lower()
        if ext == '.csv':
            return load_csv(path)
        elif ext in ('.nc', '.nc4'):
            return load_netcdf(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    else:
        # Load both sample parts and combine them
        part1 = os.path.join(UPLOAD_FOLDER, 'sample_climate_data_part1.csv')
        part2 = os.path.join(UPLOAD_FOLDER, 'sample_climate_data_part2.csv')
        return pd.concat([load_csv(part1), load_csv(part2)], ignore_index=True)

def load_netcdf(filepath):
    try:
        import xarray as xr
        ds = xr.open_dataset(filepath)
        df = ds.to_dataframe().reset_index()
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        df = _normalize_time(df)
        return df
    except ImportError:
        raise ImportError("xarray is required to load NetCDF files.")

def _normalize_time(df):
    """Extract year/month from a 'time' or 'date' datetime column if present."""
    time_col = next((c for c in df.columns if c in ('time', 'date', 'datetime')), None)
    if time_col and 'year' not in df.columns:
        try:
            dt = pd.to_datetime(df[time_col], errors='coerce')
            df['year'] = dt.dt.year
            df['month'] = dt.dt.month
        except Exception:
            pass
    return df

def get_available_variables(df):
    exclude = {'year', 'month', 'week', 'latitude', 'longitude', 'lat', 'lon', 'time'}
    return [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]

def get_year_range(df):
    if 'year' in df.columns:
        years = df['year'].dropna()
        if len(years):
            return int(years.min()), int(years.max())
    return None, None

def get_cities(df):
    if 'city' in df.columns:
        return sorted(df['city'].dropna().unique().tolist())
    return []

def has_city_data(df):
    return 'city' in df.columns and df['city'].notna().any()

def get_lat_lon_samples(df, n=20):
    """Return a sample of unique lat/lon points for NetCDF datasets."""
    lat_col = _find_col(df, ['latitude', 'lat'])
    lon_col = _find_col(df, ['longitude', 'lon'])
    if not lat_col or not lon_col:
        return []
    pts = df[[lat_col, lon_col]].drop_duplicates()
    if len(pts) > n:
        pts = pts.sample(n, random_state=42)
    return [{'lat': round(float(r[lat_col]), 3), 'lon': round(float(r[lon_col]), 3)}
            for _, r in pts.iterrows()]

def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None
