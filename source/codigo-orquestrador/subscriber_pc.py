import paho.mqtt.client as mqttClient
import time, json, datetime
from dateutil.parser import parse
from DAL import validar_agendamento
from DAL import associar_tag
from publisher_pc import publish_nome_profissional

#===============================================================
#	MQTT CONNECTION
def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
 
        print("Connected to broker")
 
        global Connected                #Use global variable
        Connected = True                #Signal connection 
 
    else:
 
        print("Connection failed")	

#===============================================================
#	MQTT DATA RECEIVER
def on_message(client, userdata, message):	
	print ("")
	print ("Message received: "  + str(message.payload))
	print ("")
	
	#Separação de infos contidas em tópico
	infoTopico = message.topic.split('/')
	#infoTopico gets topic and subtopics
	#infoTopico[1] gets codSala
	#infoTopico[2] gets function
    
	if(infoTopico[2] == "validarAgendamento"):
		#variaveis sala, funcionario, hora_saida(hrsaida)
		sala = infoTopico[1]
		funcionario,hrsaida = validar_agendamento(message.topic, message.payload)
		hatual = datetime.datetime.now().strftime("%H:%M:00")

		if (hrsaida != None):
			########################
			# TIME DELTA DEFINITION		
			datetime_atual = datetime.datetime.strptime(hatual,'%H:%M:%S')
			datetime_saida = datetime.datetime.strptime(hrsaida, '%H:%M:%S')
			deltatime=str((datetime_saida-datetime_atual).seconds * 1000) 
			########################
		else:
			deltatime = None

		#definição de mensagem json
		mensagemPython = {
		  "funcionario": funcionario,
		  "deltaT": deltatime
		}

		# convert into JSON:
		mensagemJson = json.dumps(mensagemPython)

		#função publish - file: publish_pc
		publish_nome_profissional(sala,mensagemJson)
		
	if(infoTopico[2] == "salvarTagUser"):
		status = associar_tag(message.topic, message.payload)
		print("Salvar Tag User STATUS: ", status)
		pass
		
	if(infoTopico[2] == "salvarTagMaster"):
		status = associar_tag(message.topic, message.payload)
		print("Salvar Tag Master STATUS: ", status)
		pass

#===============================================================	
Connected = False   #global variable for the state of the connection
#===============================================================
#	MQTT CONFIG
broker_address= "m12.cloudmqtt.com"  #Broker address
port = 19729                         #Broker port
user = "qxqwnxyw"                    #Connection username
password = "ktJEqMyhPOVx"            #Connection password
topic = "topicoSaida/#"			 		 #Mqqt topic
 
client = mqttClient.Client("subscriber-pc")        #create new instance
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback
 
client.connect(broker_address, port=port)          #connect to broker
#=============================================================== 
client.loop_start()        #start the loop
 
while Connected != True:    #Wait for connection
    time.sleep(0.1)
 
client.subscribe(topic)
 
try:
    while True:
        time.sleep(1)
 
except KeyboardInterrupt:
    print ("exiting")
    client.disconnect()
    client.loop_stop()