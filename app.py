import os

from flask import Flask, render_template
import plotly.graph_objects as go
import pandas as pd

from script import binance, perform_script

app = Flask(__name__)


def get_newest_csv():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(file_dir, "data")
    try:
        files = os.listdir(data_folder)
    except FileNotFoundError:
        return None

    csv_files = [file for file in files if file.endswith(".csv")]
    csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(data_folder, x)))

    return os.path.join(data_folder, csv_files[-1]) if csv_files else None


@app.route('/')
def index():
    newest_csv = get_newest_csv()
    if not newest_csv:
        perform_script()
        newest_csv = get_newest_csv()
    filename = os.path.basename(newest_csv)
    df = pd.read_csv(newest_csv)
    df['Kline open time'] = pd.to_datetime(df['Kline open time'], unit='ms')

    candlestick = go.Candlestick(
        x=df['Kline open time'],
        open=df['Open price'],
        high=df['High price'],
        low=df['Low price'],
        close=df['Close price'],
    )

    fig = go.Figure(data=[candlestick])

    fig.update_layout(
        title=f'Candlestick Chart ({filename})',
        yaxis_title='Price',
        template='plotly_dark'
    )

    graph_html = fig.to_html()

    market_caps = binance.get_market_caps()
    symbols, caps = zip(*market_caps)
    pie_chart = go.Pie(
        labels=symbols,
        values=caps,
        hole=0.4,
        name='Market Caps'
    )

    fig2 = go.Figure(data=[pie_chart])
    fig2.update_layout(
        title='Market Caps',
        template='plotly_dark'
    )
    piechart_html = fig2.to_html()

    return render_template('index.html', graph_html=graph_html, piechart_html=piechart_html)


if __name__ == '__main__':
    app.run(debug=True)
