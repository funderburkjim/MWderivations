"""normkey2.py
   Dec 26, 2015
   Variant of step1/process1b1.php.
   - simplify raw key2
   - access corresponding 'H' code from mw.xml
   - Leave the '~' (<sr/>) codes in key2, but replace '-~' and '~-' by '~'

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
 
def adjust_key2(x):
 x = re.sub(r'-+','-',x)
 x = re.sub(r'<sr1?/>','~',x) # <sr/>, <sr1/>
 x = re.sub(r'<srs1?/>','@',x) # <srs/>, <srs1/>
 x = re.sub(r'<shortlong/>','',x)
 x = re.sub(r'</?root>','',x) # <root>, </root>
 x = re.sub(r'[/\^]','',x) # accents
 #x = re.sub(r'~','',x)  # remove entirely. This is done for step1/all.txt
 x = re.sub(r'-?~-?','~',x)  # leave ~, but remove neighboring '-'
 return x

def init_mw(filein):
 d = {} # dictionary to return
 f = codecs.open(filein,"r","utf-8")
 n = 0
 for x in f:
  m = re.search(r'^<H(.*?)>.*<L[^>]*?>(.*?)</L>',x)
  if not m:
   continue
  H = m.group(1)
  L = m.group(2)
  # 14198.20 => 14198.2, etc.
  L = re.sub(r'[.]([0-9])0',r'.\1',L) # remove trailing '0'.
  d[L]=H
  n=n+1
 f.close()
 print n,"records from",filein
 return d

if __name__ == "__main__":
 filein1 = sys.argv[1] # mw.xml 
 filein2 = sys.argv[2] # lexnorm-all.txt, from Mwlexnorm/step1b
 fileout = sys.argv[3] # 
 fout = codecs.open(fileout,"w","utf-8")

 recs = init_lexdata(filein2)
 mwdict = init_mw(filein1) # mwdict[L] = H-code, without leading 'H'
 #recs = init_lexdata(filein1)

 missing=Counter()
 for rec in recs:
  key2adj = adjust_key2(rec.key2)
  if rec.L in mwdict:
   H = mwdict[rec.L]
  else:
   H = '?'
   print "L not found in mw:",rec.L,rec.key1
  outarr = [H,rec.L,rec.key1,key2adj,rec.lex]
  out = '\t'.join(outarr)
  fout.write("%s\n" % out)
  
 fout.close()
 print len(recs),"records processed from",filein2
