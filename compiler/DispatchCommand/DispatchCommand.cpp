#include <DallasTemperature.h>

#include <OneWire.h>

#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "DispatchCommand.h"

extern OneWire oneWire;
extern DallasTemperature sensors;
//CONSTRUCTOR

dispatchCommand::dispatchCommand(int* pin1, int* pin2){
_pinT1 = pin1;
_pinQ1 = pin2;
oneWire = OneWire(_pinT1);
sensors = DallasTemperature(&oneWire);

//default
dispatchCommand::setQ1(0.0);
dispatchCommand::setdCycle(5);  //default 5 menit

_inAuto = false; 
_ON = false;

SampleTime = 100;  //default sample time is 0.1 seconds
_lastTime = millis() - SampleTime;

}
/*FOR THE SAKE OF FRONT END USES*/
void dispatchCommand::begin(){
_windowStartTime = millis();
pinMode(_pinQ1, OUTPUT);
pinMode(_pinT1, INPUT);
sensors.begin();
sensors.requestTemperatures();
_degC = sensors.getTempCByIndex(0);
}

void dispatchCommand::setMode(int Mode){
if (Mode == AUTOMATIC){
dispatchCommand::autoMode();
_inAuto = true; 
}
else{
dispatchCommand::manualMode();
_inAuto = false; 
}
}

void dispatchCommand::autoMode(){
_percent_watt = max(0.0, min(100.0,_valQ1));
unsigned long now = millis(); 
unsigned long timeChange = (now - _lastTime);

/*sebenarnya fungsi ini percuma tibanya hitung pid, karena pada
akhirnya nilai output PID pertama yang dibaca, output yang selanjutnya
sia-sia, sampai windowsize time nya bertukar, baru diambil lg nilai
output terbaru*/
if (timeChange>=SampleTime){
if (now - _windowStartTime > _windowSize){ //time to shift the Relay Window   
_windowStartTime += _windowSize;
_currentWindowPidOutput = _percent_watt;
}
if (_currentWindowPidOutput * _windowSize > ((now - _windowStartTime) * 100)) {
digitalWrite(_pinQ1, LOW);
_ON = 1;
}
else{
digitalWrite(_pinQ1, HIGH);
_ON = 0;}
_lastTime = now;
}
}

void dispatchCommand::manualMode(){
if (_ON){
digitalWrite(_pinQ1, LOW);
_percent_watt = 100.0;
}
else {
digitalWrite(_pinQ1, HIGH);
_percent_watt = 0.0;
}
}


/*FOR THE SAKE OF FRONT END USES*/
void dispatchCommand::setON(int statHeater){
if (statHeater == ON){
_ON = true;}
else{
_ON = false;
}
}
void dispatchCommand::setQ1(float valQ1){_valQ1 = valQ1;}
void dispatchCommand::setdCycle(unsigned long windowSize){
_windowSize = windowSize*1000*60;
}


/*FOR THE SAKE OF FRONT END USES*/

float dispatchCommand::getT1(){ return _degC;}

float dispatchCommand::getQ1(){ return _percent_watt;}

unsigned long dispatchCommand::getdCycle(){ return _windowSize/(1000*60);}

int dispatchCommand::isOn(){ return _ON? ON : OFF;}

int dispatchCommand::getMode(){return _inAuto? AUTOMATIC : MANUAL;}
