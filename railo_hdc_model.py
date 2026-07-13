#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""railo_hdc_model.py — system = model. The whole Railo substrate encoded as ONE holographic hyperdimensional
model. Not a transformer: no weights, no gradients, no training loop. The model IS the encoded system.

Three feats a transformer structurally cannot do, all on a CPU in milliseconds:
  1. HOLOGRAPHIC CAPACITY — the entire knowledge base superposed into ONE 10 000-dim vector; probe it with
     any concept and that concept surfaces above noise. The system fits in one register.
  2. ONE-SHOT LEARNING — add a new fact by a single bind+bundle. No retraining, no gradient, instant.
  3. ALGEBRAIC ANALOGY — A:B :: C:? solved by vector arithmetic (bind is self-inverse), not by attention.

Wires runtime/hdc_vm.py (the VSA engine). numpy-only, zero network, deterministic.
"""
import json, re, sys, pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import hdc_vm as H   # the engine: hv, bind, bundle, permute, sim, DIM
H.DIM = 65536        # lift the dimension → lower noise floor → sharp recall/analogy over the whole substrate

WORD = re.compile(r"[a-zA-Z_]{3,}")


def text_hv(text: str) -> np.ndarray:
    """A holographic semantic vector for free text = superposition of its word atoms."""
    ws = WORD.findall(text.lower())[:40]
    return H.bundle([H.hv(w) for w in ws]) if ws else H.hv("∅")


class RailoHD:
    def __init__(self):
        self.items = {}          # id -> (text, hv)      ← the model (content-addressed knowledge)
        self.system = None       # ONE vector = the whole substrate superposed (holographic)

    def ingest(self, id: str, text: str):
        self.items[id] = (text, text_hv(text))

    def seal(self):
        self.system = H.bundle([hv for _, hv in self.items.values()])   # system = model, in one register
        return len(self.items)

    # FEAT 2 — one-shot learning: instant, no gradient
    def learn(self, id: str, text: str):
        self.ingest(id, text)
        v = self.items[id][1]
        self.system = v if self.system is None else H.bundle([self.system, v])
        return {"learned": id, "in": "one shot — no training", "system_now_contains": len(self.items)}

    # holographic query: recall by HD similarity (compositional, robust)
    def query(self, q: str, k: int = 3):
        qv = text_hv(q)
        scored = sorted(((H.sim(qv, hv), id, txt) for id, (txt, hv) in self.items.items()), reverse=True)
        return [{"id": id, "sim": round(s, 3), "text": txt[:90]} for s, id, txt in scored[:k]]

    # FEAT 1 — the whole system is in ONE vector: probe it, the fact surfaces above noise
    def in_system(self, id: str):
        _, hv = self.items[id]
        signal = H.sim(self.system, hv)
        noise = H.sim(self.system, H.hv("UNRELATED_RANDOM_PROBE_xyz"))
        return {"id": id, "signal": round(signal, 3), "noise_floor": round(noise, 3),
                "recovered_from_one_vector": signal > 4 * abs(noise) + 0.02}

    # FEAT 3 — structured analogy (Kanerva's "dollar of Mexico"): works because the RELATION is shared
    # structure across records, recovered by unbinding. Real vector arithmetic, no attention, no training.
    def analogy_record(self, rec_from: dict, rec_to: dict, role: str):
        A = H.encode_record(rec_from)          # e.g. {compute:"gpu", access:"rent", surface:"pod"}
        B = H.encode_record(rec_to)            # e.g. {compute:"gpu", access:"browser", surface:"webgpu"}
        want = H.hv(f"VAL:{rec_from[role]}")   # the filler in A we want the analogue of in B
        # transport: bind the wanted filler through A→B, then unbind the role → B's filler for that role
        transported = H.bind(H.bind(want, A), B)
        recovered = H.bind(transported, H.hv(f"ROLE:{role}"))
        cands = list({v for r in (rec_from, rec_to) for v in r.values()})
        scored = sorted(((H.sim(recovered, H.hv(f"VAL:{x}")), x) for x in cands), reverse=True)
        return {"question": f"the '{role}' of the second record (analogue of '{rec_from[role]}')",
                "answer": scored[0][1], "ranked": [(x, round(s, 3)) for s, x in scored[:4]]}


def build() -> RailoHD:
    m = RailoHD()
    STATE = ROOT / "RAILO_STATE"
    # verified facts — from the live substrate if present, else the bundled public sample (standalone clone)
    led = STATE / "VERIFIED_DISCOVERIES.jsonl"
    if not led.exists():
        led = pathlib.Path(__file__).with_name("sample_facts.jsonl")
    if led.exists():
        for i, l in enumerate(led.read_text().splitlines()):
            try: r = json.loads(l)
            except Exception: continue
            m.ingest(f"fact:{r.get('domain','?')}:{i}", f"{r.get('domain','')} {r.get('artifact','')}")
    # organs (the architecture)
    for f in sorted((ROOT / "runtime").glob("*.py")):
        mt = re.search(r'"""(.+?)"""', f.read_text()[:800], re.S)
        if mt: m.ingest(f"organ:{f.stem}", f"{f.stem} {mt.group(1).strip()[:200]}")
    # paradigms
    MEM = ROOT.parent / ".claude/projects/-Users-eliaslorenzo-paradigm-lab/memory"
    if MEM.exists():
        for f in MEM.glob("*.md"):
            if f.name != "MEMORY.md":
                dm = re.search(r"description:\s*(.+)", f.read_text())
                if dm: m.ingest(f"paradigm:{f.stem}", f"{f.stem} {dm.group(1)}")
    m.seal()
    return m


if __name__ == "__main__":
    m = build()
    print(f"system = model · {len(m.items)} knowledge items encoded into a single {H.DIM}-dim holographic register\n")
    print("FEAT 1 — holographic capacity (whole system in ONE vector, probe recovers the fact):")
    for id in list(m.items)[:1] + [x for x in m.items if x.startswith("paradigm")][:2]:
        print("  ", m.in_system(id))
    print("\nFEAT 2 — one-shot learning (instant, no gradient):")
    print("  ", m.learn("paradigm:hypervector-jump", "system equals model, encoded holographically in hyperdimensional space, one-shot, no transformer"))
    print("   query('encode the system without training') →")
    for r in m.query("encode the system without training", 3): print("     ", r)
    print("\nFEAT 3 — structured analogy by vector algebra (no attention, no training):")
    print("   'rent is to pod as browser is to ___' (the surface of self-owned compute):")
    print("  ", m.analogy_record({"compute": "gpu", "access": "rent", "surface": "pod"},
                                 {"compute": "gpu", "access": "browser", "surface": "webgpu"}, "surface"))
