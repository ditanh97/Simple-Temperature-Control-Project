/*
  References :
  - Jeffrey Kantor, John Hedengren, 2017 : blueprint codes
    see: https://github.com/APMonitor/arduino/blob/master/0_Test_Device/Python/tclab/tclab.ino
  - Brett Beauregard. 2009 : transforming data received from python in form of union
    see: http://brettbeauregard.com/blog/2009/05/graphical-front-end-for-the-arduino-pid-library/  
  - George Dewar, 2015 : approximation of dutycycle time used in DispatchCommand.cpp
    see: https://georgedewar.wordpress.com/2015/07/27/using-pid-on-an-arduino-to-control-an-electric-heater/
  - ThePoorEngineer,2018 :serial buffer data send to python used in SENDTOPC
    see: https://www.thepoorengineer.com/en/arduino-python-plot/#arduino
*/

#include "DispatchCommand.h"

// constants
const int baud = 9600;          // serial baud rate
const int pinT1   = 8;          // T1
const int pinQ1   = 12;         // Q1 = 4
const int pinQ2   = 13;         // Q2 = 2
float temp;
bool Q1stat, Q2stat;
bool q1, q2;
float Q1, Q2;
                  

//using plug-in library for calibration of incoming data from temperature sensor
dispatchCommand dispatch(&Q1stat, &Q2stat, pinT1);

/* UNION DATA FROM PYTHON */
union {                // This Data structure lets
  byte asBytes[16];    // us take the byte array
  float asFloat[4];    // sent from python and
}                      // easily convert it to a
pyduino;                   // float array


void SerialReceive(void) {
  int index=0;
  while(Serial.available()&&index<16)
  {
    pyduino.asBytes[index] = Serial.read();
    index++;
  }
  if(index==16)
  {
    float q1Val, wintimeVal, modVal,q2Val;
    q1Val=float(pyduino.asFloat[0]);
    dispatch.setCO(q1Val);

    wintimeVal = float(pyduino.asFloat[1]);
    dispatch.setdCycle(wintimeVal);
    
    modVal = float(pyduino.asFloat[2]);
    if (modVal == 1.0){
      dispatch.setMode(AUTOMATIC);
    }
    else{
      dispatch.setMode(MANUAL);  
    }
       
    
    q2Val=float(pyduino.asFloat[3]);
    if (q2Val == 1.0){
      dispatch.setDist(ADDPOWER);
    }
    else{
      dispatch.setDist(NODIST);
    }
   index = 0;
  }
}


// check temperature and shut-off heaters if above high limit
void checkTemp(void) {
    if (temp >= 60.0) {
      dispatch.setOFF();
    }
  }

// arduino startup
void setup() {
  Serial.begin(baud);
  pinMode(pinQ1, OUTPUT);
  pinMode(pinQ2, OUTPUT);
  dispatch.begin();
  delay(1000);
}

// arduino main event loop
void loop() {
//  testrelay();
  start();
}



/* 
FLOAT : 4BYTES; BOOL : 1BYTES; 
UNSIGNED LONG : 4BYTES; INT : 2BYTES;
*/
void testrelay(void){
  digitalWrite(pinQ1, LOW);
  digitalWrite(pinQ2, LOW);
  Serial.println("POWER ON");
  Serial.println("========="); 
  delay(5000);
  digitalWrite(pinQ1,HIGH);
  digitalWrite(pinQ1,HIGH); 
  Serial.println("POWER OFF");
  Serial.println("=========");  
//  delay(5000);
}

void start(void){

  temp = dispatch.getTemp();
//  Serial.println(temp);
  SerialReceive();
  checkTemp();
  digitalWrite(pinQ1, Q1stat);
  digitalWrite(pinQ2, Q2stat);
  getData();
  Serial.flush();
  delay(1000); // untuk testing ui
}

void getData(void){ 

  unsigned long pC = dispatch.getdCycle();
  q1 = dispatch.isOn();
  if (q1 == 1){Q1 = 100.0 ;}
  else {Q1 = 0.0;};
  q2 = dispatch.isDist();
  if (q2 == 1){Q2 = 100.0 ;}
  else {Q2 = 0.0;};
  if (dispatch.getMode() == AUTOMATIC){
    SendtoPC(&temp, &Q1, &Q2, &pC);
  }
  else {
    SendtoPC(&temp, &Q1, &Q2);
  }
  
}

void SendtoPC(float *temp, float *q1, float *q2, unsigned long *pC){
//casting
byte *data1 = (byte*) temp; //4
byte *data2 = (byte*) q1;   //4
byte *data3 = (byte*) q2;   //4
byte *data4 = (byte*) pC;   //4

byte buf[16] = {data1[0], data1[1], data1[2], data1[3],
                data2[0],data2[1], data2[2],data2[3],
                data3[0],data3[1], data3[2], data3[3],
                data4[0], data4[1], data4[2], data4[3]};
Serial.write(buf,16);           
}

void SendtoPC(float *temp, float *q1,float *q2){
//casting
byte *data1 = (byte*) temp; //4
byte *data2 = (byte*) q1;   //4
byte *data3 = (byte*) q2;   //4
byte buf[12] = {data1[0], data1[1], data1[2], data1[3],
                data2[0], data2[1], data2[2],data2[3],
                data3[0], data3[1], data3[2], data3[3]};
Serial.write(buf,12);            
}
