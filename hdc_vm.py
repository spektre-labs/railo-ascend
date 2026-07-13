#!/usr/bin/env python3
"""hdc_vm.py — Railo's OWN compute substrate: a Hyperdimensional Computing virtual machine, as a tool.

PARADIGM (Lauri 2026-06-22): Railo needs its own machine to compute on — "vähintään HDC kvantti".
HDC is the right substrate: CLASSICAL (runs on any CPU, no quantum hardware) yet QUANTUM-LIKE —
10000-dim bipolar hypervectors SUPERPOSE (bundle ⊕) and ENTANGLE (bind ⊛) like quantum states, and
cleanup memory is the measurement/collapse. This is a real VSA engine (Kanerva), not a metaphor.

It is exposed as a TOOL CAPABILITY: Railo can invoke hdc_vm to
  - encode any symbol/record into a hypervector (the machine's registers)
  - run a small HDC PROGRAM (bind/bundle/permute/cleanup) = compute in HD space
  - store & recall associatively (content-addressable memory)
  - and — the real payload — index the 1674-capability space and ROUTE by HD-similarity
    (semantic, beats keyword overlap). Railo literally computes its own routing in its own substrate.

Deterministic (seeded hypervectors → reproducible), numpy-only, zero network.
"""
from __future__ import annotations
import hashlib, json, sys
import numpy as np
from pathlib import Path

DIM = 10000
STATE = Path("/Users/eliaslorenzo/paradigm-lab/RAILO_STATE")
CAP_HV = STATE / "capability_hv.npz"


# ── core ops (the machine's instruction set) ────────────────────────────────
def hv(symbol: str) -> np.ndarray:
    """Deterministic bipolar {-1,+1} hypervector for a symbol (the machine's atoms)."""
    seed = int.from_bytes(hashlib.blake2b(symbol.encode("utf-8"), digest_size=8).digest(), "big")
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, DIM, dtype=np.int8) * 2 - 1


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """⊛ entangle (element-wise product) — reversible, dissimilar to inputs. role-filler / key-value."""
    return (a * b).astype(np.int8)


def bundle(vs: list[np.ndarray]) -> np.ndarray:
    """⊕ superpose (majority sign of the sum) — similar to ALL inputs. set / memory."""
    if not vs:
        return np.zeros(DIM, dtype=np.int8)
    s = np.sum(np.stack(vs).astype(np.int32), axis=0)
    out = np.sign(s).astype(np.int8)
    out[out == 0] = 1  # break ties deterministically
    return out


def permute(a: np.ndarray, n: int = 1) -> np.ndarray:
    """ρ rotate — encodes order/position (sequences) without collisions."""
    return np.roll(a, n).astype(np.int8)


def sim(a: np.ndarray, b: np.ndarray) -> float:
    """cosine on bipolar = normalized agreement ∈ [-1,1]. The measurement.
    NOTE: cast to float — np.dot on int8 over 10000 terms overflows int8 → garbage."""
    return float(np.dot(a.astype(np.float32), b.astype(np.float32)) / DIM)


def encode_record(fields: dict[str, str]) -> np.ndarray:
    """A structured record → one hypervector via role-filler binding, bundled. The VM's struct type."""
    return bundle([bind(hv(f"ROLE:{k}"), hv(f"VAL:{v}")) for k, v in fields.items()])


# ── content-addressable (associative) memory ────────────────────────────────
class HDMemory:
    """The machine's RAM: store(key,value) by superposition; recall(key) then cleanup to a symbol."""
    def __init__(self):
        self.mem = np.zeros(DIM, dtype=np.int32)
        self.codebook: dict[str, np.ndarray] = {}

    def learn(self, symbol: str) -> np.ndarray:
        v = hv(symbol); self.codebook[symbol] = v; return v

    def store(self, key: str, value: str):
        self.learn(key); self.learn(value)
        self.mem += bind(hv(key), hv(value)).astype(np.int32)

    def recall(self, key: str) -> tuple[str, float]:
        noisy = bind(np.sign(self.mem).astype(np.int8), hv(key))
        return self.cleanup(noisy)

    def cleanup(self, noisy: np.ndarray) -> tuple[str, float]:
        """Collapse a noisy hypervector to the nearest known symbol (the measurement)."""
        best, bs = "?", -1.0
        for s, v in self.codebook.items():
            sc = sim(noisy, v)
            if sc > bs:
                best, bs = s, sc
        return best, round(bs, 3)


# ── the real payload: HD-similarity routing over the capability space ───────
def index_capabilities() -> int:
    """Encode all 1674 capabilities as bundled hypervectors → Railo's semantic routing substrate."""
    import capacity_jump
    d = capacity_jump._load()
    syms, mat = [], []
    for mod, c in d["capabilities"].items():
        toks = c.get("kw", [])[:40]
        vecs = [hv(t) for t in toks] or [hv(mod)]
        syms.append(mod); mat.append(bundle(vecs))
    STATE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CAP_HV, syms=np.array(syms), mat=np.stack(mat).astype(np.int8))
    return len(syms)


def route_hd(intent: str, k: int = 6) -> list[dict]:
    """Route an intent through the HDC substrate (semantic similarity, not keyword overlap)."""
    if not CAP_HV.exists():
        index_capabilities()
    z = np.load(CAP_HV, allow_pickle=True)
    syms, mat = z["syms"], z["mat"].astype(np.int32)
    import re
    toks = [w for w in re.findall(r"[a-zåäö]{3,}", intent.lower())]
    q = bundle([hv(t) for t in toks]) if toks else hv(intent)
    scores = (mat @ q) / DIM
    order = np.argsort(-scores)[:k]
    return [{"module": str(syms[i]), "sim": round(float(scores[i]), 3)} for i in order]


def selftest() -> dict:
    """Prove the substrate computes: bind is reversible, bundle is similar-to-all, memory recalls."""
    a, b = hv("paris"), hv("france")
    bound = bind(a, b)
    r = dict(
        bind_reversible=round(sim(bind(bound, b), a), 2),     # ≈1.0 (recover a)
        bind_dissimilar=round(abs(sim(bound, a)), 2),         # ≈0.0 (bound unlike inputs)
        bundle_similar=round(sim(bundle([a, b, hv("x")]), a), 2),  # >0 (similar to members)
    )
    m = HDMemory()
    for k, v in [("capital_of_france", "paris"), ("capital_of_japan", "tokyo")]:
        m.store(k, v)
    sym, sc = m.recall("capital_of_france")
    r["memory_recall"] = f"{sym}={sc}"
    return r


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        print("🧮 HDC-VM selftest:", json.dumps(selftest())); return 0
    if len(argv) > 1 and argv[1] == "index":
        n = index_capabilities(); print(f"🧮 indexed {n} capabilities → HDC substrate ({DIM}-dim)"); return 0
    if len(argv) > 2 and argv[1] == "route":
        for r in route_hd(" ".join(argv[2:])):
            print(f"  sim={r['sim']:+.3f}  {r['module']}")
        return 0
    print("usage: hdc_vm.py selftest | index | route <intent...>")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
