"""samasa.py
   Dec 25, 2015
   Identify key2 compounds (a-b-c) into known headwords.
   use  all.txt as source of headwords
"""
import codecs,re,sys;
from collections import Counter


class Lexdata(object):
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.L,self.key1,self.key2,self.lex) = re.split('\t',line)

def init_lexdata(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Lexdata(x) for x in f]
 print len(recs),"Lexdata records read from",filein
 return recs

def init_hwdict(hwrecs):
 """ ignore duplicates"""
 d = {}
 for hwrec in hwrecs:
  key = hwrec.key1
  if key not in d:
   d[key]=hwrec # keep first record with the given key1
 return d

def analyze_samasa(rec,hwdict):
 """ rec is a Lexdata object
  Change two parameters
 """
 padas = re.split(r"-",rec.key2)
 a = [] # analysis
 ok = True
 for pada in padas:
  if pada in hwdict:
   a.append(pada)
  else:
   a.append("?"+pada)
   ok = False
 rec.analyzed = '-'.join(a)
 if ok:
  rec.status = "OK"
 else:
  rec.status = "TODO"
 return
 

if __name__ == "__main__":
 filein1 = sys.argv[1] # samasa.txt
 filein2 = sys.argv[2] # all.txt, headword data
 fileout1 = sys.argv[3] # solved
 fout1 = codecs.open(fileout1,"w","utf-8")

 hwrecs = init_lexdata(filein2)
 hwdict = init_hwdict(hwrecs)
 recs = init_lexdata(filein1)

 n1 = 0 #of records written to file1
 n2 = 0
 missing=Counter()
 for rec in recs:
  analyze_samasa(rec,hwdict)
  out = rec.line + "\t"+ rec.analyzed + "\t" + rec.status 
  if rec.status == 'OK':
   n1 = n1 + 1
  else:
   n2 = n2 + 1
  fout1.write("%s\n" % out)

 fout1.close()
 print len(recs),"srs records processed from",filein1
 print n1,"samasa records solved "
 print n2,"samasa records unsolved"
