date
echo "remake allnom.txt"
python normkey2.py ../../mwxml/mw.xml lexnorm-all.txt allnom.txt
echo "remake mw_extract.txt"
python mw_extract.py ../../mwxml/mw.xml auxiliary/mw_extract.txt
echo "remake all.txt"
python merge.py auxiliary/mw_extract.txt allnom.txt auxiliary/verb_step0a.txt auxiliary/icf.txt all.txt
echo "Reconstruct analysis.txt"
sh analysis.sh > analysis_log.txt
echo "redo.sh is finished"
date
