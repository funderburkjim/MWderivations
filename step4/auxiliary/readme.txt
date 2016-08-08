
verb-prep4-gati2-complete.out
  Private source: brownjf/app/preverb-sandhi/version10/
  7/10/2009
  Jim Funderburk, Peter Scharf
  Analysis of Preverbs in MW.
  6153 lines
  tab-separated fields:
  - L,key1,key2,root, prefix(es), standard form
    standard form = pfx[+pfx...]+root
deriv.txt
  Private source: ejf/pdfs/TM2013/0research/ejfcologne/lgtab1/mapnorm/whitney/
  1/15/2013
  Jim Funderburk
  Based on Scharf/Hyman digitization of Whitney roots
  703 lines
  3 tab-delimited fields:
  - Whitney root spelling
  - Corresponding MW root spelling (NOTE: L (or Ls) not specified)
  - Whitney verbal derivatives (space-separated list)

See step3/readme.org for icf.txt

participlies.txt is a concatenation of several files of participle
stems from the elispsanskrit repository in directory 
elispsanskrit/grammar/prod/outputs/.  The redo_participles.sh script
does the concatenation.

MW-verb-fap.txt
MW-verb-fmp.txt
MW-verb-fpp.txt
MW-verb-ipp.txt
MW-verb-ippa.txt
MW-verb-pap.txt
MW-verb-potp.txt
MW-verb-ppp.txt
MW-verb-prap.txt
MW-verb-prmp.txt
MW-verb-prpp.txt
MW-verb-rpp.txt


These are files with line-based records of the following structure:
:VERB Code ClassVoice:STEMS

where 
 - VERB is an root
 - Code is one of the codes above (fap,...,rpp)
 - ClassVoice is like 1a (class 1 verb, active (Parasmaipada) voice)
                      1m (class 1 verb, middle (Atmanepada) voice)
 - STEMS is one or more stems. This field may also have the formal detail
   of beginning and ending with parentheses.

There are 25890 lines in participles.txt at the time of this writing.
