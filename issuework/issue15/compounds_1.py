# coding=utf-8
""" compounds_1.py
"""
from __future__ import print_function
import sys, re,codecs

class Compound(object):
 def __init__(self,line):
  parts = line.split(':')
  self.count = int(parts[0])
  self.prefix = parts[1]
  self.data = parts[2].split(' ')
  
def init_compounds(filein):
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  recs = []
  for line in f:
   rec = Compound(line.rstrip('\r\n'))
   recs.append(rec)
 print(len(recs),"records from",filein)
 return recs

def compound_to_outrecs(compound):
 prefix = compound.prefix
 data = compound.data
 ans = []
 # exclude Verbs
 if prefix.endswith(' VERB'):
  return ans
 
 for d in data:
  if d.startswith('+'):
   suffix = d[1:]  # skip the leading plus
   headword = prefix + suffix
  else:
   # d is a headword. suffix unknown
   headword = d
   suffix = '?'
  rec = (headword,prefix,suffix)
  ans.append(rec)
 return ans

def init_outrecs(compounds):
 ans = []
 for c in compounds:
  arr = compound_to_outrecs(c)
  for x in arr:
   ans.append(x)
 return ans

def write(fileout,outrecs):
 with codecs.open(fileout,encoding='utf-8',mode='w') as f:
  for outrec in outrecs:
   # headword,prefix,suffix = outrec  # a tuple
   out = '\t'.join(outrec)
   f.write(out + '\n')
 print(len(outrecs),"records written to",fileout)
 
if __name__=="__main__":
 filein = sys.argv[1] # old.txt
 fileout = sys.argv[2] # changes.tsv
 compounds = init_compounds(filein)
 outrecs = init_outrecs(compounds)
 write(fileout,outrecs)
