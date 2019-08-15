#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "DispatchCommand.h"  // Use this instead <Dispatchcommand.h> cause it will overlap with the one use in another folder

//CONSTRUCTOR

dispatchCommand::dispatchCommand(bool* Q1state, bool* Q2state){
_Q1state = Q1state;
_Q2state = Q2state;
//default
dispatchCommand::setCO(0.0);
dispatchCommand::setdCycle(5);  //default 5 menit
dispatchCommand::setMode(MANUAL); 
dispatchCommand::setDist(NODIST);
}

/*FOR THE SAKE OF FRONT END USES*/
void dispatchCommand::begin(){
_windowStartTime = millis();
}

void dispatchCommand::setCO(float valQ1){_valQ1 = valQ1;}

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

void dispatchCommand::setdCycle(float windowSize){
_windowSize = (unsigned long) windowSize*1000.0*60.0;
}


void dispatchCommand::autoMode(){
_percent_watt = max(0.0, min(100.0,_valQ1));
unsigned long now = millis(); 
/*DISCLAIMER !!
 * 1)windowsize pertama  = 0, shg dia akan menunggu hingga melebihi kondisi pertama, 
 *   baru dimulai 
 * 2)sebenarnya fungsi ini percuma tibanya hitung pid, karena pada
akhirnya nilai output PID pertama yang dibaca, output yang selanjutnya
sia-sia, sampai windowsize time nya bertukar, baru diambil lg nilai
output terbaru*/
if (now - _windowStartTime > _windowSize){ //time to shift the Relay Window   
_windowStartTime += _windowSize;
_currentWindowPidOutput = _percent_watt;
}
if (_currentWindowPidOutput * _windowSize > ((now - _windowStartTime) * 100)) {
*_Q1state = LOW;// ingat on itu low/0, off itu high/1 karena pull up
_ON = 1; 
}
else{
*_Q1state = HIGH;
_ON = 0;}
}

void dispatchCommand::manualMode(){
if (_valQ1 == 100.0){
*_Q1state = LOW;
_ON = 1;
}
else {
*_Q1state = HIGH;
_ON = 0;
}
}


void dispatchCommand::setDist(int addPower){
if (addPower == ADDPOWER){
*_Q2state = LOW;
_inDist = 1;}
else{
*_Q2state = HIGH;
_inDist = 0;
}
}

void dispatchCommand::setOFF(){
*_Q1state = HIGH;
*_Q2state = HIGH;
_ON = 0;
_inDist = 0;
}

/*FOR THE SAKE OF FRONT END USES*/
unsigned long dispatchCommand::getdCycle(){return _windowSize/(1000.0*60.0);}

int dispatchCommand::isOn(){ return _ON? ON : OFF;}

int dispatchCommand::getMode(){return _inAuto? AUTOMATIC : MANUAL;}

int dispatchCommand::isDist(){return _inDist? ADDPOWER : NODIST;}
