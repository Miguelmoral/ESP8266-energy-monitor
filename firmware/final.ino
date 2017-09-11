#include <ESP8266WiFi.h>
#include <Wire.h>
#include<LiquidCrystal_I2C.h>
#include <Adafruit_ADS1015.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>

//Credenciales WiFi
const char* ssid     = "$SSID";
const char* password = "$SSIDPass";

// Iniciar ADS address con 0x48
Adafruit_ADS1115 ads(0x48); //Con Adafruit_ADS1115 especificamos que es la versi�n de 16 bit.
LiquidCrystal_I2C lcd(0x27, 16, 2); //Especificamos que la direcci�n del LCD es 0x27

WiFiClient client;

double offsetI;
double filteredI;
double sqI,sumI;
int16_t sampleI;
double Irms;
#define ICAL 0.0083

double squareRoot(double fg){
  double n = fg / 2.0;
  double lstX = 0.0;
  while (n != lstX)
  {
    lstX = n;
    n = (n + fg / n) / 2.0;
  }
  return n;
}


double calcIrms(unsigned int Number_of_Samples){

  float multiplier = 0.125F;    /* ADS1115 @ +/- 4.096V gain (16-bit results) */

  Serial.println("*****************Inicio***************************");
  for (unsigned int n = 0; n < Number_of_Samples; n++)
  {
    sampleI = ads.readADC_Differential_0_1();

    // Elimina los 1,6V que tiene el sistema haciendo que la muestra est� centrada en 0
    offsetI = (offsetI + (sampleI-offsetI)/65536);
    filteredI = sampleI - offsetI;

    // Root-mean-square method current
    // 1) square current values
    sqI = filteredI * filteredI;

    // 2) sum
    sumI += sqI;
  }

    double I_RATIO = ICAL * multiplier;
    Irms = squareRoot(sumI / Number_of_Samples)*I_RATIO;

    sumI = 0;


  return Irms;
}

void mandarJson(double irms, double potencia){

   if (WiFi.status() == WL_CONNECTED) { //Comprobar wifi

    StaticJsonBuffer<300> JSONbuffer;   //Declarar JSON buffer
    JsonObject& JSONencoder = JSONbuffer.createObject();

    JSONencoder["sensorType"] = "Power";
    Serial.println("IRMS dentro de mandarjson: ");Serial.println(irms);
    JsonArray& values = JSONencoder.createNestedArray("values"); //JSON array
    values.add(irms); //A�adir valor al array
    values.add(potencia); //A�adir valor al array

    JsonArray& valuesInfo = JSONencoder.createNestedArray("valuesInfo"); //JSON array
    valuesInfo.add("irmsnuevo"); //A�adir valor al array
    valuesInfo.add("potencianueva"); //A�adir valor al array

    char JSONmessageBuffer[300];
    JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
    Serial.println(JSONmessageBuffer);

    HTTPClient http;    //Declare object of class HTTPClient

    http.begin("$IPServidor");      //Especificar el destino de la solicitud
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(JSONmessageBuffer);   //Mandar la solicitud
    String payload = http.getString();

    Serial.println(httpCode);   //Imprime el c�digo http
    Serial.println(payload);    //Imprime el payload obtenido

    http.end();  //Cierra la conexi�n

  } else {

    Serial.println("Error en la conexi�n WIFI");

  }
}

void imprimirLcd(double irms, double potencia){
  lcd.clear();
  lcd.print("Irms: ");lcd.print(irms);lcd.print("A");
  lcd.setCursor(0,1);
  lcd.print("Potencia: ");lcd.print(potencia);lcd.print("W");
}


void setup() {
  Serial.begin(115200);
  delay(10);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);

  // Conexi�n wifi

  Serial.println();
  Serial.print("Connecting to ");
  lcd.print("Connecting to ");
  lcd.setCursor(0,1);
  lcd.print(ssid);
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) { // No sale del bucle hasta que no conecte al WIFI
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  lcd.print(WiFi.localIP());

  ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 2mV      0.125mV
  ads.begin();
}

void loop() {


 double irms = calcIrms(1000);
 double irmsaux = irms;
 double potencia = irms*220.0; //P=I*v  (Irms es la corriente eficaz)

 Serial.println("IRMS: ");Serial.println(irms);
 Serial.println("Potencia: ");Serial.println(potencia);


 mandarJson(irmsaux, potencia);
 imprimirLcd(irmsaux,potencia);



}
