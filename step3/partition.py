""" partition.py  Feb 7, 2016
  Input is a finite, non-empty sequence x
  Output is a list of specialized partitions of x into its elements.
  Each element p of the list is a partition of x.  
  'p' is also represented as a list [p-0 ... p-k] where
  - each  p-j is a contiguous subsequence of x
     TODO
  - and if 0<=j1<j2<len(p), then all subscripts j1-i1 < j2-i2
  There is no 'natural' order relation between two partitions p and q of x.
  Example.
   One partition p of x has just one element [x[0] ... x[len(x)]] ,
    consisting of all the elements of x.
   Use the 'list' class to generate this
"""
import sys

def partition(x):
 #print "ENTER:x=",x,"len=",len(x)
 p = [x]
 ans = [p]
 #if len(x) <=1:
 # return ans
 # now for the 'proper' partitions of x
 for j in xrange(1,len(x)):
  p0 = x[0:j] # list of the first j elements of x
  qs = partition(x[j:]) # partitions of rest of list
  for q in qs:
   # q is a list. Put p0 at start
   q.insert(0, p0) 
   ans.append(q)
 #print "EXIT:x=",x,"ans=",ans
 return ans

if __name__ == "__main__":
 n = int(sys.argv[1])
 x = range(1,n+1)
 x = 'abcdefg'[0:n]
 p = partition(x)
 print "partitions of",x
 q = ['%s'%v for v in p]
 pstr=' : '.join(q)
 print "p=",pstr
 for i in xrange(0,len(p)):
  print i+1,p[i]

