# Simple-Temperature-Control-Project

## Project Description 
The control circuit in this project consists of a heater for the main heat source, a heater for fake disturbance, a relay module for each heater (used to control the main and disturbance heater from Arduino), temperature sensor, an Arduino board, and a computer for displaying the GUI. GUI is programmed with Python and uses the serial protocol to communicate with Arduino compiler codes. Compiler codes are the one that uploaded on the Arduino board and programmed with the corresponding language. Data flows occur in both directions between Python and Arduino, each sending data packages in byte-type. Python will send data containing requests to be processed by Arduino, then Arduino sends data packages containing responses which are then sent back to Python.  These will form a cyclic process that started/stopped by pressing the play/stop button.

## Hardware assembly
Relay is connected to the digital output pin on Arduino, where both heaters contact to relays in normally open (NO) state. The temperature sensor is an analog sensor that can be connected to an anolog input pin.

## Initialization
Initially, upload the `compiler.ino` file on the Arduino board, then run `main.py` to display the GUI. Make sure the port connection to Arduino is correct, by pressing the tool ![1](https://user-images.githubusercontent.com/51126784/63222211-dad00380-c1ce-11e9-92bb-71716b17d55b.png) to pop up the dialog box for port and baud rate settings. The button ![2](https://user-images.githubusercontent.com/51126784/63222216-f3401e00-c1ce-11e9-91d4-f431e2417472.png) to start the process can only be activated if the control mode has been selected. Available control modes in this program are manual and PID. By selecting a mode, this also displays the data plot page. This button ![3](https://user-images.githubusercontent.com/51126784/63222226-19fe5480-c1cf-11e9-880f-f7fee81382cf.png) can only be accessed for manual mode, and vice versa for PID parameter input which can only be access if the PID mode is selected. Mark the checkbox in this ![4](https://user-images.githubusercontent.com/51126784/63222227-1e2a7200-c1cf-11e9-8919-c57c6e584d4c.png) section before starting the process if you want to save the data. <br/>
![Screenshot from 2019-06-16 23-03-46](https://user-images.githubusercontent.com/51126784/63222105-41ecb880-c1cd-11e9-85b2-a2a2e0da8b9b.png)

## Issues
This program is work well with manual mode, but still have issues with PID mode. 
![gui manual](https://user-images.githubusercontent.com/51126784/63055874-058d3400-bf11-11e9-98a3-36b2150f8999.png)

## Credits
This application uses Open Source components. You can find the source code of their open source projects along with license information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project:
- [RTGraph](https://github.com/ssepulveda/RTGraph)
- Copyright (c) 2014 Sebastián Sepúlveda
- MIT License: https://github.com/ssepulveda/RTGraph/blob/master/LICENSE

Project:
- [PID controller GUI](https://github.com/ussserrr/pid-controller-gui)
- Copyright (c) 2018 
- MIT License: https://github.com/ussserrr/pid-controller-gui/blob/master/LICENSE

Project:
- [Process Control Temperature Lab](https://github.com/APMonitor/arduino)
- Copyright (c) 2017 John Hedengren
- Apache License 2.0: https://github.com/APMonitor/arduino/blob/master/LICENSE

Icons:
- Icons made by [Freepik](https://www.flaticon.com/authors/freepik) from www.flaticon.com is licensed by [Creative Commons BY 3.0](http://creativecommons.org/licenses/by/3.0/)
- Icons made by [Those Icons](https://www.flaticon.com/authors/those-icons) from www.flaticon.com is licensed by [Creative Commons BY 3.0](http://creativecommons.org/licenses/by/3.0/)
- Icons made by [xnimrodx](https://www.flaticon.com/authors/xnimrodx) from www.flaticon.com is licensed by [Creative Commons BY 3.0](http://creativecommons.org/licenses/by/3.0/)
