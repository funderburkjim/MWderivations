Ref: https://github.com/funderburkjim/MWderivations/issues/15

Mwderivations/compounds/compounds.txt
Sample:
0003:aṃhri:+pa +skandha +śiras

Format:
3 colon-delimited fields
  1. Number of compounds
  2. headword
  3. words which are compounds of headword
     Some begin with '+' : These are simple 'joins' to headword
     Without beginning '+' : non-aimplw These are 'full words',
      not just the join
      
Examples
0003:aṃhri:+pa +skandha +śiras
0005:aṃhas:+pati aṃhasas-pati +patya aṃho-muc aṃho-liṅga
0001:akāraṇa:a-kāraṇo@tpanna
0002:paritark VERB:pari-tarkaṇa pari-tarkita
     verb or prefixed verb.  1247 of these.
     
Generate 
compounds_1.tsv
 tab-separated values
 3 fields:
 headword
 prefix (or ?)
 suffix (or ?)
Note: Exclude the headwords marked as VERB.

python compounds_1.py ../../compounds/compounds.txt compounds_1.tsv
12609 records from ../../compounds/compounds.txt
108415 records written to compounds_1.tsv


------------------------------------------------
# Some words occur as both prefix and suffix in compounds_1.tsv
# find all such words.
# Exclude cases where suffix = '?' in compounds_1.tsv 
python compounds_1_both.py compounds_1.tsv compounds_1_both.txt

108415 records from compounds_1.tsv
4588 records written to compounds_1_both.txt



