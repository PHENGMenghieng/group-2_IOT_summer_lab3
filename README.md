# group-2_IOT_summer_lab3

LAB3 LAB3


Explanations:

1: Boot Up
ESP32 powers on and prints the Blynk logo to the serial terminal.
Configures IR pin (D14) as input, Servo pin (D13) as PWM, and TM1637 (D16, D17) for the display.
Forces servo to 0 degree (Gate Closed) and sets the display to 0.

2: Get Online (WiFi + Blynk)
Connects to "Robotic WIFI" and waits until it gets an IP address.
Connects to the Blynk Cloud using your BLYNK_AUTH token.
Resets app dashboard: sets V0 to "Not Detected" and V2 to 0.

3: Main while True Loop
Calls blynk.run() to keep the cloud connection alive.
Scans the IR sensor pin to check for objects.
Every 500ms, updates V0 and V2 to keep the app widgets fresh.

4: Auto Mode (IR Sensor Triggered)
Count: detection_count increases by 1.
Display: Instantly updates the physical TM1637 screen and sends the count to V2 on the app.
Open: Servos moves to 90 degree and app status (V0) changes to "Detected".
Hold: Pauses for 3 seconds while keeping blynk.run() looping in the background.Close: Servo drops back to 0 degree
Clear: Waits until the object fully leaves the IR sensor before allowing the loop to reset.

5: Manual Mode (Blynk App Override) this is when you control it from your phone
V3 Switch: Flipping this to 1 sets manual_mode = True, disabling the automatic IR sensor code.
V1 Slider: Dragging the slider sends a 0–180 value to the ESP32, moving the servo to that exact angle manually.

https://github.com/user-attachments/assets/63251886-d096-49f6-bfd8-cc039d0b44b4



