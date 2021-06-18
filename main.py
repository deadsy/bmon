#------------------------------------------------------------------------------
"""
bmon - Beehive Monitoring
"""
#------------------------------------------------------------------------------

import time
import ubinascii
import machine
import network

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

def mqtt_connect(client_id, mqtt_server):
  """connect to an mqtt broker"""
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(mqtt_subscription_cb)
  client.connect()
  print("connected to mqtt broker %s" % mqtt_server)
  return client

#------------------------------------------------------------------------------

def restart():
  """restart the device"""
  print("restarting...")
  time.sleep(10)
  machine.reset()

#------------------------------------------------------------------------------

def main():
  """entry point"""
  print("bmon version %s" % bmon_version)

  # connect to wlan
  wlan_connect(cfg.wlan_essid, cfg.wlan_passphrase)

  # connect to the mqtt broker
  client_id = ubinascii.hexlify(machine.unique_id())
  try:
    client = mqtt_connect(client_id, cfg.mqtt_server)
    client.subscribe("notification")
  except OSError:
    restart()

  # publish periodic mqtt messages
  last_message = 0
  message_interval = 5
  counter = 0
  while True:
    try:
      client.check_msg()
      if (time.time() - last_message) > message_interval:
        msg = b'Hello #%d' % counter
        client.publish("stats", msg)
        last_message = time.time()
        counter += 1
    except OSError:
      restart()

main()

#------------------------------------------------------------------------------
