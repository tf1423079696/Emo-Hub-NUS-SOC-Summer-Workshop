#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

const char* ssid = "Tenda_AA8CD0"; // Wifi's SSID
const char* password = "13305485766"; // Wifi Password

WiFiClient wifiClient;
const char* pcAt = "http://192.168.0.103:8080/"; // PC's IP
const char* piAt = "http://192.168.0.105:8080/"; // Pi's IP


#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);  //I2C address, 16 chars, 2 rows


#define INTPIN_BLUE D3
#define INTPIN_YELLOW D4
#define LED D5

volatile unsigned long lastTime_blue = 0;
volatile unsigned long lastTime_yellow = 0; 
volatile unsigned long deltaT = 50;    

// 0: no demo; 1: 1st demo; 2: 2nd demo
volatile int mod = 0;

// Press button blue: 1st demo
IRAM_ATTR void button_blue() {
  if ((millis() - lastTime_blue) > deltaT) {
    mod = 1;
    digitalWrite(LED, HIGH);
    Serial.println("blue");
    lastTime_blue = millis();
  }
}

// Press button yellow: 2nd demo
IRAM_ATTR void button_yellow() {
  if ((millis() - lastTime_yellow) > deltaT) {
    mod = 2;
    digitalWrite(LED, HIGH);
    Serial.println("yellow");
    lastTime_yellow = millis();
  }
}


void setup(void){
  Serial.begin(9600);
  
  pinMode(LED, OUTPUT);
  pinMode(INTPIN_BLUE, INPUT_PULLUP);
  pinMode(INTPIN_YELLOW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(INTPIN_BLUE), button_blue, RISING);
  attachInterrupt(digitalPinToInterrupt(INTPIN_YELLOW), button_yellow, RISING);
  digitalWrite(LED, LOW);

  WiFi.begin(ssid, password);
  Serial.println("");
  
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  lcd.init();  //initialize the lcd
  lcd.backlight();
}


void loop(void){
  if (WiFi.status() == WL_CONNECTED && (mod == 1 || mod == 2)){
    HTTPClient http;
    String url = pcAt;
    
    url += ("run?mod="+String(mod));

    lcd.init();
    lcd.backlight();
    lcd.setCursor(0,0);
    lcd.print("STATUS:");
    lcd.setCursor(3,1);
    lcd.print("RECORDING");
      
    http.begin(wifiClient,url);
    int returnCode = http.GET();
    http.end();

    url = pcAt;
    url += ("status");
    String state = "";
    http.begin(wifiClient,url);
    while(true){
      returnCode = http.GET();
      state = http.getString();
      Serial.println(http.getString());
      if(state == "END"){
        mod = 0;
        break;
      }
      delay(20000);
    }
    http.end();
    
    url = piAt;
    url += "result";
    http.begin(wifiClient,url);
    returnCode = http.GET();
    if (returnCode > 0){
      String result = http.getString();
      Serial.println(result);
      lcd.init();
      lcd.backlight();
      lcd.setCursor(0,0);
      lcd.print("RESULT:");
      lcd.setCursor(3,1);
      lcd.print(result);
    }
    http.end();
      
  } else {
    if (WiFi.status() != WL_CONNECTED){
      Serial.println("WiFi disconnected");
    } else{
      Serial.println(mod);
    }
  }
  digitalWrite(LED, LOW);
  delay(1000);
}
