from flask import Flask, render_template, request, redirect
import pandas as pd
import requests

from bokeh.io import output_notebook, show
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.palettes import Spectral6
from bokeh.models import LinearAxis, Range1d

app = Flask(__name__)


# Figure generator
def build_figure(stock,data_selected):
    
    # mLoad ticker data from Quandl
    r = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/{}/data.json?api_key=ci2N98mKjYsH1WaQJyc-'.format(stock))
    data = r.json()['dataset_data']['data']
    
    # Place data in Pandas dataframe
    df = pd.DataFrame(data)
    labels = r.json()['dataset_data']['column_names']
    df.columns = labels
    df.Date = pd.to_datetime(df.Date)
    
    # Make a figure object
    numlines = len(data_selected)
    palette = Spectral6[0:numlines]
    p = figure(plot_width=400,plot_height=400,x_axis_type='datetime',title='Stock prices for {}'.format(stock))

    # add a line renderer
    for index in range(numlines):
        instring = data_selected[index]

        # assumes input in the format Type_MA00 (e.g. Open_MA30)
        if 'MA' in instring:
            operator = instring.split('_')
            duration = int(request.form.get("days"))
            MA = df[operator[0]].iloc[::-1].rolling(duration).sum()/duration
            p.line(df['Date'][MA.isnull()==False].head(200),
                   MA[MA.isnull()==False].tail(200).iloc[::-1],
                   line_width=2,
                   line_color=palette[index],
                   alpha=0.4,
                   legend=data_selected[index])        

        else:
            p.line(df['Date'].head(200),
                  df[instring].head(200),
                  line_width=2,
                  line_color=palette[index],
                  alpha=0.4,
                  legend=data_selected[index])

        # Set plot parameters and return plot
    p.xgrid.grid_line_color=None
    p.ygrid.grid_line_alpha = 0.6
    p.xaxis.axis_label='Time'
    p.yaxis.axis_label='Value (USD)'
    
    return p

# Main page
@app.route('/')
def index():
    return render_template('index.html', title='Stock Ticker App')

@app.route('/plot', methods=['GET','POST'])
def plot():
    if request.method == 'POST':
        stock = request.form.get("ticker")
        data_selected = request.form.getlist("features")
        plot = build_figure(stock,data_selected)
        script, div = components(plot)
        return render_template("plot.html", title='Stock Prices for {}'.format(stock), script=script, div=div)

if __name__ == '__main__':
    app.run(port=33507)
