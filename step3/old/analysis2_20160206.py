"""analysis2.py
   Dec 27, 2015
   Analyze the nominal elements of all.txt.
   ALL records of MW are retained. The 'lex' field is either that
   from allnom.txt or one of
    VERB:{category of verb, from verb_step0a.txt
    ICF:<substitute word>, from icf_prep1.txt
    SEE: <cf type="see"> from MW
    NONE: Not Elsewhere Classified -- Don't know what these are
   Feb 1, 2016.  Refactor so that parentRrec is a 'parent' attribute in rec.
   Feb 3, 2016.  Refactor again, so more subtle derivations possible.
"""
import codecs,re,sys
from collections import Counter
hwcpd_dict={} # module global

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
  self.parent = None  # determined by init_parents. 
  self.parenta = None # determined by init_parentsa.

 def __repr__(self):
  if self.status == 'TODO':
   if self.parent:
    self.note = '%s:parent=%s'%(self.note,self.parent.key1)
  parts=(self.H,self.L,self.key1,self.key2,self.lex,self.analysis,self.status,self.note) 
  return '\t'.join(parts)

 def substantiveP(self):
  #return self.type not in ('VERB','SEE','NONE')
  return self.type not in ('VERB','SEE')

 
def init_analysis(filein,option):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Analysis(x,option) for x in f]
 print len(recs),"records read from",filein
 return recs

def init_parents(recs):
 """ establish the 'parent' record for reach rec. This
     parent may be None.  The parent is determined by
     the ordering of the records, and also uses the H-code of the records.
 """
 parentHdata = [None,None,None,None]
 for rec in recs:
  parentRec=None
  if rec.H in ['1','2','3','4']:
   h = int(rec.H) -1 # 0,1,2,3
   if h != 0:
    parentRec = parentHdata[h-1]
    if (parentRec == None) and (h>=2):
     # where an H3 is under an H1
     parentRec = parentHdata[h-2]
  else:
   h = -1
  rec.parent = parentRec
  if h!= -1:
   parentHdata[h]=rec
   for i in xrange(h+1,4):
    parentHdata[i] = None

def init_parentsa(recs):
 """ establish the 'parent' record for reach rec. This
     parent may be None.  If rec.H is x[ABC], then this
     parent is the previous rec0 with rec0.H==x
 """
 for irec in xrange(0,len(recs)):
  rec=recs[irec]
  #if rec.status != 'TODO':
  # continue
  H = rec.H
  m = re.search(r'^([1-4])([ABC])$',H)
  if not m:
   continue
  H0=m.group(1)
  irec0=irec-1
  while (irec0>=0):
   if recs[irec0].H == H0:
    break
   irec0=irec0-1
  if irec0<0:
   continue # won't happen, but safe programming
  rec.parenta=recs[irec0]

def analysis2_noparts(rec):
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

def init_hwcpd_dict(recs):
 """ hwcpd_dict is a dictionary with 'key1' as key1
     Value is True if for some record (recs),
     the rec.type is other than ('VERB','SEE','NONE')
 """
 drec = {}
 # keys that may resolve parts of samasa
 n = 0
 for rec in recs:
  if rec.substantiveP():
   drec[rec.key1]=True 
 return drec

def analysis2_wsfx(rec,wrecs):
  drec = hwcpd_dict
  parts = re.split(r'-',rec.key2)
  parentRec=rec.parent
  if parentRec == None:
   return
  lastpart=parts[-1]
  firstpart = ''.join(parts[0:-1]
  firstpart = re.sub(r'[~@-]','',firstpart)
  #if True and (rec.key1 == 'anAgAstva'):
  # print [rec.key1,rec.key2,firstpart,lastpart,"parent=%s"%parentRec]
  # Jan 31, 2016 require that firstpart be a substantive
  if(firstpart==parentRec.key1) and (lastpart in Whitney_sfx.d) and (rec.status == 'TODO') and (parentRec.substantiveP()):
   # success
   rec.analysis = "%s-%s" %(firstpart,lastpart)
   rec.status = 'DONE'
   ref = Whitney_sfx.d[lastpart]
   rec.note = 'wsfx:%s:%s' %(lastpart, ref)

vowels = 'aAiIuUfFxXeEoO'
soft_consonants = 'gGNjJYqQRdDnbBmyrlv'
hard_consonants = 'kKcCwWtTpPs' # sibilants too?

def compound_pairP(parent,x,y):
 """ 
 """
 # sandhi cases
 if parent.endswith('i') and x.endswith('y') and (y[0:1] in vowels) and (parent[0:-1]==x[0:-1]):
  return True
 if parent.endswith('u') and x.endswith('v') and (y[0:1] in vowels) and (parent[0:-1]==x[0:-1]):
  return True
 if parent.endswith('as') and x.endswith('o') and (y[0:1] in soft_consonants) and (parent[0:-2]==x[0:-1]):
  return True
 if parent.endswith('as') and x.endswith('aH') and (y[0:1] in hard_consonants) and (parent[0:-2]==x[0:-2]):
  return True
 # other special cases
 # For nouns ending in 'in' or 'an', the compound form drops the 'n'
 m = re.search(r'^(.*[ai])n$',parent) 
 if m and ( m.group(1) == x):
  return True
 return False

def analysis2_cpd_nan(rec):
  """ nan-tatpurusha """
  drec = hwcpd_dict
  if rec.H not in ['1','2']:
   # only do this analysis for H1 or H2 case
   return
  parts = re.split(r'-',rec.key2)
  for ipart in [1]:
   firstpart = ''.join(parts[0:ipart])
   if firstpart not in ['a','an']:
    continue
   lastpart = ''.join(parts[ipart:])
   #firstpart = re.sub(r'[~@-]','',firstpart)
   lastpart = re.sub(r'[~@-]','',lastpart)
   if lastpart in drec:
    # success
    rec.analysis = "%s-%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    rec.note = 'cpd_nan'
    return # ipart loop
   lastparta = [x for x in adjective_stems(lastpart) if x in drec]
   if len(lastparta)>0:
    # success
    rec.analysis = "%s-%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    stems = ','.join(lastparta)
    rec.note = 'cpd1:%s<-%s'%(lastpart,stems)
    return 

def analysis2_cpd3(rec):
  drec = hwcpd_dict
  parentRec=rec.parent
  if (not parentRec) or (not parentRec.substantiveP()):
   return
  parts = re.split(r'-',rec.key2)
  nparts = len(parts)
  parentKey = parentRec.key1
  for ipart in xrange(1,nparts):
   firstpart = ''.join(parts[0:ipart])   
   firstpart = re.sub(r'[~@-]','',firstpart)
   if (firstpart != parentKey):
    continue
   # are all of the remaining parts compound components?
   lastparts = parts[ipart:]
   ok = True
   okparts=[]
   for p in lastparts:
    p = re.sub(r'[~@-]','',p)
    if p not in drec:
     # fails
     ok = False
     break
    else:
     okparts.append(p)
   if ok:
    # success
    rec.analysis = "%s-%s" %(parentKey,'-'.join(okparts))
    rec.status = 'DONE'
    rec.note = 'cpd3'
    break # ipart loop

def analysis2_cpd1(rec):
  drec = hwcpd_dict
  parentRec=rec.parent
  # Jan 31, 2016 require that firstpart be a substantive
  if (not parentRec) or (not parentRec.substantiveP()):
   return
  parentKey = parentRec.key1
  parts = re.split(r'-',rec.key2)
  nparts = len(parts)
  for ipart in xrange(1,nparts):
   firstpart = ''.join(parts[0:ipart])
   lastpart = ''.join(parts[ipart:])
   firstpart = re.sub(r'[~@-]','',firstpart)
   lastpart = re.sub(r'[~@-]','',lastpart)
   #if not (firstpart==parentRec.key1):
   # continue
   # Recode so cpd2 is not needed
   if not ((firstpart==parentKey) or compound_pairP(parentKey,firstpart,lastpart)):
    continue
   if (lastpart in drec):
    # success
    rec.analysis = "%s-%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    rec.note = 'cpd1'
    return
   # Is last part a feminine form of a substantive?
   # Example aja-kUlA.  Here kUla is a headword, and kUlA is a feminine form
   lastparta = [x for x in adjective_stems(lastpart) if x in drec]
   if len(lastparta)>0:
    # success
    rec.analysis = "%s-%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    stems = ','.join(lastparta)
    rec.note = 'cpd1:%s<-%s'%(lastpart,stems)
    return 
   # otherwise, continue iparts loop

def analysis2_cpd1a(rec):
  """ Same as cpd1, except that the first part is either a different
   gender than the parent, or else an inflected form of the parent.
  """
  drec = hwcpd_dict
  parentRec=rec.parent
  # Jan 31, 2016 require that firstpart be a substantive
  if (not parentRec) or (not parentRec.substantiveP()):
   return
  parentkey1=parentRec.key1
  parts = re.split(r'-',rec.key2)
  nparts = len(parts)
  for ipart in xrange(1,nparts):
   firstpart = ''.join(parts[0:ipart])
   lastpart = ''.join(parts[ipart:])
   firstpart = re.sub(r'[~@-]','',firstpart)
   lastpart = re.sub(r'[~@-]','',lastpart)
   g = gender_formP(parentkey1,firstpart)
   if not g:
    g = inflected_form(parentkey1,firstpart,parentRec.lex,rec)
   if not g:
    continue
   if (lastpart in drec):
    # success
    rec.analysis = "%s+%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    rec.note = 'cpd1a:%s<-%s'%(firstpart,parentkey1)
    break # ipart loop


presandhi_hash = {} # dictionary
presandhi_hash["A"] = (("a","a"),("a","A"),("A","a"),("A","A"))
presandhi_hash["U"] = (("u","u"),("u","U"),("U","u"),("U","U"))
presandhi_hash["I"] = (("i","i"),("i","I"),("I","i"),("I","I"))
presandhi_hash["o"] = (("a","u"),("a","U"),("A","u"),("A","U"))
presandhi_hash["e"] = (("a","i"),("a","I"),("A","i"),("A","I"))
presandhi_hash["O"] = (("a","o"),("a","O"),("A","o"),("A","O"))
presandhi_hash["E"] = (("a","e"),("a","E"),("A","e"),("A","E"))

def analysis2_srs1(rec):
  drec = hwcpd_dict
  parts = re.split(r'@',rec.key2)
  parentRec=rec.parent
  if len(parts) == 1: # no @
   return
  if (not parentRec) or (not parentRec.substantiveP()):
   # Jan 31, 2016 require that firstpart be a substantive
   return
  if True:  # could dedent subsequent lines
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
    exit(1)
  srsparts=[]
  for (end,beg) in presandhi:
   if (rec.status != 'TODO'):
    continue
   firstpart = firstpart0+end
   lastpart = beg + lastpart0
   if firstpart != parentRec.key1:
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

known_prefixes = [
 'a', 'an',  
 'aBi', 'aBy',
 'anu', 'anv',
 'ava', 'apa',
 'aDi','aDy',
 'A',
 'upa', 
 'ut','ud','ul',
 'ni','ny',
 'nir','nih',
 'pari', 'pary',
 'pra', 'prati',
 'mahA'
 'vi','vy',
 'sam', 'saM', 'su', 'sa',
 'ati','aty',
 'antar',
 'sam','saM',
]
def analysis2_pfx1(rec):
 drec = hwcpd_dict
 parts = re.split(r'-',rec.key2)
 if len(parts)==1:
  return
 firstpart=parts[0]
 lastpart = ''.join(parts[1:])
 lastpart = re.sub(r'[~@-]','',lastpart)
 if not (firstpart in known_prefixes):
  return
 if  (lastpart in drec):
  # success
  rec.analysis = "%s-%s" % (firstpart,lastpart)
  rec.status = 'DONE'
  rec.note = 'pfx1:%s' %(firstpart)
  return
 # Example aDi-vedanIyA
 lastparta = [x for x in adjective_stems(lastpart) if x in drec]
 if len(lastparta)>0:
  # success
  rec.analysis = "%s-%s" %(firstpart,lastpart)
  rec.status = 'DONE'
  stems = ','.join(lastparta)
  rec.note = 'pfx1:%s:%s<-%s'%(firstpart,lastpart,stems)
  return 

def analysis2_pfx2(rec):
 drec = hwcpd_dict
 parts = re.split(r'~',rec.key2)
 if len(parts)==1:
  return
 firstpart=parts[0]
 lastpart = ''.join(parts[1:])
 lastpart = re.sub(r'[~@-]','',lastpart)
 if not (firstpart in known_prefixes):
  return # not applicable
 if (lastpart in drec):
  # success
  rec.analysis = "%s+%s" % (firstpart,lastpart)
  rec.status = 'DONE'
  rec.note = 'pfx2:%s' %(firstpart)
  return

def adjective_stems(a):
 """Example a=kUlA. Here 'a' could be a feminine stem of 'kUla', so the
  list we return would include 'kUla'
 """
 if a.endswith('ikA'):
  return [a[0:-3]+'ika',a[0:-3]+'aka']
 if a.endswith('A'):
  return [a[0:-1]+'a']
 if a.endswith(('matI','vatI','yatI')):
  return [a[0:-1]]
 if a.endswith('rajYI'):
  return [a[0:-2]+'an']
 if a.endswith(('inI','iRI')):
  return [a[0:-3]+'in']
 return []

def feminine_forms(b):
 """Return a list of possible feminine forms of 'b', based solely on the
    ending of 'b'
 """
 if b.endswith(('mat','vat','yat')):
  return [b+'I']
 if b.endswith('in'):
  return [b+'I',b[0:-1]+'RI']  
 if b.endswith('aka'):
  return [b[0:-3]+'akA',b[0:-3]+'ikA']
 if b.endswith('a'):
  return [b[0:-1]+'A',b[0:-1]+'I']
 if b.endswith('rAjan'):
  return [b[0:-2]+'YI']
 return []

def gender_formP(b,a):
 """ is 'a' a feminine form of 'b'?
 """
 if a in feminine_forms(b):
  return 'f'
 if b == a:
  return 'same' # assume different gender in a (e.g. a is 'm', b is m:f:n')
 return None

def analysis2_gender(rec):
  H = rec.H
  if H[-1]!='B':
   return
  rec0 = rec.parenta
  if rec0 == None:
   return
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

def inflected_form(b,a,lexb,lexa):
 """ is 'a' an inflected form of 'b'?
 """
 if (b + 'm') == a:
  return '2' # accusative 
 if (b[0:-1]+'ena') == a:
  return '3' # instrumental of noun ending in 'a'
 if (b[0:-1]+'eRa') == a:
  return '3' # instrumental of noun ending in 'a', with sandhi
 if (b[0:-1]+'Aya') == a:
  return '4' # dative of noun ending in 'a'
 if (b[0:-1]+'At') == a:
  return '5' # ablative of noun ending in 'a'
 if (b[0:-1]+'asya') == a:
  return '6' # genitive of noun ending in 'a'
 if (b==a) and (b[-1:] in ['i','u']) and (lexa == 'ind'):
  return '2' # accusative of neuter noun ending in 'i' or 'u'
 if (b[0:-1]+'e') == a:
  return '7' # locative of noun ending in 'a'
 if b.endswith('at') and ((b+'A')==a):
  return '3' # instrumental of noun ending in 'at'
 if b.endswith('A') and ((b[0:-1]+'ayA')==a):
  return '4' # dative of noun ending in 'A'
 if b.endswith('a') and ((b[0:-1]+'ayA')==a):
  lexparts=re.split(r':',lexb)
  if ('f' in lexparts) or ('f#A' in lexparts):
   return '3' # 'b' is an adjective in 'a'.
 if b.endswith('i') and ((b[0:-1]+'O')==a):
  return '7' # locative of noun ending in 'i'
 if b.endswith('u') and ((b[0:-1]+'O')==a):
  return '7' # locative of noun ending in 'u'
 if (b==a) and (b=='aByagni'):
  return '7,Pan2.1.14' # ? Pan 2-1,14
 if b.endswith('i') and ((b[0:-1]+'yA')==a):
  return '4' # dative of noun ending in 'i' (amatyA)

 if b.endswith('a') and ((b[0:-1]+'ezu')==a):
  return '3pl' # locative pl. of noun ending in 'a'
 if b.endswith('an') and ((b[0:-2]+'nA')==a):
  return '3' # instrumental of neuter noun ending in 'an'
 if b.endswith('an') and ((b+'A')==a):
  return '3' # instrumental of m. noun ending in 'an'
 if b.endswith(('i','u')) and ((b+'nA')==a):
  return '3' # instrumental of m/n nouns ending in i or u
 if b.endswith('at') and ((b+'i')==a):
  return '7' # locative of noun ending in 'at'
 if b.endswith(('h','s','d','t')) and ((b+'A')==a):
  return '3' # locative of noun ending in 'h' (prAsah) or 's'
 if ((b+'tas')==a) or ((b+'Sas')==a):
  return 'wsfx-tas'  # not inflected form. Only a few
 return None

def analysis2_inflected(rec):
  H = rec.H
  if H[-1]!='C':
   return
  rec0=rec.parenta
  if rec0 == None: #should not happen
   return
  H0=H[0:1]
  g = inflected_form(rec0.key1,rec.key1,rec0.lex,rec.lex)
  if g:
   # success. g is the case number of the inflected form
   rec.analysis = rec.key1
   rec.status = 'DONE'
   rec.note = 'inflected:%s'%g

def analyze_rec(rec,wrecs,zipped,unimplemented):
 """ zipped in a list of tuples (option,analysis_function_for_option)
 """
 for (option,f) in zipped:
  if rec.status != 'TODO': # prior option solved
   return
  if option=='wsfx':
   f(rec,wrecs)
  elif option in unimplemented: # not implemented yet
   continue
  else:
   f(rec)

def analyze_rec_cC(recorig,wrecs,zipped,unimplemented):
 """ zipped in a list of tuples (option,analysis_function_for_option)
 """
 # Often, when a compound has a 2nd part whose spelling starts with 'C',
 # the spelling of that second part starts with 'cC'.
 m = re.search(r'^(.*?)-cC(.*)$',recorig.key2)
 if not m: # this analysis not applicable
  return
 # construct a copy of rec. A 'Shallow' copy suffices
 import copy
 rec = copy.copy(recorig)
 # remove the 'm' from the end of key1 and key2
 # replace 'cC' with 'C' in key2
 rec.key2 = m.group(1)+'-C'+m.group(2)
 # Try to analyze this modified record
 analyze_rec(rec,wrecs,zipped,unimplemented)
 if rec.status == 'TODO':  #analysis failed
  return
 # analysis succeeded. Modify recorig accordingly
 recorig.analysis = rec.analysis
 recorig.status = rec.status
 recorig.note = rec.note + ':-cC'  # so we'll know this route required

def analyze_rec_m(recorig,wrecs,zipped,unimplemented):
 """ zipped in a list of tuples (option,analysis_function_for_option)
 """
 # applies only when key1 ends in 'm'
 if not (recorig.key1.endswith('m')):
  return
 # construct a copy of rec. A 'Shallow' copy suffices
 import copy
 rec = copy.copy(recorig)
 # remove the 'm' from the end of key1 and key2
 rec.key1 = re.sub(r'm$','',rec.key1)
 rec.key2 = re.sub(r'm$','',rec.key2)
 # Try to analyze this modified record
 analyze_rec(rec,wrecs,zipped,unimplemented)
 if rec.status == 'TODO':  #analysis failed
  return
 # analysis succeeded. Modify recorig accordingly
 recorig.analysis = rec.analysis
 recorig.status = rec.status
 recorig.note = rec.note + ':+m'  # so we'll know this route required

def analysis_all(recs):
 options=['noparts','wsfx','cpd1','srs1','gender',
  'cpd2','cpd_nan','cpd3','inflected','pfx1',
  'cpd1a','pfx2',
 ]
 options = ['noparts','wsfx','cpd1','srs1','gender',
 'cpd_nan','cpd3','inflected','pfx1',
 'cpd1a','pfx2',
 ]
 unimplemented = []
 noptions=len(options)
 localdict = globals()
 functions = []
 for option in options:
  fcnname = "analysis2_%s" % option
  if option in unimplemented:
   print option,"not yet implemented"
   functions.append(None)
   continue
  try:
   functions.append(localdict[fcnname])
  except:
   print "analysis_all. Unknown option:",option, fcnname
   exit(1)

 wrecs = init_Whitney_sfx('auxiliary/wsfx.txt')

 zipped = zip(options,functions)
 for rec in recs:
  if rec.status != 'TODO': # only try analyis of those marked 'TODO'
   continue
  # try each of the options
  analyze_rec(rec,wrecs,zipped,unimplemented)
  if rec.status != 'TODO': # we solved it
   continue
  # try each option again, sometimes
  analyze_rec_m(rec,wrecs,zipped,unimplemented)
  if rec.status != 'TODO': # we solved it
   continue
  analyze_rec_cC(rec,wrecs,zipped,unimplemented)

if __name__ == "__main__":
 option = sys.argv[1]
 filein  = sys.argv[2] # either all.txt or a previous analysis of all.txt
 if option == 'all':
  recs = init_analysis(filein,'init')
 else:
  recs = init_analysis(filein,option) # normally not use

 init_parents(recs)
 init_parentsa(recs)
 hwcpd_dict = init_hwcpd_dict(recs) 

 if option == 'init':
  fileout = sys.argv[3]
 elif len(sys.argv)==(3+1):
  fileout = sys.argv[3]
 else:
  fileout = filein # write output to same file name as input.
 if option != 'init':
  if option == 'all':
   analysis_all(recs)
  else:
   print "option must be 'all'"
   exit(1)
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
  # aggregate some items
  note = re.sub(r':.*$','',rec.note)
  x = "%4s %10s" %(rec.status,note)
  c[x]+=1
 #for x,n in c.iteritems():
 for x in sorted(c.keys()):
  print "%6d %s" %(c[x],x)
