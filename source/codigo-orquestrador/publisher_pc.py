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
		
mqttc = mqtt.Client("publisher-pc")
mqttc.username_pw_set(user, password=password)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))

#====================================================
#	FUNCAO QUE EXECUTA A PUBLICACAO DE MENSAGENS NO BROKER
def publish_to_topic(topico, mensagem):
	mqttc.publish(topico,mensagem,1)
	print ("Published: " + str(mensagem) + " " + "on MQTT Topic: " + str(topico))
	print ("")
	
#====================================================
# RECEBE O NOME DO PROFISSIONAL ENCONTRADO NO BANCO DE DADOS E PUBLICA NO TOPICO "topico/resposta"

def publish_nome_profissional(sala,mensagem):
	topico = "topicoEntrada/"+sala+"/confirmarAgendamento"
	publish_to_topic(topico,mensagem)