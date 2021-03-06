
This readme.md provides an overview of the computations and results. 

## Independently derived data sources:
* lexnorm-all.txt
* mw.xml
* verb_step0a.txt
* icf.txt
* wsfx.txt 

## redo.sh reconstructs everything
* allnom.txt  (198467) normalize key2
* mw.extract.txt (202645) all non-repetitive records from mw, with only few fields
* all.txt  same lines as mw_extract, with allnom data where applicable
* analysis.txt  This is the end result of computations.

All files contain lines with fields of tab-delimited data, and each line
corresponds to a certain record of the digitization mw.xml of Monier-Williams
dictionary.

The fields of analysis.txt are:
* H-code (without the initial 'H')
* L-number
* key1
* key2 (normalized)
* 'lex'  For records from allnom.txt, this is the simplified lexical information
  For the non-substantive records (not in allnom.txt), it may contain
  VERB (for verbs, with several subcategories),
  ICF  (headwords identified as 'In Compound For')
  SEE  (headwords marked as <cf type="see"> in MW
  NONE (currently unclassified headwords).
* analysis  
  For analyzed Substantives, a form similar to key2 which summarizes the derivation)
  For unanalyzed substantives and for non-substantives, this field contains the
   empty string
* status 
  NTD  Nothing To Do.  Applied to non-substantives
  DONE For substantives, indicates that the analysis has succeeded
  TODO For substantives, indicates that the analysis has not succeeded.
* note
  A keyword indicating the last step of the analysis that was applied.
  For some analyses (such as wsfx), there is some additional information
  The list of these keywords is currently:
  * init  Initialize analysis.txt from all.txt
  * noparts  Substantives with no 'part' information in the normalized key2
             There is no further analysis of these
  * wsfx  Word is explainable as the addition of a secondary suffix to the
          parent headword
  * cpd1  Word is explainable as a two-part compound based on the parent headword
  * srs1  Word is explainable as a two-part compound based on the parent headword, with a simple vowel sandhi.
  * pfx1  Word is explainable as a prefix plus a known substantive headword
  * wsfx1 Word is explainable as the addition of a secondary suffix to 
          some non-parental headword
  * gender Word is explainable as the feminine form of a previous sibling headword.

Current success rate:
 Out of the 198467 substantives (from allnom.txt), there remain 30818 
 records to be explained; i.e., 85.5 % of the cases have an explanation.
 These 30818 records are identified as those marked 'TODO'.
 The statistical distribution of the classification can be seen at the
 end (starting with last analysis step 'gender') in analysis_log.txt file.

For some additional procedural discussion, consult the
readme_procedure.org file.
