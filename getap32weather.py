# -*- coding: utf-8 -*-
"""
Created on 10 Sep 2018
-looks in AP3 JSON files that have already been downloaded to our disk and creates weather_ap3.dat 
-Appends the AP3 data to the data collected by AP2 units
-currently hardcoded to just deal with the two units on the F/V Illusion and F/V Lisa Ann III  in Sep 2018
-Modified April 19, 2019 to accomodate "b" being in index 18 on 

@author: JiM
"""

from matplotlib.dates import date2num
import time
import pytz
import sys
from dateutil import parser
import glob
import json
from datetime import datetime as dt
from datetime import timedelta as td
import numpy as np
import pandas as pd

#HARDOCDES#######################
pathout='/net/pubweb_html/drifter/'
at_dock=0#always zero
'''
ship=['F/V Illusion','F/V Illusion','F/V Lisa Ann III']
ships_esn=['300234065018590','300234065616910','300234065611620']# esn on transmitters sitting on the wheelhouses
call_sign=['WBA4557','WBA4557','WDB3573']	
vn=['  Vessel_9','  Vessel_9','  Vessel_5']
barop_correction=[3.5,3.5,0.0] # as requested by Larry Hubble on 9/18/2018

ship=['F/V Lisa Ann III','F/V Lisa Ann III']
ships_esn=['300234065611620','300234063372540']# esn on transmitters sitting on the wheelhouses
#' is the old AP3
call_sign=['WDB3573','WDB3573']	
vn=['  Vessel_5','  Vessel_5']
barop_correction=[0.0,0.0] # as requested by Larry Hubble on 9/18/2018
'''
ship=['F/V Lisa Ann III']
ships_esn=['300234065311980']# esn on transmitters sitting on the wheelhouses (was 300234063372540 until Fall 2019)
call_sign=['WDB3573']	
vn=['  Vessel_5']
barop_correction=[0.0] # as requested by Larry Hubble on 9/18/2018
'''
ship=['F/V Illusion']
ships_esn=['300234065018590']# esn on transmitters sitting on the wheelhouses
call_sign=['WBA4557']	
vn=['  Vessel_9']
barop_correction=[0.0] # as requested by Larry Hubble on 9/18/2018
'''
######
# python routine to email NWS with shipboard weather in particular format requested
def email_nws(ship,call_sign,datet,lat,lon,wdir,wspd,airt,humid,barop):
   #def email_nws(test):
   # 
   import smtplib
   #from datetime import datetime as dt
   from email.MIMEMultipart import MIMEMultipart
   from email.MIMEText import MIMEText
   from conversions import dd2dm

 
   fromaddr = "james.patrick.manning@gmail.com"
   #toaddr = "james.manning@noaa.gov"
   toaddr = "webship@noaa.gov"
 
   msg = MIMEMultipart()
 
   msg['From'] = fromaddr
   msg['To'] = toaddr
   msg['Subject'] =datet.strftime("%Y%m%d-%H%M%S.AWS") #"SUBJECT OF THE EMAIL"

   if lat<100.:#reformat to DDMM.MMMM
     (lat,lon)=dd2dm(lat,lon)
   
   datet2=datet.strftime('%m/%d/%Y,%H:%M:%S')
   #body = str(count)+" raw data files were transmitted by WIFI, Please Click this link to get your aquetec data\n https://drive.google.com/open?id=0BwmSjxiv9rYLUlhhWS1sN01LTUk"
   body = "<<<"+ship+","+datet2+">>>\n<,"+call_sign+",GPS-Lat,GPS-Lon,TrueWind-Dir-1HrAvg,TrueWind-Spd-1HrAvg,AirTemp-1HrAvg,RelHumidity-1HrAvg,BaroPressure-1HrAvg,SeaTemp-1HrAvg,Version,>\n<,none,DDMM.MMMMH,DDDMM.MMMMH,degrees,knots,Celcius,percent,millibars,Celcius,Version,>\n<,,"+"%.4f" % lat+"N,"+"%.4f" % lon+"W,"+str(wdir)+","+str(wspd)+","+str(airt)+","+str(humid)+","+str(barop)+",,getap2sweather.py,>\n"

   msg.attach(MIMEText(body, 'plain'))
 
 
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login(fromaddr, "F1shM0nger$!")  # your email address and password
   text = msg.as_string(ys.argv[1]==[])
   server.sendmail(fromaddr, toaddr, text)
   server.quit()

## MAIN PROGRAM ######
if (sys.argv[1]==[]) or (sys.argv[1]=='weather.dat'):
  print 'input expected as weather_ap3.dat'
  exit()
f_output=open(pathout+str(sys.argv[1]),'w') # outputs weather_ap3.dat 
#f_output.write('vessel,esn,mth,day,hr,mn,yd,lon,lat,alt,airt,humid,barop,wspd,wdir,year,at_dock_1\n')

# assumes data from the AssetLink FTP site is already dumped into /home/jmanning/py/backup
#files=sorted(glob.glob('/home/jmanning/py/backup/2018*.json'))
files=sorted(glob.glob('/home/jmanning/py/backup/2019*.json'))

for k in range(len(ship)): # loop through the number of ships with AP3 transmitters
  c=0
  icount=0
  date_all=[]
  for i in files: # this loops through all the json files in the backup directory
    with open(i) as data_file:    
       try:
         data = json.load(data_file)
         esn=data['momentForward'][0]['Device']['esn'].encode("utf-8")
         if (esn==ships_esn[k]): # F/V Illusion & F/V Lisa Ann III, respectively
           try:
              data_raw=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex']
           except:
              data_raw=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][3]['PointHex']['hex'] # added this in Nov 2019
           if len(data_raw)>=36: # otherwise not enough to extract all the weather info (NOTE: CHANGED THIS TO 36 in APR 2019 )
             if (data_raw[18]=='b') or (data_raw[21]=='b') or (data_raw[20]=='b'): # then this is weather where illusion is 21 and LAIII is 20 as discovered 11/29/18
                date=parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date'])
                if int(parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date']).strftime('%s')) not in date_all: #make sure that this is not a repeat time
                  date_all.append(date)    
                  yr1=date.year
                  mth1=date.month
                  day1=date.day
                  hr1=date.hour
                  mn1=date.minute
                  yd1=date2num(dt(yr1,mth1,day1,hr1,mn1))-date2num(dt(yr1,1,1,0,0))
                  datet=dt(yr1,mth1,day1,hr1,mn1,tzinfo=None) # found this line out of line in Nov 2019 but fixed it
                  try: 
                    lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lat']
                    lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lon'] 
                  except:
                    try:
                      lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][5]['PointLoc']['Lat']
                      lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][5]['PointLoc']['Lon']
                    except:
                      lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][6]['PointLoc']['Lat']# added this Nov 2019
                      lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][6]['PointLoc']['Lon']
                  if data_raw[21]=='b':                
                    airt=float(data_raw[22:25])/10.-30.              
                    humid=float(data_raw[25:28])/10. 
                    barop=float(data_raw[28:32])+barop_correction[k]              
                    wspd=float(data_raw[32:35])/10.
                    wdir=float(data_raw[35:38])
                  elif data_raw[20]=='b':
                    airt=float(data_raw[21:24])/10.-30.              
                    humid=float(data_raw[24:27])/10. 
                    barop=float(data_raw[27:31])+barop_correction[k]              
                    wspd=float(data_raw[31:34])/10.
                    wdir=float(data_raw[34:37])
                  else: #case of LA Spring 2019
                    airt=float(data_raw[19:22])/10.-30.              
                    humid=float(data_raw[22:25])/10. 
                    barop=float(data_raw[25:29])+barop_correction[k]              
                    wspd=float(data_raw[29:32])/10.
                    wdir=float(data_raw[32:35])                  
                  datetg=datet
                  lastime= str(mth1).rjust(2)+ "," + str(day1).rjust(2)+"," +str(hr1).rjust(3)+ ","+str(mn1).rjust(3)
                  f_output.write(vn[k]+","+esn[-6:]+ ","+str(mth1).rjust(2)+ ","+str(day1).rjust(2)+"," +str(hr1).rjust(3)+ "," +str(mn1).rjust(3))
                  f_output.write((", %10.7f") %(yd1))
                  f_output.write((",%10.5f") %(lon)+' '+(",%10.5f") %(lat)+',10.0')
                  f_output.write(","+str(airt).rjust(10)+','+str(humid).rjust(10)+','+str(barop).rjust(10)+(",%6.2f") %(wspd)+ (",%6.2f") %(wdir)+(",%6.0f") %(yr1)+(",%6.0f") %(at_dock)+'\n')            
       except:
          print i+' is no good'       
  # For this boat, check to see if the latest report is within the past hour and, if so, create an email to send to NWS
  if (dt.now()+td(hours=5)-datetg).total_seconds()/3600.<1.25: # note: this needs to be fixed since it is hardcoded to DST
     email_nws(ship[k],call_sign[k],datetg,lat,lon,wdir,wspd,airt,humid,barop)# sends an email to the NWS folks in Alaska
     print 'emailed nws'
  
  f_output.close() #CLOSES weather_ap3.dat

# now put this data chronologically where it belongs in "weather.dat"
d1=pd.read_csv('/net/pubweb_html/drifter/weather.dat')
d2=pd.read_csv('/net/pubweb_html/drifter/weather_ap3.dat',header=None,names=['vessel','esn','mth','day','hr','mn','yd','lon','lat','alt','airt','humid','barop','wspd','wdir','year','at_dock_1'])
d = pd.concat([d1,d2], axis=0,ignore_index=True)
datetf=[]#final datetf to be created as follows
for kk in range(len(d)): # for each record of fishing boat weather
  datetf.append(dt(int(d["year"][kk]),int(d["mth"][kk]),int(d["day"][kk]),int(d["hr"][kk]),int(d["mn"][kk]),0))
d['datetf']=datetf # adds a datetime to dataframe d
d=d.sort_values(by=['vessel','datetf'])
d.to_csv('/net/pubweb_html/drifter/weather.dat')



