# SAIM – SeismoArch Earthquake Early Warning System
SAIM is a building-level earthquake early warning prototype developed during Nexora Hacks 2026.

## Overview
The system detects early seismic vibrations inside a structure and delivers real-time mobile alerts to occupants before strong destructive shaking occurs.
The prototype demonstrates how localized sensing and rapid alert delivery can reduce response time in high-rise buildings.

## System Components
- Hand-fabricated scaled building model
- Distributed vibration sensors
- Microcontroller-based data acquisition
- Real-time monitoring dashboard
- Mobile alert application with floor-aware notifications

## Data Logging
During operation, vibration readings are logged with timestamps and can be exported to Excel format for offline analysis, validation, and reporting.

## Repository Structure
- firmware/     → Embedded code for vibration sensing and alert triggering
- dashboard/    → Real-time monitoring dashboard, backend services, and Firebase Cloud Messaging (Node.js)
- mobile-app/   → Mobile application for receiving earthquake alerts

## Notes
This repository contains a hackathon prototype. The code is hardware- and environment-specific and is not intended to be run without the corresponding physical setup.
