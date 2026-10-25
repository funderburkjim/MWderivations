"""Attempt to separate genuine compound final members (uttarapada) from
derivational suffixes in the reverse index built by build_reverse_compound_index.py.

WHY this is needed: compounds.txt's right-hand tokens are NOT a homogeneous class.
The top of the frequency list is dominated by *taddhita* (secondary-derivation)
suffixes -- -tva, -tA, -vat, -mat, -maya, -tas -- which are bound morphemes and not
compound members at all. Reading the file as "what can stand on the right of a
samasa" therefore over-counts badly at the head of the distribution.

WHAT SIGNAL IS USED: a curated closed list of taddhita suffixes (Whitney,
Sanskrit Grammar, ch. XVII "Secondary derivation"; Macdonell, Vedic Grammar for
Students, ch. VII). Whitney's inventory is closed and small, which is exactly what
makes this tractable -- unlike the open class of nouns that can end a compound.

WHAT SIGNAL WAS TRIED AND REJECTED: "a real word also appears as a LEFT member,
a bound suffix cannot". Measured and refuted -- -tva, -vat, -mat, -maya, -tara,
-tama all DO appear as left members (each is homographic with an independent stem:
tva- pronominal, vat/mat as words, maya 'made of', tara 'crossing'), while a real
word like karman does NOT. Do not resurrect this heuristic; it is recorded here so
the next session does not re-derive the same dead end.

THE OTHER CORRECTION this script encodes: krt-derived stems (-kara, -kAra, -ja,
-gata, -stha, -dhara, -hara ...) are NOT suffixes in this context. They are genuine
final members of *upapada-tatpurusa* compounds -- rAja-kAra is a compound whose
second member is the stem kAra. They are flagged separately, not excluded.
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'compounds_reverse_uttarapada.tsv')
OUT = os.path.join(HERE, 'compounds_reverse_classified.tsv')

# --- Class 1: taddhita suffixes. Bound morphemes; NOT compound members. --------
# CANONICAL tier = the org's own vetted inventory, reused rather than re-derived:
# SanskritGrammar/scripts/sg_wf_004_taddhita.py SUFFIXES (Whitney ch. XVII
# SS 1136-1245), the list behind the published SG-WF-004 taddhita-overview article.
# Keep these two in sync; if SG's list changes, this one follows it, not the reverse.
TADDHITA_CANONICAL = {
    'tā', 'tva', 'maya', 'in', 'vat', 'mat', 'ika', 'īya', 'eya', 'ya',
    'aka', 'tara', 'tama', 'tas',
}

# EXTENDED tier = further Whitney/Macdonell secondary suffixes not in SG's 14
# (SG's list targets DCS-countable derivation; this file sees MW's whole markup).
# Kept as a SEPARATE tier so a reader can always tell a vetted call from an
# extrapolated one.
TADDHITA_EXTENDED = {
    'tāti', 'iman', 'vant', 'mant', 'vin', 'min', 'la', 'ala', 'ila', 'ula',
    'īyas', 'iṣṭha', 'tra', 'tha', 'thā', 'dā', 'dānīm', 'rhi', 'dhā', 'śas',
    'kṛtvas', 'sāt', 'eyaka', 'ka', 'ima', 'ina', 'na', 'tana', 'tya',
    'ra', 'ma', 'va', 'ava',
}

TADDHITA = TADDHITA_CANONICAL | TADDHITA_EXTENDED

# --- Class 2: krt-derived stems used as upapada final members. REAL members. ---
# Not exhaustive -- a flag, not a filter. Anything not listed still counts as a
# plain uttarapada, which is the conservative default.
KRT_STEMS = {
    'kara', 'kāra', 'kṛt', 'kṛta', 'ja', 'jā', 'gata', 'ga', 'stha', 'sthita',
    'dhara', 'dhārin', 'dhāra', 'hara', 'hārin', 'da', 'dā_stem', 'dāyin',
    'bhṛt', 'bhāj', 'bhū', 'bhūta', 'bhāva', 'kārin', 'gāmin', 'jña', 'jñā',
    'vid', 'vāha', 'vāhin', 'pa', 'pāla', 'pāyin', 'jit', 'jaya', 'kṣit',
    'cara', 'cārin', 'śāyin', 'sāda', 'grāhin', 'graha', 'kṛti', 'dṛś',
}


def classify(token):
    if token in TADDHITA and token in KRT_STEMS:
        return 'AMBIGUOUS'
    if token in TADDHITA_CANONICAL:
        return 'TADDHITA_SUFFIX'
    if token in TADDHITA_EXTENDED:
        return 'TADDHITA_SUFFIX_EXT'
    if token in KRT_STEMS:
        return 'KRT_STEM_MEMBER'
    return 'UTTARAPADA'


def main():
    rows = []
    with io.open(REV, encoding='utf-8') as fh:
        next(fh)
        for line in fh:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 3:
                continue
            token, n, lefts = parts[0], int(parts[1]), parts[2]
            rows.append((token, n, classify(token), lefts))

    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('uttarapada\tn_left_members\tclass\tleft_members\n')
        for token, n, cls, lefts in sorted(rows, key=lambda r: (-r[1], r[0])):
            fh.write(f'{token}\t{n}\t{cls}\t{lefts}\n')

    # --- report -------------------------------------------------------------
    from collections import Counter
    types = Counter(cls for _, _, cls, _ in rows)
    pairs = Counter()
    for _, n, cls, _ in rows:
        pairs[cls] += n
    total_types = sum(types.values())
    total_pairs = sum(pairs.values())

    print(f'{"class":<18}{"types":>8}{"types %":>10}{"pairs":>10}{"pairs %":>10}')
    for cls in ('UTTARAPADA', 'KRT_STEM_MEMBER', 'TADDHITA_SUFFIX',
                'TADDHITA_SUFFIX_EXT', 'AMBIGUOUS'):
        t, p = types[cls], pairs[cls]
        print(f'{cls:<18}{t:>8}{100*t/total_types:>9.1f}%{p:>10}{100*p/total_pairs:>9.1f}%')
    print(f'{"TOTAL":<18}{total_types:>8}{100:>9.1f}%{total_pairs:>10}{100:>9.1f}%')

    print('\nThe head of the distribution, reclassified (top 20 by left-member count):')
    for token, n, cls, _ in sorted(rows, key=lambda r: -r[1])[:20]:
        print(f'  {n:6d}  {token:<10} {cls}')

    print(f'\nwrote {OUT}')


if __name__ == '__main__':
    main()
