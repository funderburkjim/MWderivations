echo "create allnom.txt"
python normkey2.py ../../mwxml/mw.xml ../../MWlexnorm/step1b/lexnorm-all.txt allnom.txt
echo "NO longer copying verb_step0a.txt"
#cp ../../MWvlex/step0/verb_step0a.txt .
echo "Creating icf.txt from icf_prep1.txt"
python init_icf.py auxiliary/icf_prep1.txt auxiliary/icf.txt
echo "create mw_extract.txt from mw.xml"
python mw_extract.py ../../mwxml/mw.xml auxiliary/mw_extract.txt
echo "merge files into all.txt"ellison~1918
#python merge.py auxiliary/mw_extract.txt allnom.txt auxiliary/verb_step0a.txt auxiliary/icf.txt all.txt > all_log.txt
python merge.py auxiliary/mw_extract.txt allnom.txt ../../MWvlex/step0/verb_step0a.txt auxiliary/icf.txt all.txt > all_log.txt
#sh redo_analysis.sh
echo "redoing analysis2.txt"
python analysis2.py all all.txt analysis2.txt

