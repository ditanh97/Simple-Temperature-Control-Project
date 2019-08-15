//#ifndef DispatchCommand.h
//#define DispatchCommand.h

class dispatchCommand {
public:

//mode used in some of the function below
#define AUTOMATIC 1
#define MANUAL 0
#define ON 1
#define OFF 0
#define ADDPOWER 1
#define NODIST 0

//for constructor
dispatchCommand(bool*, bool*);//(bool pinQ1, pinQ2)


//for setup and loop
void begin();

//Set function
void setCO(float);
void setdCycle(float);
void setMode(int Mode);
void setDist(int addPower);
void setOFF(); // for emergency

//get function
unsigned long getdCycle();
int isOn();
int isDist();
int getMode();

private:
void manualMode();
void autoMode();
unsigned long _windowStartTime;
float _currentWindowPidOutput;
float _valQ1;
unsigned long _windowSize;
bool *_Q1state;
bool *_Q2state;
float _percent_watt;
bool _ON;
bool _inAuto;
bool _inDist;

// *(pointer) create hard link between variable and the dispatchCommand
};

//#endif
