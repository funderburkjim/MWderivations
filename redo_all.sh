echo "step2 now considered obsolete."
echo "recomputing step3"
cd step3
#echo "ASSUMING YOU HAVE DONE redo_datasources.sh, or the equivalent"
sh redo.sh
cd ../step4
sh redo.sh
