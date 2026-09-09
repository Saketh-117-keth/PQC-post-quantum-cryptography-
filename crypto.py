"""Sovereign Crypto-Agility Layer — post-quantum migration library.
Drop-in design: no application code changes when algorithms swap.
Production: replace ToyKEM with liboqs ML-KEM / ML-DSA (NIST FIPS 203/204).
"""
import os, json, hashlib, random
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# ---------------- Algorithm Registry (crypto-agility core) ----------------
REGISTRY = {}
def register(name, cls): REGISTRY[name] = cls
def kem(name): return REGISTRY[name]()

# ------------- Toy Module-LWE KEM (educational stand-in for ML-KEM/Kyber) --
class ToyKEM:
    """Simulated lattice KEM: keygen / encaps / decaps + shared secret."""
    name = "TOY-ML-KEM-512"
    n, q = 256, 3329
    def keygen(self):
        A  = [random.randrange(self.q) for _ in range(self.n)]
        s  = [random.randrange(3)-1   for _ in range(self.n)]   # small secret
        e  = [random.randrange(3)-1   for _ in range(self.n)]   # small error
        b  = [(A[i]*s[i]+e[i]) % self.q for i in range(self.n)] # LWE sample
        self._A, self._s = A, s
        return {"pub": {"A": A[:16], "b": b[:16]},
                "priv": {"hint": hashlib.sha256(str(s).encode()).hexdigest()[:16]}}
    def encaps(self, pub):
        seed = hashlib.sha256(json.dumps(pub["b"]).encode() + os.urandom(32)).digest()
        return {"ct": seed.hex(), "ss": hashlib.sha256(seed + b"ss").digest()}
    def decaps(self, ct, priv=None):
        return hashlib.sha256(bytes.fromhex(ct) + b"ss").digest()

class LegacyRSA:   # the vulnerable incumbent
    name = "RSA-2048 (quantum-vulnerable)"
    def keygen(self): return {"pub": {"N": "0xC1F3..."}, "priv": {"d": "0x5ECR3T..."}}

register("ML-KEM-512", ToyKEM); register("legacy-rsa", LegacyRSA)

# ---------------- Hybrid AES-256-GCM encryptor (AES + PQC KEM) -----------
def _kek(kdf_key):
    return HKDF(hashes.SHA256(), 32, salt=None, info=b"hybrid-kek").derive(kdf_key)

class AgileEncryptor:
    def __init__(self, algo="ML-KEM-512"):
        self.algo = algo
        self.kem = kem(algo)
        self.keys = self.kem.keygen()
    def encrypt(self, plaintext: bytes, aad=b"gov-record/v1") -> dict:
        enc = self.kem.encaps(self.keys["pub"]) if hasattr(self.kem, "encaps") else None
        key = _kek(enc["ss"] if enc else hashlib.sha256(b"rsa-key").digest())
        iv = os.urandom(12)
        c = Cipher(algorithms.AES(key), modes.GCM(iv)).encryptor()
        ct = c.update(plaintext) + c.finalize()
        return {"algo": self.algo, "iv": iv.hex(), "ct": ct.hex(), "tag": c.tag.hex(),
                "kem_ct": (enc or {}).get("ct")}
    def decrypt(self, bundle: dict) -> bytes:
        kc = bundle.get("kem_ct")
        kdf_key = (self.kem.decaps(kc, self.keys["priv"])
                   if hasattr(self.kem, "decaps") and kc
                   else hashlib.sha256(b"rsa-key").digest())
        d = Cipher(algorithms.AES(_kek(kdf_key)),
                   modes.GCM(bytes.fromhex(bundle["iv"]), bytes.fromhex(bundle["tag"]))).decryptor()
        return d.update(bytes.fromhex(bundle["ct"])) + d.finalize()

# ---------------- Crypto-inventory scanner (finds RSA everywhere) --------
LIFESPAN = {"citizen": 70, "land": 100, "health": 50, "financial": 40, "defence": 50}
def scan_systems(systems):
    out = []
    for s in systems:
        risk = ("CRITICAL" if s["algo"].startswith("RSA") and s["exposure"] == "public"
                else "HIGH" if s["algo"].startswith("RSA") else "MEDIUM")
        out.append({**s, "risk": risk,
                    "mgn_needed_by": LIFESPAN.get(s["data_type"], 50),
                    "quantum_deadline": "Q-Day" if risk == "CRITICAL" else ("2035" if risk == "HIGH" else "2045")})
    return out

if __name__ == "__main__":
    print("[1] Vulnerable today :", LegacyRSA().keygen()["pub"])
    ag = AgileEncryptor("ML-KEM-512")                      # <-- ONE-LINE migration
    record = b"Land Record #4471 | Owner: R. Sharma | Survey 12/3B"
    bundle = ag.encrypt(record)
    assert ag.decrypt(bundle) == record, "round-trip failed!"
    b = {k: (v[:24]+"..." if isinstance(v, str) and len(v) > 24 else v) for k, v in bundle.items()}
    print("[2] Migrated record  :", b)
    print("[3] Round-trip check : PASS  |  algorithm =", bundle["algo"])