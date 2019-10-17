# Parallel thread database training running
# $bash run_several.sh
# This part is mandatory to every opened terminal

export ROSETTA=/home/carlos/Escritorio/IGEM/Cosasinstaladas/rosetta_bin_linux_2018.33.60351_bundle/
export RNA_TOOLS=$ROSETTA/tools/rna_tools/
export PATH=$RNA_TOOLS/bin/:$PATH
export ROSETTA3=$ROSETTA/main/source/bin/
export PYTHONPATH=$PYTHONPATH:$RNA_TOOLS/bin/
source ~/.bashrc
python $RNA_TOOLS/sym_link.py

for i in $(seq 1 1)
do
    echo "Starting thread num " $i
    python3 Nemesis_AEGIS/DB_Creation/DB_Creation_Terminal.py $i &
done


