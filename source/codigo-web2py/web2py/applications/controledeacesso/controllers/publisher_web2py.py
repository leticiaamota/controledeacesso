import paho.mqtt.client as mqtt
import random, threading, json, string
from datetime import datetime
#====================================================
# MQTT Settings 
MQTT_Broker = "m12.cloudmqtt.com"
MQTT_Port = 19729
Keep_Alive_Interval = 45
user = "qxqwnxyw"
password = "ktJEqMyhPOVx"

#====================================================

def on_connect(client, userdata, rc):
	if rc != 0:
		pass
		print ("Unable to connect to MQTT Broker...")
	else:
		print ("Connected with MQTT Broker: " + str(MQTT_Broker))

def on_publish(client, userdata, mid):
	pass
		
def on_disconnect(client, userdata, rc):
	if rc !=0:
		pass
		
mqttc = mqtt.Client()
mqttc.username_pw_set(user, password=password)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))

#====================================================
#	FUNCAO QUE EXECUTA A PUBLICACAO DE MENSAGENS NO BROKER
def publish_to_topic(topic, message):
	mqttc.publish(topic,message,1)
	print ("Published: " + str(message) + " " + "on MQTT Topic: " + str(topic))
	print ("")
	
#====================================================
# RECEBE O TOPICO DA SALA SELECIONADA, MONTA O SUBTOPICO "../associarTagUser" E ENVIA COMANDO DE ABERTURA

def publish_associar_tag_user(topico,user):
	topicoSaida = topico + "/associarTagUser"
	message = {}
	message['Email']=user
	message['Action']='open_connection'
	json_message=json.dumps(message)
	print(json_message)
	publish_to_topic(topicoSaida,json_message)
	
#====================================================
# RECEBE O TOPICO DA SALA SELECIONADA, MONTA O SUBTOPICO "../associarTagMaster" E ENVIA COMANDO DE ABERTURA

def publish_associar_tag_master(topico,user):
	topicoSaida = topico + "/associarTagMaster"
	message = {}
	message['Email']=user
	message['Action']='open_connection'
	json_message=json.dumps(message)
	print(json_message)
	publish_to_topic(topicoSaida,json_message)