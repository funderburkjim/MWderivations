"""mw_extract.py
   Retrieve data from MW
"""
import codecs,re,sys

class Mwrec(object):
 def __init__(self,H,L,key1,key2,code):
  (self.H,self.L,self.key1,self.key2,self.lex) = (H,L,key1,key2,code)
  # key2 and code may be adjusted by later processing

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
 recs=[] # list of records to return
 f = codecs.open(filein,"r","utf-8")
 n = 0
 nin=0
 prevkey1='' # previous key1 for an H1, H2, H3, H4
 nmiss=0
 for x in f:
  nin=nin+1
  m = re.search(r'^<H([^>]*?)>.*?<key1>(.*?)</key1>.*?<key2>(.*?)</key2>.*?<L[^>]*?>(.*?)</L>',x)
  if not m:
   nmiss=nmiss+1
   print "MW SKIP:",x.encode('utf-8')
   if nmiss>10:
    print "MW skipping too many. ERROR"
    exit(1)
   continue
  H = m.group(1)
  # ignore H.A cases
  if H.endswith('A'):
   continue
  if re.search('<lex type="inh">',x):
   continue # skip these inherited, even if not "<HxA"
  key1 = m.group(2)
  if H.endswith('B') and (key1 == prevkey1): # ignore these
   #continue
   # Feb 9, 2016. Modified to keep these.  
   # This was to deal with cases like
   #   29882	ISvara	ISvara/	m:f#I
   # where there is new lex information (f#I), even though the key (ISvara) is same
   pass
  if H in ['1','2','3','4']:
   prevkey1 = key1
  key2 = m.group(3)
  key2 = adjust_key2(key2)
  L = m.group(4)
  # 14198.20 => 14198.2, etc.
  L = re.sub(r'[.]([0-9])0',r'.\1',L) # remove trailing '0'.
  n=n+1
  if re.search(r'<see type="nonhier"/>',x):
   code='SEE'
  else:
   code="NONE"
  rec = Mwrec(H,L,key1,key2,code)
  recs.append(rec)
 f.close()
 print nin,"records read from",filein
 return recs

if __name__ == "__main__":
 filein = sys.argv[1] # mw.xml 
 fileout = sys.argv[2] # all.txt
 fout = codecs.open(fileout,"w","utf-8")
 mwrecs = init_mw(filein)
 for rec in mwrecs:
  outar=(rec.H,rec.L,rec.key1,rec.key2,rec.lex)
  out = '\t'.join(outar)
  fout.write('%s\n' % out)
 fout.close()
 print len(mwrecs),"records written to",fileout
