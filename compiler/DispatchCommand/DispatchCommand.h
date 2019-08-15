#ifndef DispatchCommand.h
#define DispatchCommand.h
class dispatchCommand {
public:
//mode used in some of the function below
#define AUTOMATIC 1
#define MANUAL 0
#define ON 1
#define OFF 0
//for constructor
dispatchCommand(int*, int*);
//(pinT1, pinQ1, pinLED
//for setup and loop
void begin();
void setMode(int Mode);
//get function
float getT1();
float getQ1();
unsigned long getdCycle();
int isOn();
int getMode();
//Set function
void setON(int statHeater);
void setQ1(float);
void setdCycle(unsigned long);

private:
void manualMode();
void autoMode();
unsigned long SampleTime, _lastTime;
unsigned long _windowStartTime;
float _currentWindowPidOutput;
int *_pinT1;
int *_pinQ1;
float _valQ1;
unsigned long _windowSize;
float _degC;
float _percent_watt;
bool _ON;
bool _inAuto;
// *(pointer) create hard link between variable and the dispatchCommand
};
#endif
