import os
import re
import subprocess
import time
from influxdb import InfluxDBClient
import random
import sys
import requests
import json



response = subprocess.Popen('/usr/bin/speedtest --accept-license --accept-gdpr -f json -u bps', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

json_response = json.loads(response)

# ping = re.search('Latency:\s+(.*?)\s', response, re.MULTILINE)
# download = re.search('Download:\s+(.*?)\s', response, re.MULTILINE)
# upload = re.search('Upload:\s+(.*?)\s', response, re.MULTILINE)
# jitter = re.search('\((.*?)\s.+(jitter:)\)\s', response, re.MULTILINE)

# Typical response:
# {"type":"result","timestamp":"2022-08-17T18:32:59Z","ping":{"jitter":0.492,"latency":2.456,"low":2.308,"high":3.372},"download":{"bandwidth":11741893,"bytes":91658880,"elapsed":7807,"latency":{"iqm":376.667,"low":6.338,"high":542.037,"jitter":80.576}},"upload":{"bandwidth":11712337,"bytes":42328800,"elapsed":3614,"latency":{"iqm":6.528,"low":3.674,"high":7.725,"jitter":0.571}},"packetLoss":0,"isp":"Airtel Broadband","interface":{"internalIp":"192.168.1.108","name":"eth0","macAddr":"B8:27:EB:90:AD:1B","isVpn":false,"externalIp":"106.215.80.93"},"server":{"id":18996,"host":"speedtestdel.airtelbroadband.in","port":8080,"name":"Airtel Broadband","location":"Delhi","country":"India","ip":"122.160.129.138"},"result":{"id":"9819e091-b129-49c4-8d15-e5a50d6f82a5","url":"https://www.speedtest.net/result/c/9819e091-b129-49c4-8d15-e5a50d6f82a5","persisted":true}}
#print(response)



ping = format(round(json_response["ping"]["latency"],2),".2f")
download = format(round(json_response["download"]["bandwidth"]/125000,2),".2f")
upload = format(round(json_response["upload"]["bandwidth"]/125000,2),".2f")
jitter = format(round(json_response["ping"]["jitter"],2),".2f")

isp = json_response["isp"]

packet_loss = json_response["packetLoss"]

internal_ip = json_response["interface"]["internalIp"]
external_ip = json_response["interface"]["externalIp"]

server_host = json_response["server"]["host"]
server_port = json_response["server"]["port"]
server_name = json_response["server"]["name"]
server_location = json_response["server"]["location"]
server_country = json_response["server"]["country"]
server_ip = json_response["server"]["ip"]

result_url = json_response["result"]["url"]

#print(ping)
#print(download)
#print(upload)
#print(jitter)

#sys.exit("Debugging...")   


speed_data = [
    {
        "measurement" : "internet_speed",
        "tags" : {
            "host": "RaspberryPi"
        },
        "fields" : {
            "download": float(download),
            "upload": float(upload),
            "ping": float(ping),
            "jitter": float(jitter)
        }
    }
]


file1 = open("/home/ankit/speedtest/results3.csv", "a+")  # append mode

if os.stat("/home/ankit/speedtest/results3.csv").st_size == 0:
    file1.write('Date,Time,Ping (ms),Jitter (ms),Download (Mbps),Upload (Mbps),ISP,Packet_Loss,Internal_IP,External_IP,Server_Host,Server_Port,Server_Name,Server_Location,Server_Country,Server_IP,Results_URL\r\n')

file1.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, jitter, download, upload,isp,packet_loss,internal_ip,external_ip,server_host,server_port,server_name,server_location,server_country,server_ip,result_url))
file1.close()


client = InfluxDBClient('localhost', 8086, 'speedmonitor', 'pimylifeup', 'internetspeed')
client.write_points(speed_data)


# Feeds

download_url="https://io.adafruit.com/api/v2/webhooks/feed/********"
jitter_url="https://io.adafruit.com/api/v2/webhooks/feed/********"
ping_url="https://io.adafruit.com/api/v2/webhooks/feed/********"
upload_url="https://io.adafruit.com/api/v2/webhooks/feed/********"



download_rate = {'value':download}
upload_rate = {'value':upload}
jitter_rate = {'value':jitter}
ping_rate = {'value':ping}

session = requests.Session()

session.post(download_url,data=download_rate)
session.post(upload_url,data=upload_rate)
session.post(jitter_url,data=jitter_rate)
session.post(ping_url,data=ping_rate)
