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
pip3 install pyserial pandas flask requests
