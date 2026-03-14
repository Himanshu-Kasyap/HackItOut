import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_future(df, variable, city=None, years_ahead=10):
    """
    Fit a linear regression on yearly averages and predict future values.
    Returns historical + predicted data points.
    """
    filt = df.copy()

    if city and 'city' in filt.columns:
        filt = filt[filt['city'] == city]

    if variable not in filt.columns or 'year' not in filt.columns:
        return {'historical': [], 'predicted': [], 'r2': None}

    yearly = filt.groupby('year')[variable].mean().reset_index()
    yearly = yearly.sort_values('year').dropna()

    if len(yearly) < 3:
        return {'historical': [], 'predicted': [], 'r2': None}

    X = yearly['year'].values.reshape(-1, 1)
    y = yearly[variable].values

    model = LinearRegression()
    model.fit(X, y)
    r2 = round(float(model.score(X, y)), 4)

    last_year = int(yearly['year'].max())
    future_years = np.arange(last_year + 1, last_year + years_ahead + 1).reshape(-1, 1)
    future_preds = model.predict(future_years)

    historical = [
        {'year': int(r['year']), 'value': round(float(r[variable]), 3)}
        for _, r in yearly.iterrows()
    ]
    predicted = [
        {'year': int(future_years[i][0]), 'value': round(float(future_preds[i]), 3)}
        for i in range(len(future_years))
    ]

    slope = round(float(model.coef_[0]), 4)
    trend_desc = (
        f"Linear trend: {variable.replace('_', ' ')} changes by {slope:+.4f} units/year. "
        f"Model R² = {r2}."
    )

    return {
        'historical': historical,
        'predicted': predicted,
        'r2': r2,
        'slope': slope,
        'trend_description': trend_desc,
    }
