#include <EEPROM.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include "DHT.h"
#define DHTPIN PD2
#define DHTTYPE DHT11   // DHT 11

int j=0,temperatura=0,wilgotnosc=0,wysokosc=0;
DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP280 bmp;

void setup()
{
  delay(120000); //opoznienie do sczytywania danych z pamieci EEPROM
  Serial.begin(9600);
  dht.begin();
  if (!bmp.begin()){delay(1000);} //opoznienie dla zalaczenia czujnika BME280
  //for(int i=0;i<1024;i++){EEPROM[i]=0;} //czyszczenie pamieci EEPROM
}

void loop()
{
    if(Serial.available())
    {
      for(int k=0;k<1024;k=k+3)
      {
        Serial.print(EEPROM[k]);
        Serial.print(" ");
        Serial.print(EEPROM[k+1]);
        Serial.print(" ");
        Serial.print(EEPROM[k+2]);
        Serial.print("\n");
      }
    }

    temperatura=dht.readTemperature();
    wilgotnosc=dht.readHumidity();
    wysokosc=bmp.readAltitude(1013); //kalibracja wysokosci
    wysokosc=wysokosc/10; //wysokosc mierzona co 10m do 2560 metrow nad poziomem morza
    EEPROM[j]=temperatura;
    EEPROM[j+1]=wilgotnosc;
    EEPROM[j+2]=wysokosc;
    j=(j+3)%1023;
    delay(10000); //opoznienie do kolejnego odczytu
}
