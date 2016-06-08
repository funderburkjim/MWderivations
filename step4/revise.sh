echo "Revising all.txt"
python all_revise.py all.txt auxiliary/all_revise.txt
#sh redo_analysis.sh
echo "redoing analysis2.txt"
python analysis2.py all all.txt analysis2.txt
