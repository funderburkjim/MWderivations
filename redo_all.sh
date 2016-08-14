echo "step2 now considered obsolete."
echo "---------------------------------------"
echo "recomputing step3"
echo "---------------------------------------"
cd step3
#echo "ASSUMING YOU HAVE DONE redo_datasources.sh, or the equivalent"
sh redo.sh
echo "---------------------------------------"
echo "recomputing step4"
echo "---------------------------------------"
cd ../step4
sh redo.sh > redo_log.txt
echo "check output step4/redo_log.txt "
