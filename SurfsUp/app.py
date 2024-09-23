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
        '<h1>Welcome to the Weather API!</h1>'
        '<h2>Available Routes:</h2>'
        '<ul>'
        f'<li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>'
        f'<li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>'
        f'<li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>'
        f'<li><a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-01</a> (example: start date)</li>'
        f'<li><a href="/api/v1.0/2017-01-01/2017-01-31">/api/v1.0/2017-01-01/2017-01-31</a> (example: start/end dates)</li>'
        '</ul>'
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
    # Query to get both station ID and station name
    stations_query = session.query(Station.station, Station.name).all()

    # Convert the query results into a list of dictionaries
    stations_list = [{"id": station[0], "name": station[1]} for station in stations_query]

    # Return the list as a JSON response
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

# Route for temperature from a given start date
@app.route('/api/v1.0/<start>', methods=['GET'])
def temperature_start(start):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
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

# Route for temperature from a given date range (start date to end date)
@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def temperature_start_end(start, end):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    
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

if __name__ == '__main__':
    app.run(debug=True)