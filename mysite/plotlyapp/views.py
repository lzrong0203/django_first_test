from django.shortcuts import render
import plotly.offline as pyo
import plotly.graph_objs as go
from firebase_admin import db
import pandas as pd
import yfinance as yf
from datetime import datetime


def plotly_chart(request):
    # 讀取 Firebase 數據
    ref = db.reference('/')
    firebase_data = ref.get()
    df = pd.read_json(firebase_data)
    conversion_dict = {
        "neutral": 0,
        "positive": 1,
        "negative": -1
    }

    df['sentiment_num'] = df['sentiment'].replace(conversion_dict)
    df["time"] = pd.to_datetime(df["time"], unit='ms')

    result = df.groupby(pd.Grouper(key='time', freq='1T'))['sentiment_num'].mean().reset_index()

    gold = yf.download(tickers="^TWII", period="5d", interval="1m")

    start = datetime(2023, 6, 7, 9, 30, 0)
    end = datetime(2023, 6, 7, 13, 30, 0)

    TWII = gold[start: end]
    TWII['Close_diff'] = (TWII['Close'] - TWII['Close'].shift(1))
    s_mean = result[1:236]["sentiment_num"].mean()
    s_std = result[1:236]["sentiment_num"].std()
    twii_mean = TWII.Close_diff[1:236].mean()
    twii_std = TWII.Close_diff[1:236].std()
    df1 = (result[1:236]["sentiment_num"] - s_mean) / s_std
    df2 = (TWII.Close_diff[1:236] - twii_mean) / twii_std

    trace1 = go.Scatter(y=df1, mode="lines")
    trace2 = go.Scatter(y=df2, mode="lines")
    layout = go.Layout(title='Firebase Data')
    figure = go.Figure(data=[trace1, trace2], layout=layout)
    plot_div = pyo.plot(figure, output_type='div')

    return render(request, "plotly_chart.html", context={'plot_div': plot_div})
