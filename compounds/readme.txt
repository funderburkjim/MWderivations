
ARCHIVED (H7243, 24-10-2026): compounds.py is a Python 2 research script and
does not run under Python 3 (xrange; copy/Counter never imported; partition and
ScharfSandhi live in step3/ and step4/, not on this import path). It is kept for
provenance only and was deliberately NOT ported — see the header in compounds.py.
The maintained artifact is the generated compounds.txt, which
issue15/build_reverse_compound_index.py reads.

compounds :  Gather compounds from step4/all.txt
This is similar to step2/analysis.txt, but somewhat simplified.
We use step4/all.txt as input.

python compounds.py txt ../step4/all.txt compounds.txt
#python compounds.py md ../step4/all.txt compounds.md

python compounds.py html ../step4/all.txt compounds.html

