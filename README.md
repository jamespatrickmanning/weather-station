# weather-station
This is a set of programs used to process weather station data from fishing vessels.

As of Nov 9, 2020, it is missing one of the most important programs "weatherplots2.py" that is running on at least one vessel.
The two routines to process telemetered data are:

"getap32weather.py" which reads the json files already downloaded to the NOAA machine and outputs a "weather_ap3.dat" ascii file
"plot_realtime_weather.py" which reads weather_ap3.dat".
