# weather-station
This is a set of programs used to process weather station data from fishing vessels.

We keep a flowchart using drawio utility at:

https://app.diagrams.net/?state=%7B%22ids%22:%5B%220B1OaSh7qfuwqSTNQaGhCcGVwaWs%22%5D,%22action%22:%22open%22,%22userId%22:%22100669986945318687835%22%7D#G0B1OaSh7qfuwqSTNQaGhCcGVwaWs

but a pdf version is sometimes updated in this repository.

The most important programs "weatherplots2.py" the acquisition routine that  is running on at least one vessel.

The two routines to process telemetered data are:

"getap32weather.py" which reads the json files already downloaded to the NOAA machine and outputs a "weather_ap3.dat" ascii file
"plot_realtime_weather.py" which reads weather_ap3.dat".
