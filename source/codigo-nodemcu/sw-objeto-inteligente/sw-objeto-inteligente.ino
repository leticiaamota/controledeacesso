// --- JSON ---
#include <ArduinoJson.h>

// --- RELÉ ---
#define controle D0

// --- LCD ---
#include <Wire.h>
#include <LiquidCrystal_I2C.h> 

LiquidCrystal_I2C lcd(0x27,16,2);   // Cria instância de LiquidCrystal_I2C

// --- WIFI ---
#include<ESP8266WiFi.h>
const char* ssid = "SUA_REDE";
const char* password = "SUA_SENHA";

WiFiClient nodeMCUClient;           // Cria instância de WiFiClient

// --- MQTT ---
#include <PubSubClient.h>
const char* mqttBroker = "m12.cloudmqtt.com";
unsigned int port = 19729;
const char* mqttClientID = "ESP8266Client";
const char* mqtt_user = "qxqwnxyw";
const char* mqtt_password = "ktJEqMyhPOVx";

PubSubClient client(nodeMCUClient); // Cria instância de PubSubClient

// --- RFID ---
#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN D4
#define RST_PIN D3

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Cria instância de MFRC522

// --- DEFINICAO DE TOPICOS DE CONTROLE ---
const char* topicoEntrada = "topicoEntrada/A21/#";                            // Tópico para recebimento de msg do servidor mqtt (subscriber)
const char* associarTagUser = "topicoEntrada/A21/associarTagUser";            // Aplicação - Protótipo (abre conexao para associar tag user)
const char* associarTagMaster = "topicoEntrada/A21/associarTagMaster";        // Aplicação - Protótipo (abre conexao para associar tag master)
const char* confirmarAgendamento = "topicoEntrada/A21/confirmarAgendamento";  // Aplicação - Protótipo (confirma agendamento para abrir sala)

const char* salvarTagUser = "topicoSaida/A21/salvarTagUser";                  // Responde a solicitação com o codigo da tag a ser associada
const char* salvarTagMaster = "topicoSaida/A21/salvarTagMaster";              // Responde a solicitação com o codigo da tag a ser associada
const char* validarAgendamento = "topicoSaida/A21/validarAgendamento";        // Solicita validação de agendamento de Tag lida

/*  flag para cadastro de Tag User/Master */
int get_card = 0;

// --- FUNÇÃO DE PREPARAÇÃO DO PROTÓTIPO ---
void setup() {
  WiFi.mode(WIFI_STA);
  
  /* RELE - inicializa pinos de saida */
  pinMode(controle, OUTPUT);
  digitalWrite(controle, HIGH);
  
  /* LCD - Inicializa o display LCD */
  lcd.init();
  lcd.backlight();
  lcdpattern();
    
  /* MQTT - Define parâmetros para conexão ao MQTT Broker */
  Serial.begin(115200);
  WiFiConnect();
  client.setServer(mqttBroker, port);
  client.setCallback(callback);
  reconnect();
  
  /* RFID - Inicializa módulo RFID */
  SPI.begin();
  mfrc522.PCD_Init();
}

// --- FUNÇÃO DE MSG PADRÃO DO DISPLAY LCD ---
void lcdpattern(){
  lcd.setCursor(0,0);
  lcd.print("*** CONTROLE DE ");
  lcd.setCursor(0,1);
  lcd.print("ACESSO - LSI ***");
}

// --- FUNÇÃO DE CONEXÃO À REDE WIFI ---
void WiFiConnect(){
  delay(10);
  Serial.println();
  Serial.print("Conectando-se à rede: ");  
  Serial.println(ssid);
  WiFi.begin(ssid,password);
  
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.println(".");
  }
  
  Serial.print("Conectado à rede: ");  
  Serial.println(ssid);
  Serial.println();
}

// --- FUNÇÃO DE RECONEXÃO AO MQTT BROKER ---
void reconnect(){
  
  while (!client.connected()) {
    Serial.print("Tentando conectar-se ao MQTT Broker... ");
      if (client.connect(mqttClientID, mqtt_user, mqtt_password)) {
        Serial.println("Conectado ao MQTT Broker");
        
        // Função para inscrição em um tópico
        client.subscribe(topicoEntrada,1);
        
      } else {
        Serial.print("Falha na conexão, rc= ");
        Serial.print(client.state());
        Serial.println("Nova tentativa em 5s.");
        delay(5000);
      }
  }
  Serial.println();  
}

// --- FUNÇÃO LEITURA DE TAGS E PUBLICAÇÃO DE INFORMAÇÕES ---
void ReadTagAndPublishInfo(const char* topicoSaida, const char* msgInfo){
  // Busca novas Tags
  if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    return;
  }
  // Seleciona uma das Tags lidas
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  
  // Define string para UID da Tag
  Serial.println();
  Serial.println();
  Serial.print("Tag lida:");
  String tagInfo= "";
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
     Serial.print(mfrc522.uid.uidByte[i], HEX);
     tagInfo.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     tagInfo.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  tagInfo.toUpperCase();
  
  Serial.println();
  Serial.println();

  //print no display
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(tagInfo.substring(1));
 
  // Define objeto Json para envio
  DynamicJsonBuffer jBuffer;
  JsonObject& root = jBuffer.createObject();
  root["Tag"] = tagInfo.substring(1);

  if(topicoSaida == salvarTagUser){
    root["Email"] = msgInfo;
  }

  if(topicoSaida == salvarTagMaster){
    root["Email"] = msgInfo;
  }

  char JSONmessageBuffer[100];
  root.printTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
  Serial.print("Mensagem enviada [");
  Serial.print(topicoSaida);
  Serial.print("], ");
  Serial.println(JSONmessageBuffer);
  Serial.println();

  // Função para envio de informação
  if (client.publish(topicoSaida, JSONmessageBuffer) == true) {
    Serial.println("Mensagem enviada com sucesso.");
    lcd.setCursor(0,1);
    lcd.print("Mensagem enviada");
    get_card = 1;
  } else {
    Serial.println("Erro no envio da mensagem.");
    lcd.setCursor(0,1);
    lcd.print("Erro no envio");
    get_card = 1;
  }

  Serial.println();
  Serial.println("-------------");
}


// --- FUNÇÃO PARA TRATAMENTO DE MENSAGENS RECEBIDAS DO MQTT BROKER ---
void callback(char* topic, byte* payload, unsigned int length) {
  
  lcd.clear();
  Serial.print("Mensagem recebida [");
  Serial.print(topic);
  Serial.print("], ");
  

  /*Função associar Tag de Usuários*/
  if(String(topic) == associarTagUser){
    String message;
    for (int i = 0; i < length; i++) {
      char c = (char)payload[i];
      message += c;
    }
    Serial.print(String(message));

    // Deserializa objeto Json
    DynamicJsonBuffer jBuffer;
    JsonObject& msg_User = jBuffer.parseObject(String(message));

    lcd.setCursor(0,1);
    lcd.print("Aguardando Tag..");    
     
    get_card = 0;
    
    while(get_card < 1){
      ReadTagAndPublishInfo(salvarTagUser,msg_User["Email"].asString());
      delay(1);
    }  
  }

  /*Função associar Tag Master*/
  if(String(topic) == associarTagMaster){
    String message;
    for (int i = 0; i < length; i++) {
      char c = (char)payload[i];
      message += c;
    }
    Serial.print(String(message));

    // Deserializa objeto Json
    DynamicJsonBuffer jBuffer;
    JsonObject& msg_Master = jBuffer.parseObject(String(message));

    lcd.setCursor(0,1);
    lcd.print("Aguardando Tag..");    
     
    get_card = 0;
    
    while(get_card < 1){
      ReadTagAndPublishInfo(salvarTagMaster,msg_Master["Email"].asString());
      delay(1);
    } 
  }

  /*Função de confirmação de agendamento*/
  if(String(topic) == confirmarAgendamento){
    String message;
    for (int i = 0; i < length; i++) {
      char c = (char)payload[i];
      message += c;
    }
    Serial.print(String(message));

    // Deserializa objeto Json
    DynamicJsonBuffer jBuffer;
    JsonObject& msg_Validacao = jBuffer.parseObject(String(message));

    //Variaveis extraídas da mensagem json
    String funcionario = msg_Validacao["funcionario"].asString();
    String delta = msg_Validacao["deltaT"].asString();
    
    if(funcionario != ""){
      digitalWrite(controle, LOW);
      lcd.setCursor(0,0);
      lcd.print(funcionario);
      lcd.setCursor(0,1);
      lcd.print("Acesso Concedido");
      delay(delta.toInt());
      digitalWrite(controle, HIGH);
    }else{
      lcd.setCursor(0,0);
      lcd.print("Tag Invalida");
      lcd.setCursor(0,1);
      lcd.print("Acesso Negado");
      delay(2000);
    }
    
  }

  Serial.println("-------------");
}

// --- FUNÇÃO PRINCIPAL ---
void loop(){
  /*MQTT*/
  if (!client.connected()) {
    reconnect();
  }
  
  client.loop();

  ReadTagAndPublishInfo(validarAgendamento, NULL);
  
  // Função para inscrição em um tópico
  client.subscribe(topicoEntrada);
  delay(2000);

  lcdpattern();
} 
