# Quantum Attack & Crypto-Agility Demo

A live demo pipeline that shows why government/citizen data systems using
RSA/ECC today are exposed to a future Cryptographically Relevant Quantum
Computer (CRQC) — and how a **crypto-agility gateway** re-encrypts flagged
traffic under a post-quantum hybrid scheme in response.

It runs Shor's algorithm (order-finding) on a real quantum backend (Qiskit
Aer simulator, or optionally IBM Quantum hardware), factors a toy RSA
modulus, flags the intercepted "packet" as compromised, re-encrypts it with
a hybrid **ML-KEM + AES-256-GCM** scheme, and pushes a live alert to a
phone/browser HUD over WebSocket.

## What it demonstrates

```
ATTACKER (wire-tap)  ->  DETECTOR (flags vulnerable crypto)  ->  CRYPTO-AGILE GATEWAY (hybrid PQC re-encrypt)  ->  MOBILE ALERT (WebSocket)
```

1. A "packet" of citizen/government data (e.g. land records, banking core,
   defence comms — see `gov_systems_inventory.csv`) is intercepted on the
   wire.
2. The **detector** flags it if it's using a quantum-vulnerable algorithm
   (RSA, ECC) and/or shows an exfiltration-like traffic pattern.
3. A real **Shor's algorithm** quantum circuit is executed (period-finding
   for N=15) to demonstrate the RSA modulus being factored in polynomial
   time on a CRQC.
4. The **crypto-agility gateway** immediately re-encrypts the payload under
   a hybrid post-quantum scheme (ML-KEM key establishment + AES-256-GCM),
   and verifies the round-trip.
5. A **CRITICAL THREAT DETECTED** alert is broadcast live via WebSocket to
   a connected mobile/browser HUD.

## Project structure

| File | Purpose |
|---|---|
| `server_bridge.py` | **The server.** Flask + Flask-SocketIO app. Serves the HUD page, runs the attack→detect→remediate pipeline, and broadcasts alerts. This is the file you run. |
| `crypto.py` | The crypto-agility library — the hybrid `AgileEncryptor` (KEM + AES-256-GCM), the vulnerable `LegacyRSA` stand-in, and the inventory risk scanner. Imported by `server_bridge.py`. |
| `mob.html` | The mobile/browser HUD — sci-fi terminal display with a standby screen and a full-screen critical alert screen. Served by default at `/`. |
| `index.html` | A simpler, alternate alert screen (dataset name only). Served as a fallback if `mob.html` is missing. |
| `gov_systems_inventory.csv` | Sample dataset of government systems (department, algorithm, key length, records at risk, priority) used to pick which "packet" gets attacked. |
| `shor.py` | Standalone script to run the real Shor period-finding circuit on actual IBM Quantum hardware (free tier) via `qiskit-ibm-runtime`, outside of the web app. |
| `attack and intercept.py` | Standalone CLI version of the full attack/detect/remediate pipeline (multi-packet, threaded, terminal-only — no web server). Useful for a quick terminal demo without the HUD. |
| `M.PY` | Legacy/duplicate copy of an earlier `server_bridge.py` (ran on port 5000). **Not needed** — kept only for reference; use `server_bridge.py` instead. |
| `requirements.txt` | Python dependencies. |
| `post quantum cryptography Presentation (1).pptx` | **PowerPoint Presentation.** Slide deck covering the quantum threat model, Shor's algorithm, PQC crypto-agility gateway architecture, and project walkthrough. |
| `ANIMATION.mp4` | **Demo Animation Video.** Recorded video demonstration showcasing the live attack simulation, quantum key cracking, and mobile HUD alerts. |

---

## 📖 Detailed File-by-File Breakdown (In Simple English)

### 1. 🔑 `crypto.py` — *The Quantum-Proof Lock System*
* **What it does**: Provides the core Post-Quantum Cryptography (PQC) and crypto-agility engine.
* **How it works**:
  * Acts like a flexible lock-and-key manager. If an old encryption scheme (like RSA) is found to be vulnerable, it lets applications instantly switch to quantum-safe algorithms without altering application code.
  * Implements `ToyKEM` (a simulated NIST FIPS 203 ML-KEM / Kyber lattice-based key exchange algorithm).
  * Combines `ToyKEM` with `AES-256-GCM` inside `AgileEncryptor` to provide unbreakable, high-speed hybrid encryption.
  * Contains `scan_systems()`, which reads database records and calculates quantum risk deadlines ($Q\text{-Day}$, 2035, 2045) based on data lifetime requirements (e.g. land titles needing 100 years of secrecy).

---

### 2. ⚛️ `shor.py` — *The Quantum Cracking Engine*
* **What it does**: Executes Shor's algorithm to break traditional RSA encryption using quantum circuits.
* **How it works**:
  * Shor's algorithm finds hidden mathematical periodicities in RSA numbers.
  * Builds a 12-qubit Qiskit quantum circuit (`qpe_shor`) incorporating controlled modular exponentiation ($7^x \bmod 15$) and an Inverse Quantum Fourier Transform (`qft_dagger`).
  * Connects to real physical quantum computers via `QiskitRuntimeService` (IBM Quantum Cloud) or simulates them locally.
  * Extracts measured quantum phases and calculates the period $r=4$ to factor $15$ into $3 \times 5$, proving quantum computer capability to crack RSA keys.

---

### 3. 🌐 `server_bridge.py` — *The Main Attack & Alert Bridge (Port 8080)*
* **What it does**: Runs the live backend server that connects quantum simulations to the mobile alert screens.
* **How it works**:
  * Uses Flask and Flask-SocketIO to run a web server on port `8080`.
  * Automatically detects your local Wi-Fi IP address so smartphones on the same network can connect to `http://<IP>:8080`.
  * Executes a Qiskit Aer quantum circuit simulation on command (`/trigger` endpoint or pressing `[ENTER]` in the terminal).
  * Streams real-time alert events (`HNDL_ATTACK_ALERT`) over WebSockets to mobile HUD devices and immediately re-encrypts the target dataset with `AgileEncryptor` (ML-KEM-512).

---

### 4. 🖥️ `M.PY` — *Terminal Interactive Server Variant (Port 5000)*
* **What it does**: An alternative setup of the quantum attack server running on port `5000`.
* **How it works**:
  * Identical in core functionality to `server_bridge.py`, but configured for port `5000`.
  * Runs a background thread (`terminal_controller`) that listens for user input in the console window. Pressing `[ENTER]` triggers an instant simulated quantum attack workflow.

---

### 5. 📡 `attack and intercept.py` — *Full Network Wiretap & DPI Pipeline*
* **What it does**: Simulates a complete, multi-threaded cyber attack, real-time detection, and automated PQC gateway defense.
* **How it works**:
  * **Attacker Thread**: Taps network wires and intercepts data packets from both sample hardcoded sources and `gov_systems_inventory.csv`. If an RSA packet is detected, it runs an IBM Quantum Shor attack.
  * **Detector Sensor**: Scans packets for security flaws (e.g. RSA algorithm weaknesses, unusual data transfer volume) and calculates a risk score (0.00 to 1.00).
  * **Hybrid Gateway**: If risk $\ge 0.70$, `HybridPQCGateway` steps in, re-encrypting data with AES-256-GCM and ML-KEM-768 lattice key encapsulation to neutralize the threat.

---

### 6. 📊 `gov_systems_inventory.csv` — *Government System Risk Database*
* **What it does**: Stores data about critical government digital infrastructure.
* **How it works**:
  * Contains 15 dataset records spanning Land Records, Treasury Banking, Health eHospital, DigiLocker, Defense Communications, and Municipal APIs.
  * Tracks key attributes: active algorithm (`RSA-2048`, `ECC-P384`, `AES-256`, `hybrid-PQC`), sensitivity rating (1–5), public exposure, records at risk, required secrecy duration (years), and migration priority.

---

### 7. 📱 `mob.html` — *Cyberpunk Mobile Threat HUD*
* **What it does**: A futuristic, HUD-styled web interface for mobile devices.
* **How it works**:
  * Styled with CRT scanlines, neon corner frames, and animated status rings.
  * **Standby Mode**: Shows a live packet counter and scrolling cipher monitoring ticker.
  * **Alert Mode**: Triggers when a WebSocket `HNDL_ATTACK_ALERT` is received. Flashes full-screen red, plays a sawtooth audio siren, vibrates the device, animates quantum bit strings (`|0100⟩`), and displays the compromised dataset name, math factors, and PQC protection status.

---

### 8. 🚨 `index.html` — *Tailwind CSS High-Alert Mobile Screen*
* **What it does**: A clean, high-impact emergency alert screen for smartphones.
* **How it works**:
  * Styled with Tailwind CSS for fast rendering on mobile browsers.
  * Stays in standby until a Socket.IO attack event arrives.
  * Displays the target dataset name in bold typography, plays Web Audio alarm tones, vibrates the phone, and requests permission to issue native OS notification banners.

---


## Requirements

- Python 3.10+
- Two devices on the **same Wi-Fi network** if you want to view the HUD on
  your phone (server on laptop, browser on phone) — or just use a browser
  on the same machine.

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
python3 server_bridge.py
```

This prints something like:

```
======================================================================
 SYSTEM 1: QUANTUM ATTACK & CRYPTO-AGILITY SERVER
======================================================================
 Local Machine IP      :http://192.168.29.167:8080
 Mobile Display URL    : http://10.65.179.101:8080
 Trigger Endpoint      : http://192.168.29.167:8080/trigger
 Standby Reset URL     : http://192.168.29.167:8080/reset
 Health Check          : http://192.168.29.167:8080/health
======================================================================
```

Open the **Mobile Display URL** on your phone's browser (same Wi-Fi) or in
a browser tab on your own machine. It starts on a green "standby" screen
monitoring the wire.

### Triggering the attack simulation

Any of these fire the full attack → detect → remediate → alert pipeline:

- **Press Enter** in the terminal running the server.
- Visit `/trigger` in a browser, or `curl http://<IP>:8080/trigger`.
- Emit a `trigger_attack_simulation` WebSocket event from a connected
  client.

The HUD flips to a red **CRITICAL THREAT DETECTED** screen showing the
target dataset, the measured quantum phase register, the derived period
`r`, and the factored RSA modulus — all live from the terminal's Qiskit run.

### Resetting the HUD

Visit `/reset` (or `curl http://<IP>:8080/reset`) to flip the HUD back to
standby.

### Changing the port

The server defaults to port `8080`. Override with an environment variable:

```bash
PORT=9000 python3 server_bridge.py
```

Both `mob.html` and `index.html` connect back to whatever host/port
actually served the page (`window.location.origin`), so there's nothing
else to update when you change the port.

## HTTP / WebSocket reference

| Route | Method | Description |
|---|---|---|
| `/` | GET | Serves `mob.html` (falls back to `index.html`) |
| `/mob.html` | GET | Serves the HUD directly |
| `/index.html` | GET | Serves the simple alert screen directly |
| `/trigger` | GET | Kicks off the attack/detect/remediate pipeline |
| `/reset` | GET | Resets the HUD to standby |
| `/health` | GET | Liveness check, returns `{"status": "ok", "port": ...}` |
| `HNDL_ATTACK_ALERT` | Socket.IO event (server→client) | Pushes `dataset_name`, `phase`, `factors`, `r`, `backend` to the HUD |
| `RESET_STANDBY` | Socket.IO event (server→client) | Tells the HUD to return to standby |
| `trigger_attack_simulation` | Socket.IO event (client→server) | Alternate way to trigger the pipeline over WebSocket instead of HTTP |

## Notes

- The Shor circuit factors a toy modulus (N=15) — this is the canonical,
  widely-used teaching example for period-finding, since factoring a
  real 2048-bit RSA modulus isn't feasible on today's hardware. The point
  demonstrated is the *algorithm*, not breaking a real key.
- `crypto.py`'s `ToyKEM` is an educational stand-in for a real lattice KEM.
  The comments flag exactly where to swap in `liboqs` ML-KEM-768 (NIST
  FIPS 203) for a production deployment.
- `gov_systems_inventory.csv` is illustrative sample data for the demo,
  not a real system inventory.

---

## 📽️ PowerPoint Presentation (`post quantum cryptography Presentation (1).pptx`)

The workspace includes a complete slide deck file: **[`post quantum cryptography Presentation (1).pptx`](file:///c:/Users/Lakshmitha/OneDrive/Desktop/VS%20code/F_B/post%20quantum%20cryptography%20Presentation%20(1).pptx)**.

### Slide Deck Content Summary:
1. **Executive Summary & Threat Landscape**: Highlights the vulnerability of existing public-key infrastructure (RSA-2048 / ECC-P384) against Cryptographically Relevant Quantum Computers (CRQCs).
2. **Mathematical Foundations**: Breaks down Shor's order-finding quantum algorithm, modular exponentiation ($a^x \bmod N$), and Inverse Quantum Fourier Transform (IQFT).
3. **Crypto-Agility Architecture**: Explains zero-downtime PQC migration using hybrid encapsulation (NIST FIPS 203 ML-KEM-512/768 + AES-256-GCM).
4. **Live System Pipeline**: Details the multi-threaded Deep Packet Inspection wiretap, automated threat detector scoring, and WebSocket emergency mobile dispatch.
5. **System Inventory & Timeline**: Reviews government sector risk classification ($Q\text{-Day}$, 2035, 2045 migration deadlines) based on required data secrecy years.

---

## 🎬 Video Animation & Demonstration (`ANIMATION.mp4`)

The workspace includes a high-definition video recording file: **[`ANIMATION.mp4`](file:///c:/Users/Lakshmitha/OneDrive/Desktop/VS%20code/F_B/ANIMATION.mp4)**.

### Animation & Visual Features Showcase:
* **Interactive HUD Animations (`mob.html`)**:
  * **Radar & Status Ring Rotation**: Continuous 360° rotation (`@keyframes spin`) with pulsing green monitoring indicator (`@keyframes pulse`).
  * **Live Ticker Marquee**: Smooth horizontal scrolling text bar displaying real-time cipher watch indicators (`RSA-2048`, `ML-KEM-768`).
  * **Emergency Alert Vignette**: Pulsing radial red vignette flash overlay on critical threat detection.
  * **Laser Scanline Sweep**: Animated vertical laser scan line moving across the HUD screen.
  * **Glitch Text Typography**: RGB-split glitch text effect (`@keyframes text-glitch`) on compromised dataset titles.
  * **Quantum Register Digital Roll**: Scrambling binary digit roll (`animateRegister()`) cycling random `0`s and `1`s before locking into the measured quantum state `|0100⟩`.
  * **Web Audio Siren & Haptic Vibration**: Dynamic frequency-ramped sawtooth audio sirens synchronized with smartphone vibration pulses.
* **Pipeline Demonstration**: Visualizes the step-by-step transition from passive wiretap packet interception to quantum key cracking, instant WebSocket push alert, and post-quantum hybrid re-encryption.

---
