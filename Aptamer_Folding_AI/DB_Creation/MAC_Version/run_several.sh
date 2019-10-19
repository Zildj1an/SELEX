# Parallel thread database training running
# $bash run_several.sh
# This part is mandatory to every opened terminal

export ROSETTA=/Users/Anuska/Desktop/rosetta_code/
export RNA_TOOLS=$ROSETTA/tools/rna_tools/
export PATH=$RNA_TOOLS/bin/:$PATH
export ROSETTA3=$ROSETTA/main/source/bin/
export PYTHONPATH=$PYTHONPATH:$RNA_TOOLS/bin/
source ~/.bashrc
python $RNA_TOOLS/sym_link.py

for i in $(seq 1 10)
do
    echo "Starting thread num " $i
    python3 Nemesis_AEGIS/DB_Creation/DB_Creation_Terminal.py $i &
done


