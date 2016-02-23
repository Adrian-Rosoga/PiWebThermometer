#!/usr/bin/python

"""
RPiWebThermometer

One-trick-pony Web server giving the temperature reading (Celsius degrees)
from a DS18B20 sensor on a Raspberry Pi.
Minimum and maximum temperature alert thresholds can be specified.
The page auto-refreshes every 30 seconds.
"""

#
# Configuration
#
PORT = 8000
MAX_TEMPERATURE_THRESHOLD = 22.0
MIN_TEMPERATURE_THRESHOLD = 18.0

import re, time, glob
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

regex = re.compile(r't=(\d+)')

def get_temperature():
    """ Read temperature from the sensor """
    sensorFile = \
        open(glob.glob('/sys/bus/w1/devices/28-00000*/w1_slave')[0], 'r')
    sensorFile.readline()
    line = sensorFile.readline()
    sensorFile.close()
    data = regex.search(line)
    temperature = float(data.group(1)[0:4])/100.0
    return temperature

html_page_template = """<HTML>
<HEAD>
    <TITLE>Web Thermometer</TITLE>
    <META HTTP-EQUIV=PRAGMA CONTENT=NO-CACHE>
    <META HTTP-EQUIV=EXPIRES CONTENT=-1>
    <META HTTP-EQUIV=REFRESH CONTENT=30>
</HEAD>
<BODY>
    <B><BR>
    <P ALIGN=CENTER>
    <FONT SIZE=10>Web Thermometer</FONT>
    <BR>
    <FONT SIZE=5>(Raspberry Pi, DS18B20)</FONT>
    <BR><BR><BR>
    <FONT SIZE=14 COLOR=%s>%s &deg;C</FONT>
    <BR><BR><BR>
    <FONT SIZE=6>%s</FONT>
    <BR><BR>
    <FONT SIZE=5 COLOR=RED>%s</FONT>
    <BR><HR>
    <FONT SIZE=3>Page autorefreshes every 30 seconds.</FONT>
    </P>
    </B>
</BODY>
</HTML>"""

class TemperatureHandler(SimpleHTTPRequestHandler, object):
    
    """ Custom handler that returns the temperature page """
    
    def do_GET(self):
        
        """ Only the request for favicon is honored, for all else
        return the temperature page """
        
        if self.path == '/favicon.ico':
            return SimpleHTTPRequestHandler.do_GET(self)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        temperature = get_temperature()
        alert = ''
        color = 'GREEN'
        if (temperature > MAX_TEMPERATURE_THRESHOLD):
            alert = 'ALERT - Temperature above ' +\
                    str(MAX_TEMPERATURE_THRESHOLD) + ' &deg;C!'
            color = 'RED'
        elif (temperature < MIN_TEMPERATURE_THRESHOLD):
            alert = 'ALERT - Temperature below ' +\
                    str(MIN_TEMPERATURE_THRESHOLD) + ' &deg;C!'
            color = 'RED'

        self.wfile.write( html_page_template % (color, temperature,
                          time.ctime(), alert) )
        self.wfile.close()
    
def main():
    
    """ Start HTTP server with the custom handler """
        
    try:
        server = HTTPServer(('', PORT), TemperatureHandler)
        print 'Started HTTP server on port ' + str(PORT) + '...'
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down...')
        server.socket.close()

if __name__ == '__main__':
    main()
