echo "Initialize analysis.txt from all.txt"
python analysis.py init all.txt analysis.txt
echo "identify 'noparts' substantives"
python analysis.py noparts analysis.txt
echo "identify taddhita 'compounds'"
python analysis.py wsfx analysis.txt
echo "identify samAsa compounds"
python analysis.py cpd1 analysis.txt
echo "simple replacement sandhi compounds"
python analysis.py srs1 analysis.txt
echo "HxB records derived by gender"
python analysis.py gender analysis.txt
echo "identify samAsa compounds, with sandhi"
python analysis.py cpd2 analysis.txt
echo "identify nan-tatpurusha compounds"
python analysis.py cpd_nan analysis.txt
echo "compounds with complex second parts"
python analysis.py cpd3 analysis.txt
echo "HxC inflected forms"
python analysis.py inflected analysis.txt
echo "prefix forms"
python analysis.py pfx1 analysis.txt
echo "cpd1a"
python analysis.py cpd1a analysis.txt
echo "pfx2"
python analysis.py pfx2 analysis.txt
