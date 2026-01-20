# SAIM — SeismoArch Intelligence Model  
### Earthquake Early Warning & Structural Monitoring System

**Developed during Arctic League of Code (Winter 2025–26)**

---

## Overview

SAIM (SeismoArch Intelligence Model) is a low-cost, building-level earthquake early-warning system designed to detect **primary seismic waves (P-waves)** and issue alerts **seconds before destructive shaking occurs**.

By leveraging multi-point vibration sensing, real-time signal processing, and mobile notifications, SAIM aims to reduce human response time during earthquakes and improve structural safety awareness.

---

## Problem Statement

Most earthquake alert systems either operate at large geographic scales or rely on high-cost infrastructure. As a result, individual buildings often receive alerts too late or not at all.

SAIM addresses this gap by enabling **localized, low-latency earthquake detection at the building level**, where even a few seconds of early warning can save lives.

---

## How It Works

1. Multiple vibration sensors are placed at key structural points  
2. Sensor data is streamed through a microcontroller for real-time analysis  
3. Early seismic activity (P-waves) is detected before strong motion begins  
4. Alerts are triggered instantly and delivered to occupants via a mobile app  
5. All vibration and event data is logged and visualized on a live dashboard  

This architecture prioritizes speed, reliability, and cost efficiency.

---

## System Architecture

- **Sensors:** Multi-point vibration sensing for spatial awareness  
- **Edge Processing:** Early-wave detection and threshold logic  
- **Backend:** Real-time data handling and alert triggering  
- **Frontend:** Mobile app for alerts and dashboards for visualization  

---

## Key Features

- Early detection using primary seismic waves  
- Multi-sensor spatial monitoring  
- Real-time mobile alerts  
- Live vibration and event dashboard  
- Modular and low-cost design  
- Scalable architecture for multi-building deployment  

---

## Built With

- Embedded C / MicroPython  
- Raspberry Pi Pico  
- MPU6050 vibration sensors  
- Node.js  
- Firebase Cloud Messaging (FCM)  
- Flutter  
- Data visualization dashboards  

---

## Project Status

This repository represents the **Arctic League of Code implementation** of SAIM.  
The system is functional and serves as a foundation for future research and development.

---

## Future Work

- Machine learning models to estimate S-wave arrival time  
- Adaptive thresholds based on building characteristics  
- Long-term structural health monitoring  
- Enhanced mobile visualization and alert logic  
