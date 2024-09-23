# Import dependencies
from flask import Flask, jsonify, abort
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np
import pandas as pd

#################################################
# Database Setup
#################################################

# Create engine and reflect the database tables
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route('/')
def home():
    return (
        f"Welcome to the Weather API!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/2017-01-01'>/api/v1.0/&lt;start&gt; (example: /api/v1.0/2017-01-01)</a><br/>"
        f"<a href='/api/v1.0/2017-01-01/2017-01-07'>/api/v1.0/&lt;start&gt;/&lt;end&gt; (example: /api/v1.0/2017-01-01/2017-01-07)</a><br/>"
    )

#################################################
# Flask Routes
#################################################

# Route for precipitation data
@app.route('/api/v1.0/precipitation', methods=['GET'])
def precipitation():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date_dt = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date_dt - dt.timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

# Route for station data
@app.route('/api/v1.0/stations', methods=['GET'])
def stations():
    stations_query = session.query(Station.station).all()
    stations_list = [station[0] for station in stations_query]
    return jsonify(stations_list)

# Route for temperature observations (tobs)
@app.route('/api/v1.0/tobs', methods=['GET'])
def tobs():
    most_active_station_id = 'USC00519281'
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date_dt = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date_dt - dt.timedelta(days=365)

    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).all()

    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in tobs_data]
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>', methods=['GET'])
def temperature_start(start):
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")

    temperature_stats = session.query(
        func.min(Measurement.tobs).label('tmin'),
        func.avg(Measurement.tobs).label('tavg'),
        func.max(Measurement.tobs).label('tmax')
    ).filter(Measurement.date >= start_date).all()

    result = {
        "tmin": temperature_stats[0].tmin,
        "tavg": temperature_stats[0].tavg,
        "tmax": temperature_stats[0].tmax
    }
    return jsonify(result)

@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def temperature_start_end(start, end):
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")

    temperature_stats = session.query(
        func.min(Measurement.tobs).label('tmin'),
        func.avg(Measurement.tobs).label('tavg'),
        func.max(Measurement.tobs).label('tmax')
    ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    result = {
        "tmin": temperature_stats[0].tmin,
        "tavg": temperature_stats[0].tavg,
        "tmax": temperature_stats[0].tmax
    }
    return jsonify(result)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
