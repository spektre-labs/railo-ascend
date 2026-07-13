# railo-ascend ⟐ a knowledge organism that grows, and only ever grows truth

Three ideas fused into one standing system:

1. **Discover** — propose candidate facts (structured SMT conjectures).
2. **Re-verify** — independently re-derive each with z3 (generator ≠ verifier). σ>0 → rejected.
3. **Learn** — admit only the re-verified into a **persistent, monotonic, truth-only** store, rebuildable
   one-shot into a holographic model ([railo-hdc](https://github.com/spektre-labs/railo-hdc)).

The result is a knowledge base that **cannot contain a falsehood** and **grows on every heartbeat** —
the opposite of a frozen model trained on unverified text.

```bash
pip install z3-solver numpy
python3 ascend_daemon.py beat        # one heartbeat — discover, re-verify, admit, persist
python3 ascend_daemon.py status      # how much verified truth it holds
python3 ascend_daemon.py query "square modulo 4"
python3 verified_learning_loop.py    # the loop + a poison test (4/4 false claims rejected at the gate)
```

`verified_knowledge.jsonl` is the standing store — every line an independently re-derived truth (σ=0),
each with its witness. Delete it and the organism regrows it from first principles; it never regresses.

## Why this clears the bar

- **Truth gate on learning.** Legacy ML ingests unverified web text and freezes. This ingests only what a
  second, independent kernel re-proves — and it can prove it to you: every entry carries a re-runnable
  witness. Composes with [railo-verify](https://github.com/spektre-labs/railo-verify)'s live edge, where
  anyone re-derives any claim over any channel.
- **One-shot, no gradient.** New truth enters by a single holographic bind+bundle — instant, transparent.
- **Monotonic and honest.** Growth only; falsehoods admitted: 0, by construction, demonstrated (poison test).

*σ = declared − realized. The organism holds only the facts where σ = 0.*
