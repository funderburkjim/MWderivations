""" pfxderiv.py Feb 8, 2016
  combine information from deriv.txt and verb-prep4-gati2-complete.out
 python pfxderiv.py deriv.txt verb-prep4-gati2-complete.out pfxderiv.txt
"""
import codecs,re,sys
import sys
sys.path.append('../')
from scharfsandhi import ScharfSandhi


class Pfxverb(object):
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.L,self.key1,self.key2,self.root,self.prefixes,self.analysis) = re.split('\t',line)
  self.derivs=[] 

def init_pfxverb(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Pfxverb(x) for x in f]
 print len(recs),"records read from",filein
 return recs

class Deriv(object):
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.wkey,self.key1,derivstring) = re.split('\t',line)
  self.derivs = re.split(r' +',derivstring)

def pseudo_prefix_sandhi(prec,drec,deriv,sandhi):
 """
  Here's a case NOT properly handled.  deriv = savana for root su.
  aDi+savana is computed as aDizavana, but should be aDizavaRa  (n->R sanDi after 'z')
 """
 # first, alter the start of deriv if needed. This is the 'pseudo' part
 root = drec.key1
 key2parts = re.split('-+',prec.key2)
 pseudoroot = key2parts[-1] # last part
 if root.startswith('sT') and pseudoroot.startswith('zW') and deriv.startswith('sT'):
  deriv = 'zW' + deriv[2:]
 elif root.startswith('s') and pseudoroot.startswith('z') and deriv.startswith('s'):
  deriv = 'z' + deriv[1:]
 # now, do any other sandhi
 # probably, compound sandhi will be used. But this permits External sandhi
 # for experimental purposes.
 prefixes = prec.prefixes
 if sandhi.Compound:
  pfxderiv = sandhi.sandhi('%s-%s' % (prefixes,deriv))
 else:
  # change '-' to ' ' for external sandhi
  prefixes = re.sub('-',' ',prefixes)
  pfxderiv = sandhi.sandhi('%s %s' % (prefixes,deriv))
  # next required for external sandhi - there may still be spaces in result
  pfxderiv = re.sub(r' ','',pfxderiv)
 return pfxderiv

def init_deriv(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Deriv(x) for x in f]
 print len(recs),"records read from",filein
 return recs

if __name__ == "__main__":
 filein1  = sys.argv[1] # deriv.txt
 filein2 = sys.argv[2] # verb-prep4-gati2-complete.out
 fileout = sys.argv[3]
 drecs = init_deriv(filein1)
 precs = init_pfxverb(filein2)
 # derivdict has key = key1, and value the
 # list of records in drecs with key1
 derivdict = {} 
 for drec in drecs:
  key1 = drec.key1
  if key1 not in derivdict:
   derivdict[key1]=[]
  derivdict[key1].append(drec)
 # compute derivs field for each record of precs
 # use compound sandhi. This won't be quite right, but will be close
 # Compound sandhi gives wrong result in some important cases
 #  Example for viZWA = vi + sTA   , the 'sT' is not converted to 'zW'
 # Thus, we try external sandhi.
 # Wow! external sandhi has the same issue.  So the 'sT' to 'zW' change
 # must be due to some special prefix-combinator rule.
 sandhi = ScharfSandhi()
 sandhioption = 'C'
 sandhi.simple_sandhioptions(sandhioption) 

 for prec in precs:
  if prec.root not in derivdict:
   # nothing to do
   continue
  for drec in derivdict[prec.root]:
   for deriv in drec.derivs:
    #prec.prefixes as already '-' joined
    pfxderiv = pseudo_prefix_sandhi(prec,drec,deriv,sandhi)
    prec.derivs.append(pfxderiv)

 # write precs
 with codecs.open(fileout,"w","utf-8") as f:
  for prec in precs:
   pfxderivstring = ' '.join(prec.derivs)
   out = "%s\t%s\n" %(prec.line,pfxderivstring)
   f.write(out)
