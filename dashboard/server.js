// server.js — SAIM Final Integration (FCM + Dashboard + Pico Bridge)

import { SerialPort } from "serialport";
import { ReadlineParser } from "@serialport/parser-readline";
import { Server } from "socket.io";
import { createServer } from "http";
import admin from "firebase-admin";
import fs from "fs";

// --- Firebase Admin Setup ---
const serviceAccount = JSON.parse(fs.readFileSync("./saim-firebase-admin.json"));
admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });

// --- Helper: single, unified FCM alert ---
async function sendAlertToAllFloors(magnitude = null) {
  try {
    const magText = magnitude
      ? `⚠️ Magnitude: ${magnitude} on Richter scale ⚠️`
      : "";
    const bodyText = `${magText}\n Follow these instructions:`;

    await admin.messaging().send({
      topic: "floor_all",
      notification: {
        title: "🌍 SAIM | Earthquake Alert 🌍",
        body: bodyText,
      },
      android: { priority: "high" },
    });

    console.log("✅ Unified FCM Alert sent");
  } catch (err) {
    console.error("❌ FCM Alert failed to send", err.message);
  }
}

// --- HTTP server for Socket.io ---
const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: "*" },
});

// --- Serial Port Setup (adjust COM port if needed) ---
const port = new SerialPort({ path: "COM10", baudRate: 115200 });
const parser = port.pipe(new ReadlineParser({ delimiter: "\r" }));

// --- Richter Calculation Helper ---
function calculateRichter(values) {
  if (!values.length) return 0;
  const avg = values.reduce((a, b) => a + b, 0) / values.length;
  const g = avg / 9.81; // convert to g
  const log = Math.log10(g + 1e-6);

  // --- Normalize to 3–6 range empirically ---
  const M = 3 + (log + 3) * 0.75; // log≈–3→M≈3, log≈0→M≈6
  return M.toFixed(2);
}

let lastFiveVibrations = [];

// --- Handle incoming serial data from Pico ---
parser.on("data", async (line) => {
  line = line.trim();
  if (!line) return;

  // 🔔 Global alert trigger
  if (line.includes("ALERT,ALERT,ALERT") || line.includes("ALERT ALERT ALERT")) {
    console.log("🚨 GLOBAL ALERT DETECTED!");

    // --- Richter scale calculation from last 5 readings ---
    const magnitude = calculateRichter(lastFiveVibrations);
    console.log(`📊 Estimated Magnitude: ${magnitude} on Richter scale`);

    // --- Send alert to dashboard ---
    io.emit("alert", { magnitude });

    // --- Send unified FCM alert ---
    await sendAlertToAllFloors(magnitude);

    // Reset buffer
    lastFiveVibrations = [];
    return;
  }

  // 🧠 Sensor data (vibration, tilt, piezo)
  const parts = line.split(",").map(Number);
  if (parts.length === 3 && parts.every((v) => !isNaN(v))) {
    const [vibration, tilt, piezo] = parts;

    // Re-added sensor data logging
    console.log(`📈 Vibration: ${vibration} | Tilt: ${tilt} | Piezo: ${piezo}`);

    // Store only last 5 vibration readings
    lastFiveVibrations.push(vibration);
    if (lastFiveVibrations.length > 5) lastFiveVibrations.shift();

    // Emit to dashboard
    io.emit("sensorData", { vibration, tilt, piezo });
    return;
  }

  // 🧩 Any other system messages
  io.emit("systemMessage", line);
  console.log("ℹ️ System message:", line);
});

// --- Socket.io connections ---
io.on("connection", () => console.log("🟢 Dashboard connected"));

// --- Start bridge server ---
httpServer.listen(5000, () => console.log("✅ SAIM Bridge server running on port 5000"));
