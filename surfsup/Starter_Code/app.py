# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import pandas as pd

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in the data set
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = dict(precipitation_data)

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations_data = session.query(Station.station, Station.name).all()

    # Convert the query results to a list of dictionaries
    stations_list = [{"station": station, "name": name} for station, name in stations_data]

    # Return JSON representation of the list
    return jsonify(stations_list)

# TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query dates and temperature observations of the most-active station for the previous year of data
    most_active_station_id = 'USC00519281'
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]

    # Return JSON representation of the list
    return jsonify(tobs_list)

# Start route
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Your code for calculating TMIN, TAVG, and TMAX for start date to the end of the dataset
        # Convert the start date to a datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # Query TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # Convert the query results to a dictionary
    temp_stats_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }

    # Return JSON representation of the dictionary
    return jsonify(temp_stats_dict)

# Start and end route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Your code for calculating TMIN, TAVG, and TMAX for start date to end date (inclusive)
     # Convert the start date to a datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # If end date is provided, convert it to a datetime object
    if end:
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    else:
        # If end date is not provided, calculate stats for a single date (start date)
        end_date = start_date

    # Query TMIN, TAVG, and TMAX for dates within the specified range
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert the query results to a dictionary
    temp_stats_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }

    # Return JSON representation of the dictionary
    return jsonify(temp_stats_dict)

if __name__ == "__main__":
    app.run(debug=True)