import pandas as pd
import numpy as np

def get_heatmap_data(df, variable, year=None, month=None):
    filt = df.copy()
    if year and 'year' in filt.columns:
        filt = filt[filt['year'] == int(year)]
    if month and 'month' in filt.columns:
        filt = filt[filt['month'] == int(month)]

    lat_col = _find_col(filt, ['latitude', 'lat'])
    lon_col = _find_col(filt, ['longitude', 'lon'])
    city_col = 'city' if 'city' in filt.columns else None

    if not lat_col or not lon_col or variable not in filt.columns:
        return []

    group_cols = [lat_col, lon_col]
    if city_col:
        group_cols.append(city_col)

    agg = filt.groupby(group_cols)[variable].mean().reset_index()

    # For large NetCDF grids, sample down to ~500 points for performance
    if len(agg) > 500:
        agg = agg.sample(500, random_state=42)

    result = []
    for _, row in agg.iterrows():
        entry = {
            'lat': round(float(row[lat_col]), 4),
            'lon': round(float(row[lon_col]), 4),
            'value': round(float(row[variable]), 3),
        }
        if city_col:
            entry['city'] = row[city_col]
        result.append(entry)
    return result


def get_time_series(df, variable, city=None, lat=None, lon=None):
    filt = df.copy()

    lat_col = _find_col(filt, ['latitude', 'lat'])
    lon_col = _find_col(filt, ['longitude', 'lon'])

    if city and 'city' in filt.columns:
        filt = filt[filt['city'] == city]
    elif lat is not None and lon is not None:
        # Snap to nearest grid point
        if lat_col and lon_col:
            filt['_dist'] = ((filt[lat_col] - float(lat))**2 + (filt[lon_col] - float(lon))**2)**0.5
            nearest = filt.loc[filt['_dist'].idxmin()]
            filt = filt[(filt[lat_col] == nearest[lat_col]) & (filt[lon_col] == nearest[lon_col])]
    elif lat_col and lon_col and 'city' not in filt.columns:
        # No location specified — pick the first unique lat/lon point
        first_lat = filt[lat_col].iloc[0]
        first_lon = filt[lon_col].iloc[0]
        filt = filt[(filt[lat_col] == first_lat) & (filt[lon_col] == first_lon)]

    if variable not in filt.columns:
        return []

    # Build time axis
    if 'year' in filt.columns and 'month' in filt.columns:
        filt = filt.copy()
        filt['date'] = pd.to_datetime(
            filt[['year', 'month']].assign(day=1).rename(columns={'year': 'year', 'month': 'month'})
        )
        ts = filt.groupby('date')[variable].mean().reset_index().sort_values('date')
        return [{'date': str(r['date'].date()), 'value': round(float(r[variable]), 3)} for _, r in ts.iterrows()]

    elif 'year' in filt.columns:
        ts = filt.groupby('year')[variable].mean().reset_index().sort_values('year')
        return [{'date': str(int(r['year'])), 'value': round(float(r[variable]), 3)} for _, r in ts.iterrows()]

    elif 'time' in filt.columns:
        filt = filt.copy()
        filt['time'] = pd.to_datetime(filt['time'], errors='coerce')
        ts = filt.groupby('time')[variable].mean().reset_index().sort_values('time')
        return [{'date': str(r['time'].date()), 'value': round(float(r[variable]), 3)} for _, r in ts.iterrows()]

    return []


def get_comparison_data(df, variable, year1, year2):
    return {
        'year1': get_heatmap_data(df, variable, year=year1),
        'year2': get_heatmap_data(df, variable, year=year2),
    }


def get_ai_insights(df, variable, city=None):
    insights = []
    filt = df.copy()

    if city and 'city' in filt.columns:
        filt = filt[filt['city'] == city]

    if variable not in filt.columns:
        return ['Insufficient data for analysis.']

    # Build yearly series
    if 'year' in filt.columns:
        yearly = filt.groupby('year')[variable].mean().dropna()
    elif 'time' in filt.columns:
        filt['_year'] = pd.to_datetime(filt['time'], errors='coerce').dt.year
        yearly = filt.groupby('_year')[variable].mean().dropna()
        yearly.index.name = 'year'
    else:
        return ['No time dimension found for trend analysis.']

    if len(yearly) < 2:
        return ['Not enough yearly data to generate insights.']

    label = variable.replace('_', ' ')
    first_val, last_val = yearly.iloc[0], yearly.iloc[-1]
    delta = last_val - first_val
    direction = 'increased' if delta > 0 else 'decreased'
    insights.append(
        f"Average {label} {direction} by {abs(delta):.2f} units "
        f"between {int(yearly.index[0])} and {int(yearly.index[-1])}."
    )

    peak_year = int(yearly.idxmax())
    insights.append(f"Highest average {label} recorded in {peak_year} ({yearly.max():.2f}).")

    low_year = int(yearly.idxmin())
    insights.append(f"Lowest average {label} recorded in {low_year} ({yearly.min():.2f}).")

    mean_val, std_val = yearly.mean(), yearly.std()
    anomalies = yearly[abs(yearly - mean_val) > 2 * std_val]
    if not anomalies.empty:
        years_str = ', '.join(str(y) for y in anomalies.index.tolist())
        insights.append(f"Anomalous {label} values detected in: {years_str}.")
    else:
        insights.append(f"No significant anomalies detected in {label} over the period.")

    if len(yearly) >= 20:
        first_decade = yearly[yearly.index <= yearly.index[0] + 9].mean()
        last_decade = yearly[yearly.index >= yearly.index[-1] - 9].mean()
        d_change = last_decade - first_decade
        d_dir = 'higher' if d_change > 0 else 'lower'
        insights.append(
            f"The most recent decade averages {abs(d_change):.2f} units {d_dir} than the earliest decade."
        )

    return insights


def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None
