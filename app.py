from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()
import paho.mqtt.client as mqtt
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
uni_data=''
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("kankan")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    processRequest(msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("18.216.139.115", 1883, 60)




@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))
    #res = processRequest(req)
    speech = "Your Vehicle is in "+uni_data
    print (speech)
    res= {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print(r)
    return r


def processRequest(reh):
   # if req.get("result").get("action") != "yahooWeatherForecast":
   #     return {}
    baseurl = "https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyA_ASQP-QLxu8N9DOFjn5UBogVdfwBGxF0&sensor=false&language=en&latlng="
    #yql_query = makeYqlQuery(req)
    #if yql_query is None:
    #    return {}
    yql_url = baseurl +str(reh.decode("utf-8"))+ "&format=json"
    print(yql_url)
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeWebhookResult(data):
    rest=data.get("results")[0].get("formatted_address")
    if rest is None:
        return{}
    print(rest)
    uni_data=rest
    


if __name__ == '__main__':
    client.loop_forever()
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
    
