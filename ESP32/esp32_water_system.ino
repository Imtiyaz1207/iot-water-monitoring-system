#include <WiFi.h>

#include <PubSubClient.h>

#include <ArduinoJson.h>

// ================= WIFI =================

const char* ssid = "Wokwi-GUEST";

const char* password = "";

const char* mqtt_server = "broker.hivemq.com";

// ================= MQTT =================

WiFiClient espClient;

PubSubClient client(espClient);

String ACTION_TOPIC =
"iot/smarttank/actions";

String STATUS_TOPIC =
"iot/smarttank/status";

String ACK_TOPIC =
"iot/smarttank/system_ack";

// ================= LEDs =================

#define LED_UP 4

#define LED_DOWN 16

#define LED_LEFT 17

#define LED_RIGHT 5

#define LED_ROTATE_L 18

#define LED_ROTATE_R 19

#define LED_PUSH 21

#define LED_PULL 22

// ================= VARIABLES =================

String currentCommand =
"Neutral";

unsigned long lastPublish = 0;

int water = 0;

bool increasing = true;
 // new 10/06
String lastCommandId = "";
// ================= CLEAR LEDs =================

void clearLEDs(){

digitalWrite(
LED_UP,
LOW
);

digitalWrite(
LED_DOWN,
LOW
);

digitalWrite(
LED_LEFT,
LOW
);

digitalWrite(
LED_RIGHT,
LOW
);

digitalWrite(
LED_ROTATE_L,
LOW
);

digitalWrite(
LED_ROTATE_R,
LOW
);

digitalWrite(
LED_PUSH,
LOW
);

digitalWrite(
LED_PULL,
LOW
);

}

// ================= EXECUTE ================= old 

//void executeCommand(

//String cmd

//){
// new 
void executeCommand(
    String cmd,
    String commandId
){

    clearLEDs();

    currentCommand = cmd;

    Serial.print(
        "Command: "
    );

    Serial.println(
        cmd
    );

if(

cmd=="Up"

){

digitalWrite(
LED_UP,
HIGH
);

}

else if(

cmd=="Down"

){

digitalWrite(
LED_DOWN,
HIGH
);

}

else if(

cmd=="Left"

){

digitalWrite(
LED_LEFT,
HIGH
);

}

else if(

cmd=="Right"

){

digitalWrite(
LED_RIGHT,
HIGH
);

}

else if(

cmd=="Rotate_Left"

){

digitalWrite(
LED_ROTATE_L,
HIGH
);

}

else if(

cmd=="Rotate_Right"

){

digitalWrite(
LED_ROTATE_R,
HIGH
);

}

else if(

cmd=="Push"

){

digitalWrite(
LED_PUSH,
HIGH
);

}

else if(

cmd=="Pull"

){

digitalWrite(
LED_PULL,
HIGH
);

}
//change  

StaticJsonDocument<200> ackDoc;

ackDoc["command_id"] = commandId;
ackDoc["command"] = cmd;
ackDoc["status"] = "SUCCESS";

char ackBuffer[200];

serializeJson(
    ackDoc,
    ackBuffer
);

client.publish(
    ACK_TOPIC.c_str(),
    ackBuffer
);

}

// ================= WIFI =================

void setup_wifi(){

Serial.println(
"Connecting WiFi..."
);

WiFi.begin(

ssid,

password

);

while(

WiFi.status()

!= WL_CONNECTED

){

delay(500);

Serial.print(
"."
);

}

Serial.println();

Serial.println(
"Connected"
);

}

// ================= CALLBACK =================

void callback(

char* topic,

byte* payload,

unsigned int length

){

String msg="";

for(

int i=0;

i<length;

i++

){

msg +=

(char)

payload[i];

}

Serial.println(
msg
);

StaticJsonDocument<200> doc;

DeserializationError error =

deserializeJson(

doc,

msg

);

if(error){

Serial.println(
"JSON Error"
);

return;

}

String command =
doc["command"] | "";

String commandId =
doc["command_id"] | "";

if(commandId == lastCommandId)
{
    Serial.println(
        "Duplicate Command Ignored"
    );

    return;
}

lastCommandId = commandId;

executeCommand(
    command,
    commandId
);

}

// ================= RECONNECT =================

void reconnect(){

while(

!client.connected()

){

String id =

"ESP32-" +

String(

random(9999)

);

if(

client.connect(

id.c_str()

)

){

client.subscribe(

ACTION_TOPIC.c_str()

);

Serial.println(
"MQTT Connected"
);

}

else{

delay(1000);

}

}

}

// ================= SETUP =================

void setup(){

Serial.begin(
115200
);

pinMode(
LED_UP,
OUTPUT
);

pinMode(
LED_DOWN,
OUTPUT
);

pinMode(
LED_LEFT,
OUTPUT
);

pinMode(
LED_RIGHT,
OUTPUT
);

pinMode(
LED_ROTATE_L,
OUTPUT
);

pinMode(
LED_ROTATE_R,
OUTPUT
);

pinMode(
LED_PUSH,
OUTPUT
);

pinMode(
LED_PULL,
OUTPUT
);

clearLEDs();

setup_wifi();

client.setServer(

mqtt_server,

1883

);

client.setCallback(

callback

);

}

// ================= LOOP =================

void loop(){

if(

!client.connected()

){

reconnect();

}

client.loop();

// water simulation

if(

millis()

-

lastPublish

>

1000

){

lastPublish = millis();

if(

increasing

){

water++;

if(

water>=100

){

water=100;

increasing=false;

}

}

else{

water--;

if(

water<=0

){

water=0;

increasing=true;

}

}

StaticJsonDocument<300> doc;

doc["water"] = water;

doc["command"] = currentCommand;

doc["system"] = "ONLINE";

doc["up"] =

currentCommand=="Up"

?

"ON"

:

"OFF";

doc["down"] =

currentCommand=="Down"

?

"ON"

:

"OFF";

doc["left"] =

currentCommand=="Left"

?

"ON"

:

"OFF";

doc["right"] =

currentCommand=="Right"

?

"ON"

:

"OFF";

doc["ack"] =

currentCommand;

char buffer[300];

serializeJson(

doc,

buffer

);

client.publish(

STATUS_TOPIC.c_str(),

buffer

);

}

}