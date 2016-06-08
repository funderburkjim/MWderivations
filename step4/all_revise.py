""" all_revise.py
    May 23, 2016
    Read both all.txt and all_revise.txt;
    For each record in all_revise, match (using L) the record in all.txt,
    and replace it with the one in all_revise.
"""
import sys,re,codecs

class Lexdata(object):
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.H,self.L,self.key1,self.key2,self.lex) = re.split('\t',line)
  self.used=False # for later use
 def __repr__(self):
  vals = (self.H,self.L,self.key1,self.key2,self.lex)
  return '\t'.join(vals)

def init_lexdata(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Lexdata(x) for x in f if (not x.startswith(';'))]
 print len(recs),"Lexdata records read from",filein
 d = {}
 for rec in recs:
  d[rec.L] = rec
 return (recs,d)

if __name__ == "__main__":
 filein1 = sys.argv[1] # all.txt
 filein2 = sys.argv[2] # auxiliary/all_revise.txt
 if len(sys.argv) == 3:
  fileout = filein1
 else:
  fileout = sys.argv[3]
 print "writing output to",fileout
 (recs,d) = init_lexdata(filein1)
 (recsadj,dadj) = init_lexdata(filein2)
 fout = codecs.open(fileout,"w","utf-8")
 nadj = 0
 for rec in recs:
  L = rec.L
  if L in dadj:
   nadj = nadj + 1
   recadj = dadj[L]
   rec = recadj
  fout.write('%s\n' % rec)
 fout.close()
 print len(recs),"records written to",fileout
 print nadj,"of these records adjusted from",filein2
 
