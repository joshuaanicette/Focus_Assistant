# Focus_Assistant

# 🎯 Focus Assistant Device

## 1. Problem Statement
Students often get distracted during study sessions — leaving the desk, taking longer breaks than planned, or losing track of time. Without accountability, focus time suffers.

**Goal:**  
Build a **Focus Assistant Device** that detects presence at the desk, provides **real-time feedback** using LEDs and a buzzer, and logs study sessions to a **Raspberry Pi dashboard**.

---

## 2. Tools & Hardware
- **Arduino Mega 2560** (Elegoo Starter Kit)
- **Raspberry Pi 4**
- **HC-SR04 Ultrasonic Sensor**
- **RGB LED (4-pin, common cathode)** + **3 × 220Ω resistors**
- **Active Buzzer**
- **Breadboard + jumper wires**
- **USB cable** (Arduino ↔ Raspberry Pi)

---

## 3. System Overview

### Arduino (focus monitor)
- Reads distance from ultrasonic sensor.
- Determines state:
  - 🟢 **FOCUS**: seated
  - 🟢 **SHORT BREAK (<2 min)**: away briefly
  - 🔵 **WARNING (2–5 min)**: away too long (1 short beep every 30s)
  - 🔴 **DISTRACTED (>5 min)**: away excessively (flashing red + triple beep every 30s)
- Drives **RGB LED + active buzzer**.
- Sends state over **USB serial**.

### Raspberry Pi (logger & dashboard)
- Logs state + timestamp into `focus_log.csv`.
- Provides **Flask web dashboard** with stats + CSV download.
- Optional desktop notifications and audio alerts.

---

## 4. Hardware Wiring

### 4.1 Power
- Arduino **5V → Breadboard Red (+) rail**
- Arduino **GND → Breadboard Blue (–) rail**

### 4.2 Ultrasonic Sensor (HC-SR04)
- **VCC → Red rail (5V)**
- **GND → Blue rail (GND)**
- **TRIG → D9**
- **ECHO → D10**

### 4.3 RGB LED (Common Cathode)
- **Red leg → 220Ω → D5**
- **Green leg → 220Ω → D6**
- **Blue leg → 220Ω → D7**
- **Common (longest leg) → Blue rail (GND)**

> ⚠️ If using **common anode**, connect longest leg to +5V and invert logic in code.

### 4.4 Active Buzzer
- **+ → D8**
- **– → Blue rail (GND)**

---

## 5. Arduino Code
The Arduino:
- Reads distance using `pulseIn()`.
- Classifies focus state by away time.
- Drives LED + buzzer feedback.
- Prints state to Serial for Pi logging.

👉 See [`arduino/focus_assistant.ino`](arduino/focus_assistant.ino)

---

## 6. Raspberry Pi Scripts

### Install dependencies
```bash
sudo apt update
sudo apt install -y python3-pip alsa-utils libnotify-bin
sudo apt install python3-venv -y
python -m venv venv
- venv is the name of the virtual environment folder (you can name it anything)
source venv/bin/activate
pip3 install pyserial pandas flask requests
```

Create project folder
```bash
mkdir focus_assistant
cd focus_assistant
nano focus_app.py
```

(Add the Python code, then press CTRL+X → Y → Enter to save and exit.)

## 7. Running the Project

Wire components as shown in Section 4.

Upload Arduino sketch via Arduino IDE.

Connect Arduino → Pi via USB.

On Raspberry Pi, run:
```bash
python3 focus_app.py
```
🔧 Focus Assistant – Testing, Results & Quick Start
Open Browser

- After running the app, open your browser at:
➡️ http://<your-pi-ip>:8080

## 8. Testing & Calibration
Calibrate Distance Threshold

Sit at desk → note reading (25–40 cm typical).

Set PRESENT_CM ~10–15 cm higher (e.g., 50 cm).

Check LEDs

- Present → 🟢 Green

- Away 2–5 min → 🔵 Blue

- Away >5 min → 🔴 Flashing Red

Check Buzzer

- Short beep → Warning

- Triple beep → Distracted

Verify Logging

```bash
tail -f focus_log.csv
```

Dashboard View

- Displays total focus minutes

- Tracks away minutes

- Logs event counts

## 9. Results

✅ Automatic focus tracking via ultrasonic sensor

✅ Real-time feedback (LED + buzzer) reduced long distractions

✅ CSV log + dashboard provided daily summaries

✅ Built with only Arduino Mega + Raspberry Pi 4 + starter kit

## 10. Future Improvements

⏱️ Add Pomodoro mode (25/5 timers)

📟 Add LCD/OLED countdown display

💾 Use SQLite for long-term analytics**

📱 Add Telegram/phone alerts

🔒 Auto-lock screen when distracted too long

## 11. Quick Start
```bash
git clone https://github.com/<your-repo>/focus-assistant.git
cd focus-assistant
python3 focus_app.py
```

Then open in your browser:
➡️ http://<pi-ip>:8080


## 📷 Demo<img width="1426" height="730" alt="Screenshot 2025-08-17 124335" src="https://github.com/user-attachments/assets/6ca42dde-b9fa-4bef-80ca-0a63378184ea" />

[focus_assistant_log.pdf](https://github.com/user-attachments/files/21823627/focus_assistant_log.pdf)
