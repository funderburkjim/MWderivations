# coding=utf-8
""" compounds_1_both.py
"""
from __future__ import print_function
import sys, re,codecs

class CompoundInstance(object):
 def __init__(self,line):
  self.headword,self.prefix,self.suffix = line.split('\t')
 
def init_compounds(filein):
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  recs = []
  for line in f:
   rec = CompoundInstance(line.rstrip('\r\n'))
   if rec.suffix != '?':
    recs.append(rec)
 print(len(recs),"records from",filein)
 return recs

def find_pfxsfxes(compounds):
 ans = []
 pfxes = set([x.prefix for x in compounds])
 #sfxes = set([x.suffix for x in compounds if x.suffix != '?'])
 sfxes = set([x.suffix for x in compounds])
 isect = pfxes.intersection(sfxes)
 if False: #dbg
  print('# pfxes = %s, # sfxes = %s' %(len(pfxes),len(sfxes)))
  w = 'vallikā'
  print('%s %s in pfxes' % ( w in pfxes,w))
  print('%s %s in sfxes' % ( w in sfxes,w))
  temp = [x for x in compounds if x.suffix == w]
  print('%s instances with suffix == %s' %(len(temp),w))
  for x in temp:
   print(x.headword,x.prefix,x.suffix)
 ans = list(isect)
 return ans

def write(fileout,pfxsfxes):
 with codecs.open(fileout,encoding='utf-8',mode='w') as f:
  for w in pfxsfxes:
   f.write(w + '\n')
 print(len(pfxsfxes),"records written to",fileout)

def find_counts(pfxsfxes,compounds):
 dpfx = {}
 dsfx = {}
 for w in pfxsfxes:
  dpfx[w] = 0
  dsfx[w] = 0
 for c in compounds:
  w = c.prefix
  if w in dpfx:
   dpfx[w] = dpfx[w] + 1
  w = c.suffix
  if w in dsfx:
   dsfx[w] = dsfx[w] + 1
 #
 ans = []
 for w in pfxsfxes:
  temp = (w,dpfx[w],dsfx[w])
  ans.append(temp)
 return ans

def write_counts(fileout,counts):
 with codecs.open(fileout,encoding='utf-8',mode='w') as f:
  for w,cpfx,csfx in counts:
   f.write('%s %s %s\n' % (w,cpfx,csfx))
 print(len(counts),"records written to",fileout)

if __name__=="__main__":
 filein = sys.argv[1] # 
 fileout = sys.argv[2] # 
 compounds = init_compounds(filein)
 pfxsfxes = find_pfxsfxes(compounds)
 #write(fileout,pfxsfxes)
 counts = find_counts(pfxsfxes,compounds)
 write_counts(fileout,counts)
