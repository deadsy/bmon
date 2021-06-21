#------------------------------------------------------------------------------
"""
bmon - Beehive Monitoring
"""
#------------------------------------------------------------------------------

import time
import json
import machine
import network
import ntptime
import ubinascii

from umqtt import MQTTClient
import cfg

#------------------------------------------------------------------------------

bmon_version = "0.1"

#------------------------------------------------------------------------------

def wlan_connect(essid, passphrase):
  """connect to wlan network"""
  sta_if = network.WLAN(network.STA_IF)
  if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect(essid, passphrase)
    while not sta_if.isconnected():
      pass
  print("network: ip %s subnet %s gateway %s dns %s" % sta_if.ifconfig())

#------------------------------------------------------------------------------

def mqtt_subscription_cb(topic, msg):
  """mqtt subscription message callback"""
  print((topic, msg))

#------------------------------------------------------------------------------

def restart():
  """restart the device"""
  print("restarting...")
  time.sleep(10)
  machine.reset()

#------------------------------------------------------------------------------

class Hive:

  def __init__(self):
    self.temperature = [27.0, 32.0, 42.0]
    self.humidity = [80.0, 98.0]
    self.weight = 115.0

  def stats(self):
    stats = {
      "ts": (time.time() + 946684800) * 1000,
      "temperature": self.temperature,
      "humidity": self.humidity,
      "weight": self.weight,
      }
    return json.dumps(stats)

#------------------------------------------------------------------------------

def main():
  """entry point"""
  print("bmon version %s" % bmon_version)

  h = Hive()

  # connect to wlan
  wlan_connect(cfg.wlan_essid, cfg.wlan_passphrase)

  # get the network time (set the rtc also)
  ntptime.settime()

  if cfg.mqtt_client_id is None:
    cfg.mqtt_client_id = ubinascii.hexlify(machine.unique_id())

  # connect to the mqtt broker
  try:
    client = MQTTClient(cfg.mqtt_client_id, cfg.mqtt_server, port=cfg.mqtt_port,
                        user=cfg.mqtt_user, password=cfg.mqtt_password)
    client.set_callback(mqtt_subscription_cb)
    client.connect()
    #client.subscribe("notification")
  except OSError:
    restart()
  print("connected to mqtt broker %s" % cfg.mqtt_server)

  # publish periodic mqtt messages
  last_message = 0
  message_interval = 5
  while True:
    try:
      client.check_msg()
      if (time.time() - last_message) > message_interval:
        client.publish(cfg.mqtt_topic, h.stats())
        last_message = time.time()
    except OSError:
      restart()

main()

#------------------------------------------------------------------------------
