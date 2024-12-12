# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # query last 12 months of precipitation data
    precip = session.query(Measurement.date, func.Max(Measurement.prcp)).\
        filter(Measurement.date > '2016-08-22').\
        filter(Measurement.prcp != None).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    # prepare the data into a dictionary
    outputDict = {}
    
    for p in precip:
        outputDict[p[0]] = p[1]

    return jsonify(outputDict)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()

    # Convert data into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # query last 12 months of precipitation data for most active station
    precip = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > '2016-08-22').\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.tobs != None).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    # prepare the data into a list
    outputList = []
    
    for p in precip:
        outputList.append({
            p.date : p.tobs
        })

    return jsonify(outputList)

@app.route("/api/v1.0/<start>")
def start(start):
    # Test whether the start date is valid
    try:
        startDate = dt.datetime.strptime(start, '%Y-%m-%d')
    except:
        return jsonify({"error": "Invalid date format: YYYY-MM-DD"}), 400
    
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date.
    activeData = session.query(func.Min(Measurement.tobs), func.Avg(Measurement.tobs), func.Max(Measurement.tobs)).\
        filter(Measurement.date >= start).first()

    return jsonify(list(np.ravel(activeData)))

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    # Test whether the start or end date is valid
    try:
        startDate = dt.datetime.strptime(start, '%Y-%m-%d')
        endDate = dt.datetime.strptime(end, '%Y-%m-%d')
    except:
        return jsonify({"error": "Invalid date format: YYYY-MM-DD"}), 400
    
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start and end date.
    activeData = session.query(func.Min(Measurement.tobs), func.Avg(Measurement.tobs), func.Max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).first()

    return jsonify(list(np.ravel(activeData)))

# Start the application
if __name__ == "__main__":
    app.run(debug=True)
