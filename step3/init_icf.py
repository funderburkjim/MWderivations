"""init_icf.py
   Dec 26, 2015
   Refine icf_prep1.txt
"""
import codecs,re,sys
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

def adjust_refkey(key1,refkey):
 refkey = re.sub(r'[-@]','',refkey)
 if not refkey.startswith('~'):
  return refkey
 x = refkey[1:] # all but the initial '~'
 # 1. key1=gaRi, refkey=~Rin => gaRin
 #    key1=grAva, refkey=~van => grAvan
 m = re.search(r'^(.*[ia])n$',x)
 if m:
  if key1.endswith(m.group(1)):
   refkey = key1+'n'
   return refkey
 # 2 key1=ceto, refkey=~tas => cetas
 m = re.search(r'^(.*)as$',x)
 if m:
  if key1.endswith(m.group(1)+'o'):
   refkey = key1[0:-1]+'as'
   return refkey
 # 3 key1 = jyotir, refkey=~tis => jyotis
 m = re.search(r'^(.*)s',x)
 if m:
  key1a = key1[0:-1]
  c = key1[-1:] # last character
  if key1a.endswith(m.group(1)) and (c in ['H','r','S','z']):
   refkey = key1a + 's'
   return refkey
 # 3a catuz, ~tur => catur
 m = re.search(r'^(.*)r',x)
 if m:
  key1a = key1[0:-1]
  c = key1[-1:] # last character
  if key1a.endswith(m.group(1)) and (c in ['H','s','S','z']):
   refkey = key1a + 'r'
   return refkey
 # 4 key1=jagad, refkey=~gat => jagat
 m = re.search(r'^(.*[aAi])t',x)
 if m:
  key1a = key1[0:-1]
  c = key1[-1:] # last character
  if key1a.endswith(m.group(1)): # and (c in ['H','r','S','z']):
   refkey = key1a + 't'
   return refkey
 # 5 suraBy, ~Bi => suraBi
 m = re.search(r'^(.*)i',x)
 if m:
  key1a = key1[0:-1]
  c = key1[-1:] # last character
  if key1a.endswith(m.group(1))and (c in ['y']):
   refkey = key1a + 'i'
   return refkey
 # 5a jAnv,~nu => jAnu
 m = re.search(r'^(.*)u',x)
 if m:
  key1a = key1[0:-1]
  c = key1[-1:] # last character
  if key1a.endswith(m.group(1))and (c in ['v']):
   refkey = key1a + 'u'
   return refkey
 # 6 pfTag, ~Tak => pfTak
 m = re.search(r'^(.*)k',x)
 if m:
  key1a = key1[0:-1]
  c = key1[-1:] # last character
  if key1a.endswith(m.group(1)) and (c in ['g','N']):
   refkey = key1a + 'k'
   return refkey
 # 7 vizvak, ~vaYc => vizvaYc
 m = re.search(r'^(.*[aA])Yc$',x)
 if m:
  key1a = key1[0:-1]
  c = key1[-1:] # last character
  if key1a.endswith(m.group(1)): #and (c in ['v']):
   refkey = key1a + 'Yc'
   return refkey
 # 8 praguRI,~guRa => praguRa .  This case probably could be used for
 #   several of the above specialized cases
 m = re.search(r'^(.*)(.)$',x)
 if m: # always holds
  key1a=key1[0:-1]
  if key1a.endswith(m.group(1)):
   refkey = key1a + m.group(2)
   return refkey
 # 9 paya,~yas => payas
 m = re.search(r'^(.*)(.)$',x)
 if m: # always holds
  key1a=key1
  if key1a.endswith(m.group(1)):
   refkey = key1a + m.group(2)
   return refkey

 # 10 cakzU, ~kzus => cakzus
 m = re.search(r'^(.*)(..)$',x)
 if m: # always holds
  key1a=key1[0:-1]
  if key1a.endswith(m.group(1)):
   refkey = key1a + m.group(2)
   return refkey
 # 11 one case
 if key1 == 'hanumanta':
  refkey = 'hanumat'
  return refkey

 return refkey

class Icf(object):
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.L,H,self.key1,key2,icf,info) = re.split('\t',line)
  self.key2=adjust_key2(key2)
  self.H = re.sub(r'[H]','',H)  # H is like 'H2'. Simplify to '1'
  m = re.search(r'OK (.*?)$',info)
  refkey0 = m.group(1)
  refkey = adjust_key2(refkey0)
  # additional adjustment
  refkey = adjust_refkey(self.key1,refkey)
  if not re.search(r'~?[a-zA-Z-]+$',refkey):
   print "ICF: WARNING (%s), line=%s" %(refkey0,line)
  self.code = "ICF:%s" % refkey

def init_icf(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Icf(x) for x in f if re.search('\tOK ',x)]
 print len(recs),"records read from",filein
 return recs

if __name__ == "__main__":
 filein = sys.argv[1] # icf_prep1.txt
 fileout = sys.argv[2] # icf.txt
 icfrecs = init_icf(filein)
 fout = codecs.open(fileout,"w","utf-8")
 for rec in icfrecs:
  outar=(rec.H,rec.L,rec.key1,rec.key2,rec.code)
  out = '\t'.join(outar)
  fout.write('%s\n' % out)
 fout.close()

