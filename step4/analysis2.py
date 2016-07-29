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
import copy
from scharfsandhi import ScharfSandhi
from partition import partition

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
  # July 25, 2016
  self.adjust_key2()
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
  self.childrena = [] # determined by init_parentsa
 
 corrections_key2 = {
  "4860":"anati-dfSya",
  "4860.1":"anati-dfSna",
 }
 def adjust_key2(self):
  """ Correct some errors in key2
  """
  if self.L in Analysis.corrections_key2:
   old = self.key2
   self.key2 =  Analysis.corrections_key2[self.L]
   print "Correcting key2:",self.L,self.key1,old,"=>",self.key2

 def __repr__(self):
  note=self.note
  if self.status == 'TODO':
   if self.parent:
    note = '%s:parent=%s'%(self.note,self.parent.key1)
    if self.parent.type == 'VERB':
     note = "%s:VERB"%note
  parts=(self.H,self.L,self.key1,self.key2,self.lex,self.analysis,self.status,note) 
  return '\t'.join(parts)

 def substantiveP(self):
  #return self.type not in ('VERB','SEE','NONE')
  #return self.type not in ('VERB','SEE')
  return self.type not in ('VERB')


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
     July 24, 2016.  Also, determine childrena attribute.
     For a substantive with A(probably never), B or C children,
      the childrena attribute contains the spelling of these A,B,C children.
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
  # update childrena of irec0
  rec0 = recs[irec0]
  if rec.key1 not in rec0.childrena:
   rec0.childrena.append(rec)

def analysis2_noparts(rec):
  found = rec.lex.startswith('LOAN') or (not re.search(r'[~@-]',rec.key2))
  if found:
   (rec.analysis,rec.status,rec.note)=(rec.key2,'DONE','noparts')

def analysis2_wsfx(rec,wrecs):
  drec = hwcpd_dict
  parts = re.split(r'-',rec.key2)
  parentRec=rec.parent
  if parentRec == None:
   return
  lastpart=parts[-1]
  firstpart = ''.join(parts[0:-1])
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

def analysis2_pfxderiv(rec):
  drec = hwcpd_dict
  parts = re.split(r'-',rec.key2)
  parentRec=rec.parent
  if parentRec == None:
   return
  if parentRec.L in Whitney_deriv.d:
   pass
  else:
   # try parent of parent
   parentRec = parentRec.parent
   if parentRec == None:
    return
   if parentRec.L not in Whitney_deriv.d:
    return
  derivrec = Whitney_deriv.d[parentRec.L]
  pfxderivs = derivrec.pfxderivs
  if rec.key1 in pfxderivs:
   #success
   rec.analysis = rec.key1
   rec.status = 'DONE'
   rec.note = 'pfxderiv:%s'%derivrec.analysis
   return
  # try some other forms, which do NOT appear in Whitney's derivatives
  # TODO
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

class Whitney_deriv(object):
 d = {} 
 d1 = {}
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.L,self.key1,self.key2,self.root,self.prefixes,self.analysis,self.derivstring) = re.split('\t',line)
  self.pfxderivs = re.split(r' +',self.derivstring)
  Whitney_deriv.d[self.L] = self
  for pfxderiv in self.pfxderivs:
   Whitney_deriv.d1[pfxderiv]=self

def init_Whitney_deriv(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Whitney_deriv(x) for x in f if (not x.startswith(';'))]
 print len(recs),"records read from",filein
 return recs

def gender_form(key1,lex):
 if key1.endswith('a'):
  if lex in ('m','n'):
   return key1
  if lex in ('f','f#A'):
   return key1[0:-1]+'A'
  if lex =='f#I':
   return key1[0:-1]+'I'
  if (lex == 'f#ikA') and key1.endswith(('aka','ika')):
   return key1[0:-3]+'ikA'
 # _in
 if key1.endswith('in'):
  if lex == 'm':
   return key1
  if lex == 'n':
   return key1[0:-1] # drop final 'n'
  if lex == 'f':
   return key1+'I'  # not always correct, sometimes key1[0:-1]+'RI'
  return key1
 if key1.endswith(('a','I','i')) and (lex in ['f#I','f#i']):
  return key1[0:-1] + lex[-1:]
 return key1

def inflected_forms(key1):
 """ return miscellaneous inflected forms. Return a list of strings
 """
 forms=[]
 if key1.endswith('i'):
  forms.append(key1[0:-1]+"yA") # 3s
 elif key1 == 'go':
  forms.append('goH')
 return forms

additional_forms_special = {
 "SIrzan":"SIrzRI",  # nIlaSIrzRI
 "kaMja":"kaYja",    # kAla-kaYja
 "saMDi":"sanDi",    # kARqasanDi
 "saMDyA":"sanDyA",  # agrasanDyA
 "hiNkAra":"hiMkAra", # dvi-hiMkAra
 "kiMcana":"kiYcana", # akiYcana
 "kilbiza":"kilviza", # akilviza
 "stana":["stanI","stanA"], # ifc f. forms
 "ABA":"ABa", # apramARA@Ba, etc
 "BrUkuwI":"BrUkuwi", # saM-hata-BrUkuwi-muKa
 "GoRA":"GoRa", # ud-GoRa
 "icCA":"icCa", # pUrRe@cCa,
 "AKyA":"AKya", # SakrAKya
}
def additional_forms(rec):
 """ Crude generation of additional forms for substantives
 """
 forms=[]
 # require normal substantive or perhaps missing
 if rec.type not in ['S','NONE']: 
  return forms
 key1 = rec.key1
 lexparts = re.split(r':',rec.lex)
 for lex in lexparts:
  form = gender_form(key1,lex)
  forms.append(form)
 # compound forms
 if key1.endswith(('in','an')):
  forms.append(key1[0:-1])  # drop final 'n'
 # some special, adhoc cases
 if key1 in additional_forms_special:
  a = additional_forms_special[key1]
  if not isinstance(a,list):
   a = [a]
  for a1 in a:
   forms.append(a1)
 # some inflected forms
 for x in inflected_forms(key1):
  forms.append(x)
 # July 25, 2016.  anusvAra variants.
 key1a = re.sub(r'sam([pPbBm])',r'saM\1',key1)
 key1b = re.sub(r'saM([pPbBm])',r'sam\1',key1)
 if key1a != key1:
  forms.append(key1a)
 if key1b != key1:
  forms.append(key1b)
 key1a = re.sub(r'san([tTdDn])',r'saM\1',key1)
 key1b = re.sub(r'saM([tTdDn])',r'san\1',key1)
 if key1a != key1:
  forms.append(key1a)
 if key1b != key1:
  forms.append(key1b)
 key1a = re.sub(r'sam(kx)',r'saM\1',key1)
 key1a = re.sub(r'saM(kx)',r'sam\1',key1)
 if key1a != key1:
  forms.append(key1a)
 if key1b != key1:
  forms.append(key1b)

 return forms

def init_hwcpd_dict(recs):
 """ hwcpd_dict is a dictionary with 'key1' as key1
     Value is True if for some record (recs),
     the rec.type is other than ('VERB','SEE','NONE')
 """
 drec = {}
 # keys that may resolve parts of samasa
 n = 0
 for rec in recs:
  if not rec.substantiveP():
   continue
  drec[rec.key1]=rec
 # Feb 8, 2016. Also, do a preliminary generation of additional forms 
 for rec in recs:
  if rec.key1 not in drec:
   continue
  forms = additional_forms(rec)
  for form in forms:
   if form not in drec:
    drec[form]=rec
 return drec


vowels = 'aAiIuUfFxXeEoO'
soft_consonants = 'gGNjJYqQRdDnbBmyrlv'
hard_consonants = 'kKcCwWtTpPs' # sibilants too?
all_consonants = soft_consonants+hard_consonants+'zSh'

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
 if parent.endswith('as') and x.endswith('aS') and (y[0:1] in ['c']) and (parent[0:-2]==x[0:-2]):
  return True
 if x.endswith(('m','M')) and (parent==x[0:-1]) and (y[0:1] in all_consonants):
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
    rec.note = 'cpd_nan:%s<-%s'%(lastpart,stems)
    return 
   # example a-garta-skandya
   # check if all parts (but the first,'a' or 'an') is a substantivep
   remainingparts = [re.sub('~@','',part) for part in parts[1:]]
   notfounds = [x for x in remainingparts if x not in drec]
   if len(notfounds)==0:
    # success
    rec.analysis = "%s-%s" %(firstpart,'-'.join(remainingparts))
    rec.status = 'DONE'
    rec.note = 'cpd_nan:multicpd'
    return     

def analysis2_cpd3(rec):
  """ uses parent 
  """
  drec = hwcpd_dict
  parentRec=rec.parent
  if (not parentRec) or (not parentRec.substantiveP()):
   return
  parts = re.split(r'-',rec.key2)
  nparts = len(parts)
  parentKey = parentRec.key1
  starFlag=False
  star = '*'
  for ipart in xrange(1,nparts):
   firstpart = ''.join(parts[0:ipart])   
   firstpart = re.sub(r'[~@-]','',firstpart)
   #if (firstpart != parentKey):
   # continue
   # are all of the remaining parts compound components?
   lastparts = parts[ipart:]
   ok = True
   okparts=[]
   for p in lastparts:
    p = re.sub(r'[~@-]','',p)
    if p in drec:
     okparts.append(p)
     continue
    tempparts = [x for x in adjective_stems(p) if x in drec]
    if len(tempparts) > 0:
     okparts.append(p+star)
     starFlag=True
     continue
    # fails
    ok = False
    break
   if ok:
    if (firstpart == parentKey):
     # success
     rec.analysis = "%s-%s" %(parentKey,'-'.join(okparts))
     rec.status = 'DONE'
     rec.note = 'cpd3'
     if starFlag:
      rec.note = rec.note + ':'+star
     break # ipart loop
    # try sandhi
    # example: prati~pat-tUrya, parent=pratipad
    sandhi = ScharfSandhi()
    sandhi.simple_sandhioptions('C') # compound sandhi
    lastpart = ''.join(okparts)
    lastpart = lastpart.replace(star,'')
    sandhijoin = sandhi.sandhi('%s-%s'%(parentKey,lastpart))
    if sandhijoin == rec.key1:
     # success
     rec.analysis = "%s-%s" %(parentKey,'+'.join(okparts))
     rec.status = 'DONE'
     rec.note = 'cpd3:%s<-%s(sandhi)'%(firstpart,parentKey)
     if starFlag:
      rec.note = rec.note + star
     break # ipart loop

def prev_analysis2_cpd3(rec):
  """ uses parent """
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
   #if (firstpart != parentKey):
   # continue
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
    if (firstpart == parentKey):
     # success
     rec.analysis = "%s-%s" %(parentKey,'-'.join(okparts))
     rec.status = 'DONE'
     rec.note = 'cpd3'
     break # ipart loop
    # try sandhi
    # example: prati~pat-tUrya, parent=pratipad
    sandhi = ScharfSandhi()
    sandhi.simple_sandhioptions('C') # compound sandhi
    lastpart = ''.join(okparts)
    sandhijoin = sandhi.sandhi('%s-%s'%(parentKey,lastpart))
    if sandhijoin == rec.key1:
     # success
     rec.analysis = "%s-%s" %(parentKey,'+'.join(okparts))
     rec.status = 'DONE'
     rec.note = 'cpd3:%s<-%s(sandhi)'%(firstpart,parentKey)
     break # ipart loop

def analysis2_cpd4(rec):
  """ A compound, but not of  the parent. Only H1,2
   Require each '-' component to be a known substantive.
   Example: muRqI-kalpa
  """
  drec = hwcpd_dict
  if rec.H not in ['1','2']:
   # only do this analysis for H1 or H2 case
   return
  parts = re.split(r'-',rec.key2)
  okparts=[]
  for ipart in xrange(0,len(parts)):
   part = parts[ipart]
   part = re.sub('~@','',part)
   if part not in drec:
    return # this analysis fails
   okparts.append(part)
  # success
  rec.analysis = '-'.join(okparts)
  rec.status = 'DONE'
  rec.note = 'cpd4'

def previous_analysis2_cpd1(rec):
  """ uses parent"""
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
   # is lastpart a derivative form?
   if lastpart in Whitney_deriv.d1:
    # success
    rec.analysis = "%s-%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    o =  Whitney_deriv.d1[lastpart] # a Whitney_deriv object
    rec.note = 'cpd1:%s<-%s(deriv)'%(lastpart,o.key1)
    return 
   # Cases like jyoti-zwoma
   # otherwise, continue iparts loop

def analysis2_cpd1(rec):
 """ uses parent"""
 drec = hwcpd_dict
 parentRec=rec.parent
 # Jan 31, 2016 require that firstpart be a substantive
 if (not parentRec) or (not parentRec.substantiveP()):
  return
 parentKeys = [parentRec.key1]
 for r in parentRec.childrena:
  parentKeys.append(r.key1)
 #if rec.key1 == 'uKAsaMBaraRa':
 # print rec.key1,"has parentKeys=",parentKeys
 #parentKey = parentRec.key1
 parts = re.split(r'-',rec.key2)
 nparts = len(parts)
 # find the break point identifying the parent
 # There may be no such point. 
 # There may be more than 1 such point:
 #   viDu-M-tuda  parent = viDu.
 firstparts=[]
 for ipart in xrange(1,nparts):
  firstpart = ''.join(parts[0:ipart])
  lastpart = ''.join(parts[ipart:])
  firstpart = re.sub(r'[~@-]','',firstpart)
  lastpart = re.sub(r'[~@-]','',lastpart)
  for parentKey in parentKeys:
   if  ((firstpart==parentKey) or compound_pairP(parentKey,firstpart,lastpart)):
    firstparts.append((ipart,firstpart,lastpart))
    break
 if len(firstparts)==0: # couldn't identify the parent
  return
 # take the 'longest' firstpart
 (ipart,firstpart,lastpart) = firstparts[-1] # last one is longest
 if (lastpart in drec):
  # success
  rec.analysis = "%s-%s" %(firstpart,lastpart)
  rec.status = 'DONE'
  if parentKey != parentRec.key1:
   t = ':*'
  else:
   t = ''
  rec.note = 'cpd1%s'%t
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
 # is lastpart a derivative form?
 if lastpart in Whitney_deriv.d1:
  # success
  rec.analysis = "%s-%s" %(firstpart,lastpart)
  rec.status = 'DONE'
  o =  Whitney_deriv.d1[lastpart] # a Whitney_deriv object
  rec.note = 'cpd1:%s<-%s(deriv)'%(lastpart,o.key1)
  return 
 # Maybe lastpart is an srs compound?
 lastpart = ''.join(parts[ipart:])
 if '@' in lastpart:
  # possibly could analyze further, but assume lastpart is just X@Y
  lastpart = re.sub(r'[~-]','',lastpart) 
  srsparts = floating_srs(lastpart)
  if srsparts:
   # success
   # srsparts is a list of tuples (a,b) each of which explains lastpart. 
   rec.note='cpd1:srs'
   analyses = ["%s-%s+%s" %(firstpart,a,b) for (a,b) in srsparts]
   rec.analysis = ','.join(analyses)
   rec.status='DONE'
   return
 # otherwise, routine fails to find an analysis

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
    # special cases
    if (parentkey1=='aNguli') and (firstpart=='aNgulI'):
     g = 'special'
    elif (parentkey1.endswith('m') and firstpart.endswith('M') and
          parentkey1[0:-1]==firstpart[0:-1]):
     # evaM-Sila, etc.
     g = 'special'
   if not g:
    continue
   if (lastpart in drec):
    # success
    rec.analysis = "%s+%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    rec.note = 'cpd1a:%s<-%s'%(firstpart,parentkey1)
    break # ipart loop
   # is lastpart a gender variant of a known substantive?
   lastfems = feminine_forms(lastpart)
   lastmasculines = masculine_forms(lastpart)
   lastothers = lastfems + lastmasculines
   foundforms = [x for x in lastothers if x in drec]
   if len(foundforms)>0:
    # success
    lastparta='|'.join(foundforms)
    rec.analysis = "%s+%s" %(firstpart,lastpart)
    rec.status = 'DONE'
    rec.note = 'cpd1a:last:%s<-%s'%(lastpart,lastparta)
    break # ipart loop


presandhi_hash = {} # dictionary
presandhi_hash["A"] = (("a","a"),("a","A"),("A","a"),("A","A"))
presandhi_hash["U"] = (("u","u"),("u","U"),("U","u"),("U","U"))
presandhi_hash["I"] = (("i","i"),("i","I"),("I","i"),("I","I"))
presandhi_hash["o"] = (("a","u"),("a","U"),("A","u"),("A","U"))
presandhi_hash["e"] = (("a","i"),("a","I"),("A","i"),("A","I"))
presandhi_hash["O"] = (("a","o"),("a","O"),("A","o"),("A","O"))
presandhi_hash["E"] = (("a","e"),("a","E"),("A","e"),("A","E"))

def floating_srs(key2):
  # key2 is a 'fragment' of some record's key2
  # returns a list of analyses of key2 as an srs-compound.
  # Or, may return None
  # an analysis is a tuple (x,y) such that x+y derives key2 via srs sandhi
  # at 'the' @ point in key2, 
  # AND both x and y are known substantives
  drec = hwcpd_dict
  parts = re.split(r'@',key2)
  if len(parts) == 1: # no @
   return None
  #if (not parentRec) or (not parentRec.substantiveP()):
   # Jan 31, 2016 require that firstpart be a substantive
  # return
  lastpart0=parts[-1]  # split at the last '@', if there is more than one '@'
  lastpart0 = re.sub(r'[~@-]','',lastpart0)
  firstpart = ''.join(parts[0:-1])
  firstpart = re.sub(r'[~@-]','',firstpart)
  firstpart0 = firstpart[0:-1] # all but last character, which is the sandhi
  c0 = firstpart[-1] # last character
  if c0 not in presandhi_hash:
   print "DBG: floating_srs anomaly",c0,key2
   return None
  presandhi = presandhi_hash[c0]
  srsparts=[]
  for (end,beg) in presandhi:
   firstpart = firstpart0+end
   lastpart = beg + lastpart0
   if firstpart not in drec:
    continue
   if lastpart not in drec:
    continue
   srsparts.append((firstpart,lastpart))
  if len(srsparts)==0:
   return None
  return srsparts

def previ_floating_compounds(lastpart,allowOne=False):
 drec = hwcpd_dict
 lastanswers=[]
 lparts = re.split(r'-',lastpart)
 lpartitions = partition(lparts)
 for ipartition in xrange(0,len(lpartitions)):
  if (ipartition == 0) and (not allowOne):
   continue
  lpartition = lpartitions[ipartition]
  subwords=[''.join(subseq) for subseq in lpartition]
  # remove @,~ from each subword
  subwords1 = [re.sub(r'[~@]','',subword) for subword in subwords]
  okwords = [subword for subword in subwords1 if subword in drec]
  if len(okwords) == len(subwords1):
   lastpart1 = '-'.join(okwords)
   lastanswers.append(lastpart1)
   # by the construction of lpartitions, the first case means that
   # okwords has just one element. In this case, we don't consider
   # other partitions
   if (ipartition == 0) and allowOne:
    break
 return lastanswers

def floating_compounds(lastpart,allowOne=False):
 star='*'
 drec = hwcpd_dict
 lastanswers=[]
 lparts = re.split(r'-',lastpart)
 lpartitions0 = partition(lparts)
 # sort this way so lpartitions[0] == lparts
 lpartitions = sorted(lpartitions0,key=lambda p: len(p), reverse=True)
 for ipartition in xrange(0,len(lpartitions)):
  lpartition = lpartitions[ipartition]
  if (len(lpartition) == 1) and (not allowOne):
   continue
  subwords=[''.join(subseq) for subseq in lpartition]
  okwords=[]
  for subword in subwords:
   subword1 = re.sub(r'[~]','',subword)
   # First, try removing any @ 
   subword2 = re.sub(r'[@]','',subword1)
   if subword2 in drec:
    okwords.append(subword2)
    continue
   # July 28, 2016. Maybe subword2 is a gender variant of a headword?
   if len([x for x in adjective_stems(subword2) if x in drec]) > 0:
    okwords.append(subword2 + star)
    continue
   # Second, if there is an @, try analyzing as a srs compound
   if '@' in subword1:
    srsparts = floating_srs(subword1)
    if srsparts:
     analyses = ["%s+%s" %(a,b) for (a,b) in srsparts]
     analysis = ','.join(analyses)
     okwords.append('(%s)'%analysis)
     continue
  if len(okwords) == len(subwords):
   lastpart1 = '-'.join(okwords)
   lastanswers.append(lastpart1)
   if (len(lpartition) == len(lparts)): 
    break # ? 
   # by the construction of lpartitions, the first case means that
   # okwords has just one element. In this case, we don't consider
   # other partitions
   if (ipartition == 1) and allowOne:
    break
 return lastanswers

def analysis2_cpd5(rec):
 analyses = floating_compounds(rec.key2,allowOne=False)
 if len(analyses)== 0:
  return
 rec.analysis = ','.join(analyses)
 rec.status = 'DONE'
 if len(analyses) == 1:
  rec.note = 'cpd5'
 else:
  rec.note = 'cpd5?'

def analysis2_srs2(rec):
 """ a more robust variant of srs1
  This catches vidyA@~DirAja-tIrTa where srs1 does not
 """
 drec = hwcpd_dict
 parts = re.split(r'@',rec.key2)
 parentRec=rec.parent
 if len(parts) == 1: # no @
  return
 if (not parentRec) or (not parentRec.substantiveP()):
  # Jan 31, 2016 require that firstpart be a substantive
  return
 # There may be more than one '@' part. Get the one matching parent
 ipart=None
 for i in xrange(1,len(parts)):
  part = ''.join(parts[0:i])
  part = re.sub(r'[~-]','',part)
  if part[0:-1]==parentRec.key1[0:-1]:
   ipart=i
   break
 if ipart == None:
  # no luck
  return
 # continue with analysis
 firstpart = ''.join(parts[0:i])
 firstpart = re.sub(r'[~-]','',firstpart)
 #lastpart0=parts[-1]
 #lastpart0 = re.sub(r'[~@-]','',lastpart0)
 firstpart0 = firstpart[0:-1] # all but last character, which is the sandhi
 c0 = firstpart[-1:] # last character
 presandhi = presandhi_hash[c0]
 srsbegs=[]
 firstpart1=None
 for (end,beg) in presandhi:
  firstpart = firstpart0+end
  if firstpart == parentRec.key1:
   if beg not in srsbegs: # don't repeat
    srsbegs.append(beg)
    firstpart1=firstpart
 if len(srsbegs) == 0:
  # no luck. Should not happen
  return
 lastpart0 = ''.join(parts[ipart:])
 lastpart0 = re.sub(r'~','',lastpart0)
 lastanswers=[]
 for beg in srsbegs:
  # analyze the rest of the word. 
  lastpart = beg+lastpart0
  #lastpart1 = re.sub(r'-','',lastpart)
  #if lastpart1 in drec:
  # lastanswers.append(lastpart1)
  # continue
  # analyze lastpart as a compound
  current_lastanswers = floating_compounds(lastpart,allowOne=True)
  for temp in current_lastanswers:
   lastanswers.append(temp)
  """
  lparts = re.split(r'-',lastpart)
  lpartitions = partition(lparts)
  for ipartition in xrange(0,len(lpartitions)):
   lpartition = lpartitions[ipartition]
   subwords=[''.join(subseq) for subseq in lpartition]
   okwords = [subword for subword in subwords if subword in drec]
   if len(okwords) == len(subwords):
    lastpart1 = '-'.join(okwords)
    lastanswers.append(lastpart1)
    # by the construction of lpartitions, the first case means that
    # okwords has just one element. In this case, we don't consider
    # other partitions
    if ipartition == 0:
     break
  """
 if len(lastanswers)>0:
  # success. Note firstpart1 = parentRec.key1
  analyses = ["%s+%s"%(firstpart1,lastpart) for lastpart in lastanswers]
  rec.analysis = ','.join(analyses)
  rec.status = 'DONE'
  if len(lastanswers) == 1:
   rec.note = 'srs2'
  else:
   rec.note = 'srs2?'

def analysis2_srs3(rec):
 """ More general than srs2, in that there is no requirement that the
 first be the parent. It is limited, in that only 2 parts (defined by @) are
 allowed.
 """
 drec = hwcpd_dict
 parts = re.split(r'@',rec.key2)
 parentRec=rec.parent
 if len(parts) == 1: # no @
  return
 #if len(parts) > 2:
 # return
 # continue with analysis
 firstpart = parts[0]
 firstpart = re.sub(r'[~-]','',firstpart)
 firstpart0 = firstpart[0:-1] # all but last character, which is the sandhi
 c0 = firstpart[-1:] # last character
 presandhi = presandhi_hash[c0]
 srsbegs=[]
 firstpart1=None
 for (end,beg) in presandhi:
  firstpart = firstpart0+end
  if firstpart in drec:
   if beg not in srsbegs: # don't repeat
    srsbegs.append(beg)
    firstpart1=firstpart
 if len(srsbegs) == 0:
  # no luck. Should not happen
  return
 lastpart0 = ''.join(parts[1:])
 lastpart0 = re.sub(r'~','',lastpart0)
 lastanswers=[]
 for beg in srsbegs:
  # analyze the rest of the word. 
  lastpart = beg+lastpart0
  current_lastanswers = floating_compounds(lastpart,allowOne=True)
  for temp in current_lastanswers:
   lastanswers.append(temp)
 if len(lastanswers)>0:
  # success. 
  analyses = ["%s+%s"%(firstpart1,lastpart) for lastpart in lastanswers]
  rec.analysis = ','.join(analyses)
  rec.status = 'DONE'
  if len(lastanswers) == 1:
   rec.note = 'srs3'
  else:
   rec.note = 'srs3?'

known_prefixes = [
 'a', 'an',  
 'aBi', 'aBy',
 'anu', 'anv',
 'ava', 'apa', 'apA',
 'aDi','aDy',
 'A',
 'upa', 
 'ut','ud','ul','uc','uj','un',
 'ni','ny',
 'nir','nih',
 'pari', 'pary',
 'pra', 'prati',
 'mahA'
 'vi','vy',
 'sam', 'saM', 
 'su', 'sv',
 'sa',
 'ati','aty',
 'antar',
 'sam','saM',
]
def pfx1_main(key2):
 """ main logic of analysis2_pfx1, but doesn't use the 'rec'
 """
 drec = hwcpd_dict
 parts = re.split(r'-',key2)
 if len(parts)==1:
  return None
 firstpart=parts[0]
 lastpart = ''.join(parts[1:])
 lastpart = re.sub(r'[~@-]','',lastpart)
 if not (firstpart in known_prefixes):
  return
 if  (lastpart in drec):
  # success
  analysis = "%s-%s" % (firstpart,lastpart)
  status = 'DONE'
  note = 'pfx1:%s' %(firstpart)
  return (analysis,status,note)
 # Example uc-CiKaRqa
 if (firstpart == 'uc') and (lastpart.startswith('C')):
  # In example. Look up SiKaRqa
  lastpart = 'S' + lastpart[1:]
  if (lastpart in drec):
   # success
   analysis = "%s+%s" % (firstpart,lastpart)
   status = 'DONE'
   note = 'pfx1:%s' %(firstpart)
   return (analysis,status,note)

 # Example aDi-vedanIyA
 lastparta = [x for x in adjective_stems(lastpart) if x in drec]
 if len(lastparta)>0:
  # success
  analysis = "%s-%s" %(firstpart,lastpart)
  status = 'DONE'
  stems = ','.join(lastparta)
  note = 'pfx1:%s:%s<-%s'%(firstpart,lastpart,stems)
  return (analysis,status,note)

def analysis2_pfx1(rec):
 result = pfx1_main(rec.key2)
 if not result:
  return
 (rec.analysis,rec.status,rec.note)=result
 return

def prev_analysis2_pfx1(rec):
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
 # Example uc-CiKaRqa
 if (firstpart == 'uc') and (lastpart.startswith('C')):
  # In example. Look up SiKaRqa
  lastpart = 'S' + lastpart[1:]
  if (lastpart in drec):
   # success
   rec.analysis = "%s+%s" % (firstpart,lastpart)
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

def masculine_forms(b):
 return []

def gender_formP(b,a):
 """ is 'a' a feminine form of 'b'?
     is 'a' a masculine form of 'b' [not implemented]
 """
 if a in feminine_forms(b):
  return 'f'
 if b == a:
  return 'same' # assume different gender in a (e.g. a is 'm', b is m:f:n')
 #if a in masculine_forms(b):
 # return 'm'
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
   # May 19, 2016. Show key whose gender gives this. 
   # Alternate approach would be to show this key in rec.analysis, instead of rec.key1
   #rec.note = 'gender:%s' % g
   rec.note = 'gender:%s of %s' % (g,rec0.key1)

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
   # May 19, 2016. Show rec 
   rec.note = 'inflected:case %s of %s'%(g,rec0.key1)

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
 """ zipped is a list of tuples (option,analysis_function_for_option)
     July 26, 2016. expanded slightly to include ~.
     Also, included cases where 'c-C' should be analyzed as 'c-S'
 """
 # Often, when a compound has a 2nd part whose spelling starts with 'C',
 # the spelling of that second part starts with 'cC'.
 #m = re.search(r'^(.*?)-cC(.*)$',recorig.key2)
 #July 26. include
 m = re.search(r'^(.*?[-~])cC(.*)$',recorig.key2)
 if m: 
  # construct a copy of rec. A 'Shallow' copy suffices
  rec = copy.copy(recorig)
  # remove the 'm' from the end of key1 and key2
  # replace 'cC' with 'C' in key2
  rec.key2 = m.group(1)+'C'+m.group(2)
  # Try to analyze this modified record
  analyze_rec(rec,wrecs,zipped,unimplemented)
  if rec.status != 'TODO':  #analysis failed
   # analysis succeeded. Modify recorig accordingly
   recorig.analysis = rec.analysis
   recorig.status = rec.status
   recorig.note = rec.note + ':+cC'  # so we'll know this route required
   return
 #-----------------
 # first part failed. Try another
 # second part (July 26, 2016)
 m = re.search(r'^(.*?c-)C(.*)$',recorig.key2)
 if m: 
  # construct a copy of rec. A 'Shallow' copy suffices
  rec = copy.copy(recorig)
  # remove the 'm' from the end of key1 and key2
  # replace 'c-C' with 'c-S' in key2
  rec.key2 = m.group(1)+'S'+m.group(2)
  # Try to analyze this modified record
  analyze_rec(rec,wrecs,zipped,unimplemented)
  if rec.status != 'TODO':  #analysis failed
   # analysis succeeded. Modify recorig accordingly
   recorig.analysis = rec.analysis
   recorig.status = rec.status
   recorig.note = rec.note + ':+cC'  # so we'll know this route required
   return
 # no luck
 return

def analyze_rec_removesfx(recorig,wrecs,zipped,unimplemented):
 """ zipped in a list of tuples (option,analysis_function_for_option)
  recorig.key2 = XY, where Y is a known suffix. Remove Y and analyze X.
 """
 drec = hwcpd_dict
 key1 = recorig.key1
 key2 = recorig.key2
 suffixes = [sfx for sfx in Whitney_sfx.d if key1.endswith(sfx)]
 if len(suffixes) != 1:
  if len(suffixes) > 1:  # currently never happens (Feb 9, 2016)
   print "DBG: removesfx:",key1,suffixes
  return
 sfx = suffixes[0]
 key1 = re.sub("%s$"%sfx,'',key1)
 key2 = re.sub("%s$"%sfx,'',key2)
 # one possibility is that this modified key1 is already a substantive
 if key1 in drec:
  recorig.analysis = key1+"+"+sfx
  recorig.status = 'DONE'
  recorig.note = '+wsfx1:%s'%sfx  # so we'll know this route required
  return
 # otherwise, try an analysis after removing the suffix
 # construct a copy of rec. A 'Shallow' copy suffices
 rec = copy.copy(recorig)
 rec.key2 = key2
 rec.key1 = key1
 # Try to analyze this modified record
 analyze_rec(rec,wrecs,zipped,unimplemented)
 if rec.status == 'TODO':  #analysis failed
  return
 # analysis succeeded. Modify recorig accordingly
 recorig.analysis = rec.analysis+"+"+sfx
 recorig.status = rec.status
 recorig.note = rec.note + ':+wsfx:%s'%sfx  # so we'll know this route required

def analyze_rec_fauxcpd(recorig,wrecs,zipped,unimplemented):
 """ zipped in a list of tuples (option,analysis_function_for_option)
  recorig.key2 = X~Y, which we change to analyze as X-Y
 """
 key2 = recorig.key2
 if ('~' in key2) and ('-' not in key2) and ('@' not in key2):
  pass
 else:
  return  # this analysis not applicable
 parts = re.split(r'~',recorig.key2)
 if len(parts)!=2:
  # in case of more than 1 '~', this analysis does not apply
  return
 key2 = parts[0]+'-'+parts[1] 
 # construct a copy of rec. A 'Shallow' copy suffices
 rec = copy.copy(recorig)
 rec.key2 = key2
 # Try to analyze this modified record
 analyze_rec(rec,wrecs,zipped,unimplemented)
 if rec.status == 'TODO':  #analysis failed
  return
 # analysis succeeded. Modify recorig accordingly
 recorig.analysis = rec.analysis
 recorig.status = rec.status
 recorig.note = rec.note + ':+fauxcpd'  # so we'll know this route required

def analyze_rec_z(recorig,wrecs,zipped,unimplemented):
 """ zipped in a list of tuples (option,analysis_function_for_option)
     This analysis includes several 'sandhi' cases.
 """
 # Case 1
 # Often, when a compound has a 2nd part whose spelling starts with 's',
 # the spelling of that second part starts with 'z'.
 if re.search(r'-z',recorig.key2):
  key2 = re.sub(r'-zW','-sT',recorig.key2)
  key2 = re.sub(r'-zw','-st',key2)
  key2 = re.sub(r'-z','-s',key2)
  case = '+z'
 elif re.search(r'a-r',recorig.key2):
  key2 = re.sub(r'a-r','a-f',recorig.key2)
  case = '+a-r'
 elif re.search(r'a-R',recorig.key2):
  key2 = re.sub(r'a-R','a-n',recorig.key2)
  case = '+a-R'
 else:  # this analysis fails
  return
 # construct a copy of rec. A 'Shallow' copy suffices
 rec = copy.copy(recorig)
 rec.key2 = key2
 # Try to analyze this modified record
 analyze_rec(rec,wrecs,zipped,unimplemented)
 if rec.status == 'TODO':  #analysis failed
  return
 # analysis succeeded. Modify recorig accordingly
 recorig.analysis = re.sub(r'-','+',rec.analysis)
 recorig.status = rec.status
 recorig.note = rec.note + ':%s'%case  # so we'll know this route required

def analyze_rec_m(recorig,wrecs,zipped,unimplemented):
 """ zipped in a list of tuples (option,analysis_function_for_option)
 """
 # applies only when key1 ends in 'm'
 if not (recorig.key1.endswith('m')):
  return
 # construct a copy of rec. A 'Shallow' copy suffices
 rec = copy.copy(recorig)
 # remove the 'm' from the end of key1 and key2
 rec.key1 = re.sub(r'm$','',rec.key1)
 rec.key2 = re.sub(r'm$','',rec.key2)
 # Try to analyze this modified record
 analyze_rec(rec,wrecs,zipped,unimplemented)
 if rec.status != 'TODO':
  # analysis succeeded. Modify recorig accordingly
  recorig.analysis = rec.analysis
  recorig.status = rec.status
  recorig.note = rec.note + ':+m'  # so we'll know this route required
 
def analysis_all(recs):
 options=['noparts','wsfx','cpd1','srs1','gender',
  'cpd2','cpd_nan','cpd3','inflected','pfx1',
  'cpd1a','pfx2','cpd4','srs2','pfxderiv',
  'cpd5'
 ]
 options = ['noparts','wsfx','cpd1', #'srs1',
 'gender',
 'cpd_nan','cpd3','inflected','pfx1',
 'cpd1a','pfx2','cpd4','srs2','pfxderiv',
 'cpd5','srs3'
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
 wderivs = init_Whitney_deriv('auxiliary/pfxderiv.txt')

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
  if rec.status != 'TODO': # we solved it
   continue
  analyze_rec_z(rec,wrecs,zipped,unimplemented)
  if rec.status != 'TODO': # we solved it
   continue
  analyze_rec_fauxcpd(rec,wrecs,zipped,unimplemented)
  if rec.status != 'TODO': # we solved it
   continue
  # see if the word ends with a known suffix (e.g. 'ka','Iya', etc.)
  # and try to analyze without this suffix
  analyze_rec_removesfx(rec,wrecs,zipped,unimplemented)

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
  note = re.sub(r'[?]$','',note)
  x = "%4s %s" %(rec.status,note)
  c[x]+=1
 #for x,n in c.iteritems():
 for x in sorted(c.keys()):
  print "%6d %s" %(c[x],x)
