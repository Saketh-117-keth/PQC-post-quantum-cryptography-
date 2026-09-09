"""Run on IBM Quantum (free tier) at the hackathon:
   pip install qiskit qiskit-ibm-runtime
"""
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
import numpy as np
import math
import os

# ---- Shor period-finding for N=15, a=7  (the canonical demo) ----
# Modular exponentiation circuit: |x> -> |7^x mod 15>
def c_amod15(a, power):
    U = QuantumCircuit(4)
    for _ in range(power):
        if a in (2, 4, 8, 13, 14):
            U.swap(2, 3); U.swap(1, 2); U.swap(0, 1)
        if a in (7, 8, 11, 12, 13, 14):
            U.swap(0, 3); U.swap(1, 2)
    U = U.to_gate(); U.name = f"{a}^{power} mod 15"
    return U.control()

# FIX: Proper inverse QFT (IQFT) implementation
def qft_dagger(qc, n):
    """n-qubit inverse QFT on the first n qubits of qc."""
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-math.pi / float(2 ** (j - m)), m, j)
        qc.h(j)

def qpe_shor(a=7, n_count=8):
    qc = QuantumCircuit(4 + n_count, n_count)
    for q in range(n_count): qc.h(q)                       # superposition
    qc.x(n_count)                                          # FIX: |1> work register (was hardcoded 4, now uses n_count)
    for q in range(n_count): qc.append(c_amod15(a, 2**q), [q] + list(range(n_count, n_count + 4)))
    qft_dagger(qc, n_count)                                # FIX: proper inverse QFT (was plain qc.h which is wrong)
    qc.measure(range(n_count), range(n_count))
    return qc

qc = qpe_shor()

# ---- IBM Quantum account setup ----
# Option 1: set environment variable IBM_QUANTUM_TOKEN=<your_token>
# Option 2: the script will prompt you to paste your token once, then save it
IBM_TOKEN = os.environ.get("IBM_QUANTUM_TOKEN", "").strip()
if IBM_TOKEN:
    # Save (or overwrite) the account so future runs work without re-entering
    QiskitRuntimeService.save_account(
        channel="ibm_quantum_platform",
        token=IBM_TOKEN,
        overwrite=True,
    )

try:
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
except Exception:
    # Account not saved yet — ask once and save for future runs
    IBM_TOKEN = input("Paste your IBM Quantum API token (from quantum.ibm.com): ").strip()
    QiskitRuntimeService.save_account(
        channel="ibm_quantum_platform",
        token=IBM_TOKEN,
        overwrite=True,
    )
    service = QiskitRuntimeService(channel="ibm_quantum_platform")

backend = service.least_busy(simulator=False, operational=True)
print("Running Shor(15) on", backend.name)
sampler = Sampler(mode=backend)
job = sampler.run([transpile(qc, backend)], shots=1024)

# FIX: Newer Qiskit returns BitArray; use get_counts() on the data attribute correctly
result = job.result()[0]
# The classical register name may be "c" or "meas" depending on Qiskit version
counts = result.data.meas.get_counts() if hasattr(result.data, "meas") else result.data.c.get_counts()

# Phase -> period r via continued fractions; then factor 15
from fractions import Fraction
n_count = 8                                                # must match qpe_shor default

# Try candidates from most- to least-frequent measurement
factors_found = False
for bitstring, _ in sorted(counts.items(), key=lambda x: -x[1]):
    phase = int(bitstring, 2) / 2**n_count
    if phase == 0:
        continue                                           # trivial phase -> skip
    r = Fraction(phase).limit_denominator(15).denominator
    if r % 2 != 0:
        continue                                           # odd period -> useless for factoring
    p = math.gcd(pow(7, r // 2, 15) - 1, 15)
    q_factor = math.gcd(pow(7, r // 2, 15) + 1, 15)
    if p * q_factor == 15 and p != 1 and q_factor != 1:
        print(f"Measured phase {phase:.3f} -> period r={r} -> factors {p} x {q_factor}")
        print("RSA-15 BROKEN ON REAL QUANTUM HARDWARE")
        factors_found = True
        break
    print(f"  phase {phase:.3f} -> r={r} -> trivial ({p},{q_factor}), trying next...")

if not factors_found:
    print("No valid period found in this shot batch - re-run the job (normal ~25% of the time).")