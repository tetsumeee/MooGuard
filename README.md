# MooGuard
# MooGuard: Landslide Detection & Early Warning System

MooGuard is an autonomous, edge-computing landslide detection system designed for rural agricultural environments. By utilizing multi-sensor fusion and on-device processing, it provides real-time disaster monitoring without dependency on persistent cloud connectivity.

## Core Features
* [cite_start]**Edge-AI Processing:** Risk analysis is performed locally on the device, ensuring alerts remain functional during severe weather events when cloud connectivity is typically lost[cite: 109, 116].
* [cite_start]**Multi-Sensor Fusion:** Monitors environmental stability via soil moisture, rainfall intensity, standing water accumulation, ambient temperature, and ground tilt [cite: 108, 161, 338-342].
* [cite_start]**Predictive Ground-Tilt Detection:** Utilizes the MPU6050 gyroscope to identify micro-vibrations and ground displacement—the "pre-collapse phase"—providing 15–30 minutes of additional evacuation time compared to traditional moisture-only systems[cite: 367, 368].
* [cite_start]**Reliable Alerting:** Dispatches critical risk status via a hybrid notification system, including Web Push (PWA), SMS fallback, and KakaoTalk integration [cite: 298-300].

## Hardware Architecture
* [cite_start]**Controller:** Raspberry Pi 4B (4GB RAM)[cite: 157].
* [cite_start]**Interface:** 2.8-inch SPI TFT LCD (ILI9341) for local status dashboard[cite: 336].
* [cite_start]**Sensor Suite:** * MPU6050 (3-axis Gyroscope/Accelerometer)[cite: 342].
    * [cite_start]DHT22 (Temp/Humidity)[cite: 338].
    * [cite_start]Soil Moisture (Capacitive)[cite: 340].
    * [cite_start]Rain Sensor Module[cite: 339].
    * [cite_start]Water Level Sensor[cite: 341].
* [cite_start]**Enclosure:** 3D-printed PETG+CF with an IP67-rated waterproof seal[cite: 163, 349].

## Software Stack
* **Language:** Python 3.x
* [cite_start]**Core Logic:** Real-time data acquisition via MCP3008 (SPI protocol)[cite: 157].
* **Dashboard:** Custom GUI built with Pillow (PIL) for landscape TFT rendering.
* [cite_start]**Connectivity:** 4G LTE/WiFi with offline-first synchronization to Firebase[cite: 163, 216].

## Academic Implementation
This project was developed for the *2025-2 IBTI|ISE Capstone Design Course* at Inha University, School of Global Convergence Studies.

---
### Installation
1. [cite_start]Ensure `python3-pip` and `libgpiod2` are installed[cite: 212].
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure your API credentials in a `.env` file (excluded from git).
4. Execute via: `python main.py`.

---
*Developed by Team 2. All hardware connections utilize strict I2C and SPI bus management to ensure operational stability.*
