# Import the dependencies.
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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine) 

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    previous_year = dt.date(2017,8,23) - dt.timedelta(days = 365)
    results = session.query(measurement.date,measurement.prcp).filter(measurement.date >= previous_year).all()
    session.close()
    precip = {}
    precip["date"] = [x[0] for x in results]
    precip["precipitation"] = [x[1] for x in results]
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(measurement.station).group_by(measurement.station).all()
    session.close()
    station_list = {}
    station_list["stations"] = [x[0] for x in results]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    start_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    
    results = session.query(measurement.tobs).filter(measurement.date >= start_date).filter(measurement.station == 'USC00519281').all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None,end=None):
    var = [func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)]
    if not end:
        start = dt.datetime.strptime(start,'%Y%m%d')
        results = session.query(*var).filter(measurement.date >= start).all()
        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps)
    start = dt.datetime.strptime(start,'%Y%m%d')
    end = dt.datetime.strptime(end,'%Y%m%d')
    results = session.query(*var).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)






if __name__ == "__main__":
    app.run(debug=True)

