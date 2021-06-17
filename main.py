
import ubinascii
import machine
import time

from umqtt import MQTTClient
import cfg

version = "1.0"
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'notification'
topic_pub = b'hello'

def wlan_connect():
  import network
  sta_if = network.WLAN(network.STA_IF)
  if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect(cfg.wlan_essid, cfg.wlan_passphrase)
    while not sta_if.isconnected():
      pass
  print('network config:', sta_if.ifconfig())

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'notification' and msg == b'received':
    print("received hello message")

def connect_and_subscribe():
  global client_id, topic_sub
  client = MQTTClient(client_id, cfg.mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('connected to %s MQTT broker, subscribed to %s topic' % (cfg.mqtt_server, topic_sub))
  return client


def restart_and_reconnect():
  print("failed to connect to MQTT broker, restarting")
  time.sleep(2)
  machine.reset()

def main():

  global version, topic_pub

  print("bmon version %s" % version)

  wlan_connect()

  try:
    client = connect_and_subscribe()
  except OSError as e:
    restart_and_reconnect()

  last_message = 0
  message_interval = 5
  counter = 0

  while True:
    try:
      client.check_msg()
      if (time.time() - last_message) > message_interval:
        msg = b'Hello #%d' % counter
        client.publish(topic_pub, msg)
        last_message = time.time()
        counter += 1
    except OSError as e:
      restart_and_reconnect()


main()
