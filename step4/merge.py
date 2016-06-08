"""merge.py
   Dec 26, 2015
   Merges simplified nominal records with other records from MW.
   ALL records of MW are retained. The 'lex' field is either that
   from allnom.txt or one of
    VERB:{category of verb, from verb_step0a.txt
    ICF:<substitute word>, from icf_prep1.txt
    SEE: <cf type="see"> from MW
    NEC: Not Elsewhere Classified -- Don't know what these are


"""
import codecs,re,sys
from collections import Counter


class Lexdata(object):
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.H,self.L,self.key1,self.key2,self.lex) = re.split('\t',line)
  self.used=False # for later use

def init_lexdata(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Lexdata(x) for x in f]
 print len(recs),"Lexdata records read from",filein
 d = {}
 for rec in recs:
  d[rec.L] = rec
 return d

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

class Mwrec(object):
 def __init__(self,line):
  line = line.rstrip('\r\n')
  (self.H,self.L,self.key1,self.key2,self.lex) = re.split('\t',line)

def init_mw(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs=[Mwrec(line) for line in f]

 print len(recs),"records from",filein
 return recs

class Verb(object):
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.key1,self.L,H,code,dummy,self.info) = re.split(':',line)
  self.key2 = self.key1
  self.H = re.sub(r'[<>H]','',H)  # H is like <H1>. Simplify to '1'
  self.lex= "VERB:%s" % code
  self.used=False # for later analysis

def init_verb(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Verb(x) for x in f]
 print len(recs),"records read from",filein
 d = {}
 for rec in recs:
  d[rec.L] = rec
 return d

class Icf(Lexdata):
 pass

def init_icf(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Icf(x) for x in f]
 print len(recs),"records read from",filein
 d = {}
 for rec in recs:
  d[rec.L] = rec
 return d

if __name__ == "__main__":
 filein1 = sys.argv[1] # mw.xml 
 filein2 = sys.argv[2] # allnom.txt
 filein3 = sys.argv[3] # auxiliary/verb_step0a.txt
 filein4 = sys.argv[4] # auxiliary/icf.txt
 fileout = sys.argv[5] # all.txt
 fout = codecs.open(fileout,"w","utf-8")
 mwrecs = init_mw(filein1) #

 dlex = init_lexdata(filein2) # dictionary of allnom.txt
 dverb = init_verb(filein3)
 dicf = init_icf(filein4)

 missing=Counter()
 #recs = [] # output records
 for mwrec in mwrecs:
  L = mwrec.L
  if L in dlex:
   rec = dlex[L]
   rec.used=True
  elif L in dverb:
   rec = dverb[L]
   rec.used=True
  elif L in dicf:
   rec = dicf[L]
   rec.used=True
  else:
   rec = mwrec
  outarr = [rec.H,rec.L,rec.key1,rec.key2,rec.lex]
  out = '\t'.join(outarr)
  fout.write("%s\n" % out)
 fout.close()
 # some usage messages  
 for L in dlex.keys():
  rec = dlex[L]
  if not rec.used:
   x = rec.line
   print filein2,"UNUSED:",x.encode('utf-8')

 filein3 = re.sub(r'auxiliary/','',filein3)
 for L in dverb.keys():
  rec = dverb[L]
  if not rec.used:
   x = rec.line
   print filein3,"UNUSED:",x.encode('utf-8')

 filein4 = re.sub(r'auxiliary/','',filein4)
 for L in dicf.keys():
  rec = dicf[L]
  if not rec.used:
   x = rec.line
   print filein4,"UNUSED:",x.encode('utf-8')

