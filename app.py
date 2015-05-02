# requires the following packages installed.
# Flask, Flask-OAuthlib
# to test locally with out SSL, set environment variable DEBUG=true
 
from flask import Flask, request, url_for, session, jsonify, redirect, Response, render_template
from flask_oauthlib.client import OAuth
from collections import defaultdict
import pandas as pd
import numpy as np
import json
import urllib
import time
import config_production #TODO create this file

WoTKitApp = Flask(__name__)
WoTKitApp.config.from_object('config_production.ProductionConfig')

WoTKitApp.secret_key = WoTKitApp.config['CONSUMER_SECRET']
oauth = OAuth(WoTKitApp)

wotkit = oauth.remote_app('wotkit',
    base_url='https://wotkit.sensetecnic.com/api/',
    request_token_url=None,
    access_token_url='https://wotkit.sensetecnic.com/api/oauth/token',
    authorize_url='https://wotkit.sensetecnic.com/api/oauth/authorize',
    consumer_key=WoTKitApp.config['CONSUMER_KEY'], 
    consumer_secret=WoTKitApp.config['CONSUMER_SECRET'], 
    request_token_params={'scope': ['all']}, #Request access to all.
    access_token_params={'scope': ['all']} #Request access to all.
)

@wotkit.tokengetter
def get_wotkit_token(token=None):
    return session.get('wotkit_token')

@WoTKitApp.route('/login')
def login():
    return wotkit.authorize(callback=url_for('oauth_authorized', _external=True))

@WoTKitApp.route('/')
def index():
    if 'wotkit_token' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@WoTKitApp.route('/oauth-authorized')
@wotkit.authorized_handler
def oauth_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['wotkit_token'] = (resp['access_token'], '')
    return redirect('/')

# 
@WoTKitApp.route('/api/search', methods=['GET'])
def search():
    """A simple API endpoint to compare data from two sensors
       Example http://127.0.0.1:5000/api/search?text=sensoraname
    """
    if 'wotkit_token' in session:
        text = request.args.get('text')
        if (text):
            data = WoTKitsearchSensor(text)
            json_response = json.dumps(data)
            return Response(json_response, content_type='application/json')
        return """You must provide a search text. Example: 
               http://127.0.0.1:5000/api/search?text=sensoraname"""
    return redirect(url_for('login'))

# TODO: finish this 
@WoTKitApp.route('/api/correlation', methods=['GET'])
def analysis():
    """ A simple API endpoint to compare data from two sensors
        Example http://127.0.0.1:5000/api/stats/compare?a=sensoraname&b=sensorbname
    """

    if 'wotkit_token' in session:

        a = request.args.get('a')
        b = request.args.get('b')
        hours = int(request.args.get('hours'))
        
        if (a and b and hours):
            
            msph = 3600000 #milliseconds per hour
            result = defaultdict(dict)
            
            sensoraDataSeries = WotKitDataToSeries(WoTKitgetSensorData(a, msph*hours))
            sensorbDataSeries = WotKitDataToSeries(WoTKitgetSensorData(b, msph*hours))
           
            # Labels object
            result['labels'] = [`i`+"h" for i in range(1,hours)]

            # Sensor A object             
            sensoraDailyMeans = sensoraDataSeries.resample('H', how = 'mean')
            result['a']['mean'] = SeriesToList( sensoraDailyMeans )
            result['a']['rolling_mean'] = SeriesToList( pd.rolling_mean(sensoraDailyMeans, 5) )
            result['a']['rolling_stdev'] = SeriesToList( pd.rolling_std(sensoraDailyMeans, 5) )
            result['a']['rolling_skewness'] = SeriesToList( pd.rolling_skew(sensoraDailyMeans, 5) )
            result['a']['rolling_kurtosis'] = SeriesToList( pd.rolling_kurt(sensoraDailyMeans, 5) )

            #Sensor B object         
            sensorbDailyMeans = sensorbDataSeries.resample('H', how = 'mean')
            result['b']['mean'] = SeriesToList(sensorbDailyMeans)
            result['b']['rolling_mean'] = SeriesToList( pd.rolling_mean(sensorbDailyMeans, 5) )
            result['b']['rolling_stdev'] = SeriesToList( pd.rolling_std(sensorbDailyMeans, 5) )
            result['b']['rolling_skewness'] = SeriesToList( pd.rolling_skew(sensorbDailyMeans, 5) )
            result['b']['rolling_kurtosis'] = SeriesToList( pd.rolling_kurt(sensorbDailyMeans, 5) )
            
            #Comparison object
            result['comparison']['correlation'] = SeriesToList( pd.rolling_corr(sensoraDailyMeans, sensorbDailyMeans, 5) )
            result['comparison']['covariance'] = SeriesToList( pd.rolling_cov(sensoraDailyMeans, sensorbDailyMeans, 5) )         
          
            json_response = json.dumps(result)

            return Response(json_response, content_type='application/json')
        return """You must provide two sensors. Example: 
               http://127.0.0.1:5000/api/compare?a=sensoraname&b=sensorbname&hours=12"""
    return redirect(url_for('login'))




## External API Methods

def WoTKitgetSensorData(sensorname, before):
    """Get Sensor Data from WoTKit.

    :param sensorname: The name or id of the sensor
    :param beofre: Before parameter in milliseconds (e.g. 86400000 = 1 day)
    :returns: The data object return from WoTKit 
    """
    rawdata = wotkit.get('v1/sensors/'+str(sensorname)+'/data?before='+str(before))
    return rawdata.data

def WoTKitsearchSensor(text):
    """Get Sensor Data from WoTKit.

    :param text: The text to search
    :returns: The data object return from WoTKit 
    """
    rawdata = wotkit.get('v1/sensors?text='+urllib.quote_plus(text))
    return rawdata.data

def WotKitDataToSeries(data):
    """Get a Pandas Series object from a WoTKit sensor data response
    
    :param data: A data object from the WoTKit
    :returns: A Pandas Series object with timestamp as index
    """
    result = pd.Series()
    for i,element in enumerate(data):
        if "value" in element:
            timestamp = pd.to_datetime(element["timestamp_iso"]) 
            value = element["value"]
            result.set_value(timestamp, value)
    return result
    
def SeriesToList(series):
    """ Clean data (NaN and Infinity) and turn into a list
    :param series: A Pandas series object
    :returns: A list of elements, cleaned of Infinity and NaN (replaced by 0)
    """
    return series.replace([np.inf, -np.inf], np.nan).fillna(0).tolist()

if __name__ == "__main__":
    WoTKitApp.run()
