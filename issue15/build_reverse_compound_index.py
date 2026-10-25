"""Invert MWderivations compounds.txt into an uttarapada-keyed (right-member) index.

Forward source (funderburkjim, MWderivations/compounds/compounds.txt):
    <count>:<purvapada>:<space-separated uttarapada tokens>
where a token '+X' means the headword is the plain concatenation purvapada+X,
and any other token is a non-simple form (carries '-' or '@') whose suffix
funderburkjim's issue-15 analysis marks '?'.

This script answers MWderivations#15's second half — "what words are there in
left and right, and what can be on both sides" — from the local clone, without
needing his issuework/ directory.
"""
import sys
import io
import os
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "compounds", "compounds.txt")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

reverse = defaultdict(list)      # uttarapada -> [purvapada, ...]  (simple only)
forward_count = defaultdict(int)  # purvapada -> n simple compounds
nonsimple = 0
simple = 0
lines = 0

with io.open(SRC, encoding='utf-8') as fh:
    for line in fh:
        line = line.rstrip('\n')
        if not line:
            continue
        parts = line.split(':', 2)
        if len(parts) < 3:
            continue
        lines += 1
        _count, prefix, rest = parts
        for tok in rest.split():
            if tok.startswith('+'):
                suffix = tok[1:]
                if not suffix:
                    continue
                reverse[suffix].append(prefix)
                forward_count[prefix] += 1
                simple += 1
            else:
                nonsimple += 1

print(f"source lines parsed      : {lines}")
print(f"simple (+suffix) entries : {simple}")
print(f"non-simple entries       : {nonsimple}")
print(f"distinct uttarapadas     : {len(reverse)}")
print(f"distinct purvapadas      : {len(forward_count)}")

# --- both-sides set: word used as left member AND as right member -------------
left = set(forward_count)
right = set(reverse)
both = sorted(left & right)
print(f"words on BOTH sides      : {len(both)}")

# --- write the reverse index (TSV) -------------------------------------------
rev_path = os.path.join(OUT_DIR, "compounds_reverse_uttarapada.tsv")
with io.open(rev_path, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write("uttarapada\tn_left_members\tleft_members\n")
    for suffix in sorted(reverse, key=lambda k: (-len(reverse[k]), k)):
        lefts = sorted(set(reverse[suffix]))
        fh.write(f"{suffix}\t{len(lefts)}\t{' '.join(lefts)}\n")

both_path = os.path.join(OUT_DIR, "compounds_both_sides.tsv")
with io.open(both_path, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write("word\tas_left\tas_right\n")
    for w in sorted(both, key=lambda k: -(forward_count[k] + len(set(reverse[k])))):
        fh.write(f"{w}\t{forward_count[w]}\t{len(set(reverse[w]))}\n")

# --- top uttarapadas ----------------------------------------------------------
top = sorted(reverse.items(), key=lambda kv: -len(set(kv[1])))[:25]
print("\nTop 25 uttarapadas by distinct left members:")
for suffix, lefts in top:
    print(f"  {len(set(lefts)):6d}  {suffix}")

# --- the issue's own example --------------------------------------------------
for probe in ('pāla', 'kāra', 'ja', 'gata'):
    lefts = sorted(set(reverse.get(probe, [])))
    print(f"\n{probe}: {len(lefts)} left members; sample: {' '.join(lefts[:12])}")

print(f"\nwrote {rev_path}")
print(f"wrote {both_path}")
