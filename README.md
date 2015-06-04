This application uses NumPy and Pandas to analyze and visualize data from the WoTKit. We also use OAuth2 to access private sensor data.


![alt](https://raw.githubusercontent.com/SenseTecnic/wotkit-example-python-pandas/master/screenshot-wotkit-example-python-pandas.png)


## Getting Started

Install Flask using ``pip``. Flask is a microframework for Python applications (http://flask.pocoo.org/).

```
pip install Flask
```

Install Flask OAuth, a Flask extension that uses ``oauthlib`` to interact with remote OAuth applications (https://github.com/lepture/flask-oauthlib)

```
pip install Flask-OAuthlib
```

We need to install the python development libraries. In Ubuntu, you can do:

```
sudo apt-get install python-dev libxml2-dev libxslt-dev
```

We can now install pandas using ``pip``

```
pip install pandas
```

## Running the Application

You can now start the application with:

```
python app.py
```

and visit http://127.0.0.1:5000
