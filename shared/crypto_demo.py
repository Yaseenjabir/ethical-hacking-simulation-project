"""
Cryptography Demo Module
Demonstrates password hashing concepts used in the brute force attack simulation.
"""

import hashlib
import os
import bcrypt
import time


# ─────────────────────────────────────────────
# 1. MD5 Hashing — Weak (no salt, fast, broken)
# ─────────────────────────────────────────────

def hash_md5(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


# ─────────────────────────────────────────────
# 2. SHA-256 Hashing — Stronger but still no salt
# ─────────────────────────────────────────────

def hash_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ─────────────────────────────────────────────
# 3. Salted SHA-256 — Better (unique per password)
# ─────────────────────────────────────────────

def hash_sha256_salted(password: str) -> tuple[str, str]:
    salt = os.urandom(16).hex()
    salted_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, salted_hash


def verify_sha256_salted(password: str, salt: str, stored_hash: str) -> bool:
    return hashlib.sha256((salt + password).encode()).hexdigest() == stored_hash


# ─────────────────────────────────────────────
# 4. Bcrypt — Modern standard (slow by design)
# ─────────────────────────────────────────────

def hash_bcrypt(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_bcrypt(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ─────────────────────────────────────────────
# 5. Brute Force Speed Comparison
#    Shows why algorithm choice matters for attackers
# ─────────────────────────────────────────────

def brute_force_speed_demo(password: str = "admin123") -> dict:
    wordlist = [
        "123456", "password", "admin", "admin123", "letmein",
        "qwerty", "abc123", "monkey", "111111", "dragon"
    ]

    results = {}

    # MD5 brute force speed
    target_md5 = hash_md5(password)
    start = time.perf_counter()
    for attempt in wordlist:
        if hash_md5(attempt) == target_md5:
            break
    results["md5_time_ms"] = round((time.perf_counter() - start) * 1000, 4)

    # SHA-256 brute force speed
    target_sha = hash_sha256(password)
    start = time.perf_counter()
    for attempt in wordlist:
        if hash_sha256(attempt) == target_sha:
            break
    results["sha256_time_ms"] = round((time.perf_counter() - start) * 1000, 4)

    # Bcrypt brute force speed (slow by design)
    target_bcrypt = hash_bcrypt(password)
    start = time.perf_counter()
    for attempt in wordlist:
        if verify_bcrypt(attempt, target_bcrypt):
            break
    results["bcrypt_time_ms"] = round((time.perf_counter() - start) * 1000, 4)

    return results


# ─────────────────────────────────────────────
# Demo runner — called from attack.ipynb
# ─────────────────────────────────────────────

def run_demo(password: str = "admin123"):
    print("=" * 60)
    print("  CRYPTOGRAPHY DEMO — Password Hashing & Brute Force")
    print("=" * 60)

    print(f"\n[*] Target password: '{password}'")

    print("\n--- 1. MD5 (Weak) ---")
    md5 = hash_md5(password)
    print(f"    Hash : {md5}")
    print(f"    Why weak: No salt, extremely fast to compute,")
    print(f"              rainbow tables exist for common passwords.")

    print("\n--- 2. SHA-256 (Better, still no salt) ---")
    sha = hash_sha256(password)
    print(f"    Hash : {sha}")
    print(f"    Why weak: Same password always produces same hash.")
    print(f"              Vulnerable to dictionary attacks.")

    print("\n--- 3. Salted SHA-256 (Good) ---")
    salt, salted = hash_sha256_salted(password)
    print(f"    Salt : {salt}")
    print(f"    Hash : {salted}")
    verified = verify_sha256_salted(password, salt, salted)
    print(f"    Verified: {verified}")
    print(f"    Why better: Unique salt means same password → different hash.")
    print(f"                Rainbow tables useless.")

    print("\n--- 4. Bcrypt (Modern Standard) ---")
    bh = hash_bcrypt(password)
    print(f"    Hash : {bh}")
    verified = verify_bcrypt(password, bh)
    print(f"    Verified: {verified}")
    print(f"    Why best: Built-in salt + intentionally slow (work factor).")

    print("\n--- 5. Brute Force Speed Comparison ---")
    speeds = brute_force_speed_demo(password)
    print(f"    MD5    cracked in : {speeds['md5_time_ms']} ms")
    print(f"    SHA256 cracked in : {speeds['sha256_time_ms']} ms")
    print(f"    Bcrypt cracked in : {speeds['bcrypt_time_ms']} ms")
    print(f"\n    Bcrypt is {round(speeds['bcrypt_time_ms'] / max(speeds['md5_time_ms'], 0.001))}x slower than MD5 — by design.")
    print(f"    With millions of attempts, this difference is critical.")

    print("\n" + "=" * 60)
    print("  CONCLUSION: Use bcrypt/argon2 for password storage.")
    print("  Weak hashes (MD5/SHA) make brute force attacks trivial.")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
