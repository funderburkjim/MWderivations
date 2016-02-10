"""analysis.py
   Dec 27, 2015
   Analyze the nominal elements of all.txt.
   ALL records of MW are retained. The 'lex' field is either that
   from allnom.txt or one of
    VERB:{category of verb, from verb_step0a.txt
    ICF:<substitute word>, from icf_prep1.txt
    SEE: <cf type="see"> from MW
    NONE: Not Elsewhere Classified -- Don't know what these are


"""
import codecs,re,sys
from collections import Counter
hwcpd_dict={} # module global

def unused_init_hwdict(hwrecs):
 """ ignore duplicates"""
 d = {}
 for hwrec in hwrecs:
  key = hwrec.key1
  if key not in d:
   d[key]=hwrec # keep first record with the given key1
 return d

def unused_analyze_samasa(rec,hwdict):
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


class Analysis(object):
 def __init__(self,line,option):
  line = line.rstrip('\r\n')
  self.line = line
  parts = re.split('\t',line)
  nparts=len(parts)
  if (option == 'init') and (nparts == 5):
   pass
  elif (option != 'init') and (nparts == 8):
   pass
  else:
   print "Analysis ERROR. %s and %s inconsistent" %(option,nparts)
   print "line=",line.encode('utf-8')
   exit(1)
  (self.H,self.L,self.key1,self.key2,self.lex) = parts[0:5]
  # use self.lex to get self.type (type of record)
  m = re.search(r'^(m|f|n|ind|LEXID|INFLECTID|LOAN|NONE|VERB|ICF|SEE)',self.lex)
  if not m:
   print "Analysis. UNEXPECTED lex:",self.lex.encode('utf-8')
   print "  line=",line.encode('utf-8')
   exit(1)
  code=m.group(1)
  if code in ('m','f','n','ind'):
   self.type='S' # normal Substantive or indeclineable 
  elif code in ('LEXID','INFLECTID','LOAN'):
   self.type='S1' # special substantive
  else:
   self.type=code
  if nparts == 5:  # form of all.txt
   self.analysis='' 
   self.note='init'
   if self.type in ('S','S1'):
    self.status = 'TODO'
   else:
    self.status = 'NTD' # Nothing To Do
  elif nparts == 8:
   (self.analysis,self.status,self.note) = parts[5:]
  else:
   print "Analysis, INTERNAL ERROR:",nparts
   print "Should be either 5 or 8 tab-delimited parts"
   print "line=",line.encode('utf-8')
   exit(1)
 def __repr__(self):
  parts=(self.H,self.L,self.key1,self.key2,self.lex,self.analysis,self.status,self.note) 
  return '\t'.join(parts)

def init_analysis(filein,option):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Analysis(x,option) for x in f]
 print len(recs),"records read from",filein
 return recs

def analysis_noparts(recs):
 for rec in recs:
  if rec.status != 'TODO':
   continue
  found = rec.lex.startswith('LOAN') or (not re.search(r'[~@-]',rec.key2))
  if found:
   (rec.analysis,rec.status,rec.note)=(rec.key2,'DONE','noparts')

class Whitney_sfx(object):
 d = {}
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.key,self.ref) = re.split(r' +',line)
  Whitney_sfx.d[self.key] = self.ref

def init_Whitney_sfx(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Whitney_sfx(x) for x in f if (not x.startswith(';'))]
 print len(recs),"records read from",filein
 return recs

def analysis_test(recs):
 # suffixes
 print "\nsuffixes\n"
 c=Counter()
 for rec in recs:
  if rec.status != 'TODO':
   continue
  m = re.search(r'-([^~@-]*)$',rec.key2)
  if not m:
   continue
  x = m.group(1) # ending pada
  #if len(x)>3: # exclude long ones
  # continue
  c[x]+=1
 for (x,n) in c.most_common(5):
  print "-%s"%x,n
 # prefixes
 print "\nprefixes\n"
 c=Counter()
 for rec in recs:
  if rec.status != 'TODO':
   continue
  m = re.search(r'^([^~@-]*)-',rec.key2)
  if not m:
   continue
  x = m.group(1) # ending pada
  #if len(x)>3: # exclude long ones
  # continue
  c[x]+=1
 for (x,n) in c.most_common(20):
  print "%s-"%x,n

def matchParent(firstpart,parentHkey):
 """ Jan 31, 2016. This is obscure"""
 if (firstpart == parentHkey):
  return True
 m = re.search(r'^(.*[ai])n$',parentHkey) 
 if m and (firstpart == m.group(1)):
  return True
 return False

def init_hwcpd_dict(recs):
 """ hwcpd_dict is a dictionary with 'key1' as key1
     Value is True if for some record (recs),
     the rec.type is other than ('VERB','SEE','NONE')
 """
 drec = {}
 # keys that may resolve parts of samasa
 n = 0
 for rec in recs:
  # may need to qualify
  if rec.type not in ('VERB','SEE','NONE'):
   drec[rec.key1]=True 
  #if True: # dbg
  # if rec.key1 == 'pratI':
  #  print "DBG: %s has type=%s,%s" %(rec.key1,rec.type,rec.L)
 return drec

def analysis_wsfx(recs):
 drec = hwcpd_dict
 wrecs = init_Whitney_sfx('auxiliary/wsfx.txt')
 parentHdata = [None,None,None,None]
 for rec in recs:
  parts = re.split(r'-',rec.key2)
  parentHkey=''
  if rec.H in ['1','2','3','4']:
   h = int(rec.H) -1 # 0,1,2,3
   if h != 0:
    parentHkey = parentHdata[h-1]
    if (parentHkey == None) and (h>=2):
     # where an H3 is under an H1
     parentHkey = parentHdata[h-2]
  else:
   h = -1
  lastpart=parts[-1]
  firstpart = ''.join(parts[0:-1])
  firstpart = re.sub(r'[~@-]','',firstpart)
  #if True and (rec.key1 == 'anAgAstva'):
  # print [rec.key1,rec.key2,firstpart,lastpart,"parent=%s"%parentHkey]
  # Jan 31, 2016 require that firstpart be a substantive
  if matchParent(firstpart,parentHkey) and (lastpart in Whitney_sfx.d) and (rec.status == 'TODO') and (parentHkey in drec):
   # success
   rec.analysis = "%s-%s" %(firstpart,lastpart)
   rec.status = 'DONE'
   ref = Whitney_sfx.d[lastpart]
   rec.note = 'wsfx:%s:%s' %(lastpart, ref)
  if h!= -1:
   parentHdata[h]=rec.key1
   for i in xrange(h+1,4):
    parentHdata[i] = None

def analysis_cpd1(recs):
 drec = hwcpd_dict
 parentHdata = [None,None,None,None]
 for rec in recs:
  parts = re.split(r'-',rec.key2)
  parentHkey=''
  if rec.H in ['1','2','3','4']:
   h = int(rec.H) -1 # 0,1,2,3
   if h != 0:
    parentHkey = parentHdata[h-1]
    if (parentHkey == None) and (h>=2):
     # where an H3 is under an H1
     parentHkey = parentHdata[h-2]
  else:
   h = -1
  nparts = len(parts)
  for ipart in xrange(1,nparts):
   firstpart = ''.join(parts[0:ipart])
   lastpart = ''.join(parts[ipart:])
   firstpart = re.sub(r'[~@-]','',firstpart)
   lastpart = re.sub(r'[~@-]','',lastpart)
   # Jan 31, 2016 require that firstpart be a substantive
   if parentHkey not in drec:
    continue
   if matchParent(firstpart,parentHkey) and (lastpart in drec) and (rec.status == 'TODO'):
    # success
    rec.analysis = "%s-%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    rec.note = 'cpd1'
    break # ipart loop
  if h!= -1:
   parentHdata[h]=rec.key1
   for i in xrange(h+1,4):
    parentHdata[i] = None

presandhi_hash = {} # dictionary
presandhi_hash["A"] = (("a","a"),("a","A"),("A","a"),("A","A"))
presandhi_hash["U"] = (("u","u"),("u","U"),("U","u"),("U","U"))
presandhi_hash["I"] = (("i","i"),("i","I"),("I","i"),("I","I"))
presandhi_hash["o"] = (("a","u"),("a","U"),("A","u"),("A","U"))
presandhi_hash["e"] = (("a","i"),("a","I"),("A","i"),("A","I"))
presandhi_hash["O"] = (("a","o"),("a","O"),("A","o"),("A","O"))
presandhi_hash["E"] = (("a","e"),("a","E"),("A","e"),("A","E"))

def analysis_srs1(recs):
 drec = hwcpd_dict
 parentHdata = [None,None,None,None]
 for rec in recs:
  parts = re.split(r'@',rec.key2)
  parentHkey=''
  if rec.H in ['1','2','3','4']:
   h = int(rec.H) -1 # 0,1,2,3
   if h != 0:
    parentHkey = parentHdata[h-1]
    if (parentHkey == None) and (h>=2):
     # where an H3 is under an H1
     parentHkey = parentHdata[h-2]
  else:
   h = -1
  if len(parts) == 1: # no @
   presandhi = []
  else:
   lastpart0=parts[-1]
   lastpart0 = re.sub(r'[~@-]','',lastpart0)
   firstpart = ''.join(parts[0:-1])
   firstpart = re.sub(r'[~@-]','',firstpart)
   firstpart0 = firstpart[0:-1] # all but last character, which is the sandhi
   try:
    c0 = firstpart[-1:] # last character
    presandhi = presandhi_hash[c0]
   except:
    presandhi=[]
    out = "%s" % rec
    print "srs1 exception:",out.encode('utf-8')
  srsparts=[]
  for (end,beg) in presandhi:
   if (rec.status != 'TODO'):
    continue
   firstpart = firstpart0+end
   lastpart = beg + lastpart0
   if firstpart != parentHkey:
    continue
   # Jan 31, 2016 require that firstpart be a substantive
   if parentHkey not in drec:
    continue
   if lastpart not in drec:
    continue
   srsparts.append((firstpart,lastpart))
  if len(srsparts) in (1,2):
   # success
   (firstpart,lastpart) = srsparts[0]
   rec.analysis = "%s+%s" %(firstpart,lastpart)
   rec.status = 'DONE'
   if len(srsparts) == 1:
    rec.note = 'srs1'
   else:
    lastpartalt = srsparts[1][1]
    #rec.note = 'srs1?:%s' % lastpartalt
    rec.note = 'srs1?'
  if h!= -1:
   parentHdata[h]=rec.key1
   for i in xrange(h+1,4):
    parentHdata[i] = None

known_prefixes = [
 'a', 'an',  'aBi', 'anu', 'ava', 'apa','aDi',
 'A',
 'upa', 'ut','ud',
 'ni','nir','aBy',
 'pari', 'pra', 'prati',
 'mahA'
 'vi','vy',
 'sam', 'saM', 'su', 'sa',
]
def analysis_pfx1(recs):
 drec = hwcpd_dict

 for rec in recs:
  if rec.status != 'TODO':
   continue
  parts = re.split(r'-',rec.key2)
  if len(parts)==1:
   continue
  firstpart=parts[0]
  lastpart = ''.join(parts[1:])
  lastpart = re.sub(r'[~@-]','',lastpart)
  if (firstpart in known_prefixes) and (lastpart in drec):
   # success
   rec.analysis = "%s-%s" % (firstpart,lastpart)
   rec.status = 'DONE'
   rec.note = 'pfx:%s' %(firstpart)

def analysis_testwsfx(recs):
 wrecs = init_Whitney_sfx('auxiliary/wsfx.txt')
 drec = hwcpd_dict

 for rec in recs:
  if rec.status != 'TODO':
   continue
  parts = re.split(r'-',rec.key2)
  if len(parts)==1:
   continue
  lastpart=parts[-1]
  firstpart = ''.join(parts[0:-1])
  firstpart = re.sub(r'[~@-]','',firstpart)
  if (firstpart in drec) and (lastpart in Whitney_sfx.d):
   # success
   rec.analysis = "%s-%s" %(firstpart,lastpart)
   rec.status = 'DONE'
   ref = Whitney_sfx.d[lastpart]
   rec.note = 'wsfx:%s:%s' %(lastpart, ref)

def gender_formP(b,a):
 """ is 'a' a feminine form of 'b'?
 """
 if b.endswith(('mat','vat','yat','in')) and (a == (b+'I')):
  return 'f'
 if b.endswith('in') and (a == (b[0:-1]+'RI')):
  return 'f'
 if b.endswith('a') and (a ==(b[0:-1]+'A')):
  return 'f'
 if b.endswith('a') and (a ==(b[0:-1]+'I')):
  return 'f' 
 if b.endswith('aka') and (a == (b[0:-3]+'ikA')):
  return 'f'
 if b.endswith('rAjan') and (a == (b[0:-2]+'YI')):
  return 'f'
 if b.endswith('am') and (a == (b[0:-2]+'A')):
  # example aBi-vAtA
  return 'f'
 if b == a:
  return 'same' # assume different gender in a (e.g. a is 'm', b is m:f:n')
 return None

def analysis_gender(recs):
 #wrecs = init_Whitney_sfx('auxiliary/wsfx.txt')
 #drec = hwcpd_dict

 for irec in xrange(0,len(recs)):
  rec=recs[irec]
  if rec.status != 'TODO':
   continue
  H = rec.H
  if H[-1]!='B':
   continue
  H0=H[0:1]
  irec0=irec-1
  while (irec0>=0):
   if recs[irec0].H == H0:
    break
   irec0=irec0-1
  if irec0<0:
   continue # won't happen, but safe programming
  rec0 = recs[irec0]
  g = gender_formP(rec0.key1,rec.key1)
  #if rec.key1 == 'atiSayanI':
  # print rec0.key1,rec.key1,g
  if (g == 'same') and (rec.lex[0] in ['m','f','n']):
   g = rec.lex[0]
  if g:
   # success
   rec.analysis = rec.key1
   rec.status = 'DONE'
   rec.note = 'gender:%s' % g

def analysis(recs,option):
 if option == 'noparts':
  analysis_noparts(recs)
 elif option == 'test':
  analysis_test(recs)
 elif option == 'testwsfx':
  analysis_testwsfx(recs)
 elif option == 'wsfx':
  analysis_wsfx(recs)
 elif option == 'cpd1':
  analysis_cpd1(recs)
 elif option == 'srs1':
  analysis_srs1(recs)
 elif option == 'pfx1':
  analysis_pfx1(recs)
 elif option == 'gender':
  analysis_gender(recs)
 else:
  print 'analysis ERROR. option not implemented',option
  exit(1)

if __name__ == "__main__":
 option = sys.argv[1]
 filein  = sys.argv[2] # either all.txt or a previous analysis of all.txt
 recs = init_analysis(filein,option)
 hwcpd_dict = init_hwcpd_dict(recs) 

 if option == 'init':
  fileout = sys.argv[3]
 elif len(sys.argv)==(3+1):
  fileout = sys.argv[3]
 else:
  fileout = filein # write output to same file name as input.
 if option != 'init':
  analysis(recs,option)
 if option.startswith('test'):
  print fileout,"not changed for option=",option
  exit(0)

 fout = codecs.open(fileout,"w","utf-8")
 for rec in recs:
  fout.write('%s\n' % rec) # use __repr__ to generate default form
 fout.close()
 # statistics
 # 1. status
 c = Counter()
 for rec in recs:
  x = "%4s %10s" %(rec.status,rec.note)
  c[x]+=1
 for x,n in c.iteritems():
  print "%6d %s" %(n,x)
