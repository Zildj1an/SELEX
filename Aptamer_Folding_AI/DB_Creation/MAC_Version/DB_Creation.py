### IMPORTS

# VienaRNA
import RNA

# Numpy
import numpy as np

# Pandas
import csv

# Os
import os

# Pyrosetta
from pyrosetta import init, get_fa_scorefxn, pose_from_pdb
from pyrosetta.teaching import *
init()
scorefxn = get_fa_scorefxn()

# Time 
import time

### GLOBAL VARIABLES
# Change
NUM_NUCLEOTIDES = 50
RESULTS_CSV = "Carpeta_en_uso/database.csv"
ROSETA_FILES = "/Users/anuska/Desktop/IGEM/Rosetta/rosetta_src_code/"
NUM_STRUCTURES_PER_SEQUENCE = 100
NUM_STRUCTURES_IN_DATA_BASE = 10000
MINIMIZATION_RNA = "false" 

# No change
ADENINE = "a"
GUANINE = "g"
CITOSINE = "c"
TYMINE = "t"
URACIL = "u"
FIRST_TIME = True

### DEFINED FUNCTIONS
# FUNCTION THAT EXTRACT AND COMPILE ROSETTA AND RNA TOOLS
# os.system("export ROSETTA=%s " % (ROSETA_FILES))
# os.system("export RNA_TOOLS=$ROSETTA/tools/rna_tools/ ")
# os.system("export PATH=$RNA_TOOLS/bin/:$PATH ")
# os.system("export ROSETTA3=$ROSETTA/main/source/bin/ ")
# os.system("export PYTHONPATH=$PYTHONPATH:$RNA_TOOLS/bin/ ")
# os.system("source ~/.bashrc ")
# os.system("python $RNA_TOOLS/sym_link.py ")

# FUNCTIONS THAT CREATES A RANDOM DNA - ONE CHAIN
# Choose a,c,g or t randomly
def random_nucleotide():
    value = np.random.choice((1, 2, 3, 4))
    global ADENINE, GUANINE, CITOSINE, TYMINE
    if value == 1:
        return ADENINE
    elif value == 2:
        return GUANINE
    elif value == 3:
        return CITOSINE
    elif value == 4:
        return TYMINE

# creates a DNA chain with a number of NUM_NUCLEOTIDES
def noise_nucleotides():
    global NUM_NUCLEOTIDES
    noise = []
    for _ in range(0, NUM_NUCLEOTIDES):
        aux = random_nucleotide()
        noise.append(aux)
    return noise

# FUNCTIONS THAT PERFORM THE DNA/RNA CHANGES
# Performs the DNA to RNA change
def from_DNA_to_RNA(noise):
    noise_copy=noise
    global NUM_NUCLEOTIDES, TYMINE
    for i in range(0, NUM_NUCLEOTIDES):
        if noise_copy[i] == TYMINE:
            noise_copy[i] = URACIL
    return noise_copy

# Performs the RNA to DNA change
def from_RNA_to_DNA(atomes):  # (Lyon Igem code)
    output = []
    #i = 0
    for atome in atomes:
        #i += 1
        #print("hola %s %s" % (i, atome))
        # Lyon's code solution:
        if (atome == "\n"):
            break
        if not("O2'" in atome):
            if (atome[-5] == "H" or atome[-4] == "H") and ("U" in atome) and ("H5 " in atome):
                line = atome.split("   ")
                line[1] = line[1][:-2] + "C7"
                line[-1] = "  C \n"
                atome = "   ".join(line)
            if "U" in atome:
                atome = atome[:19]+"T"+atome[20:]
        output.append(atome)
    return output

# INPUT-OUTPUT FUNCTIONS (FROM FILES)
# Saving FASTA in txt
def save_pose_in_FASTA_format(seq_A):
    with open("aptamer.txt", "w") as Myfile:
        Myfile.write(">" + "aptamer" + "\n" + seq_A + "\n")

# Saving secondary structure in txt
def save_secondary_structure(secondary_structure):
    with open("aptamer_sec.txt", "w") as Myfile:
        Myfile.writelines(secondary_structure)

# Extract the atomes from the pose saved in PDB format
def extract_atomes_from_PDB():
    with open("S_000001_prueba_0001.pdb", "r") as file_pdb:
        atomes = file_pdb.readlines()
    return atomes

# Save DNA to PDB format
def save_DNA_to_PDB(output):
    with open("DNA_aptamer.pdb", "w") as file_pdb:
        file_pdb.writelines(output)
    new_pose = pose_from_pdb("DNA_aptamer.pdb")
    return new_pose

# Remove the unused files
def remove_unused_files():
    os.system("rm my_rna_structures.out")
    os.system("rm aptamer_sec.txt")
    os.system("rm aptamer.txt")
    os.system("rm S_000001_prueba_0001.pdb")
    os.system("rm DNA_aptamer.pdb")
    os.system("rm aptamer_best.out")
    os.system("rm default.sc")

# FUNCTIONS THAT SAVES THE DATA INTO CSV
# Extracts the angles from pose, opens csv and save: Save the given sequence in a csv
def save_to_csv(seq, x, score):
    headers = ("Sequence", "Degrees", "Score")
    table = [seq, x, score]
    global FIRST_TIME, RESULTS_CSV
    if (FIRST_TIME == True):
        with open(RESULTS_CSV, "w", newline = "", encoding = "utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerow(table)
        FIRST_TIME = False
    else:
        with open(RESULTS_CSV, "a", newline = "", encoding = "utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(table)

# Save the poses in a csv (per lines)
def save_poses_in_a_csv(pose, seq):
    global NUM_NUCLEOTIDES, ADENINE, GUANINE, TYMINE, CITOSINE, URACIL
    gen_img = []
    for k in range(0, NUM_NUCLEOTIDES):
        gen_img.append(pose.gamma(k+1))
        gen_img.append(pose.epsilon(k+1))
        gen_img.append(pose.delta(k+1))
        gen_img.append(pose.chi(k+1))
        gen_img.append(pose.zeta(k+1))
    print(gen_img)
    sequence = []
    for s in range(0, NUM_NUCLEOTIDES):
        if seq[s] == ADENINE:
            sequence.append("A[ADE]")
        elif seq[s] == GUANINE:
            sequence.append("G[GUA]")
        elif seq[s] == CITOSINE:
            sequence.append("C[CYT]")
        elif seq[s] == TYMINE or seq[s] == URACIL:
            sequence.append("T[THY]")
    print(sequence)
    my_seq = "".join(sequence)
    score = scorefxn(pose)
    save_to_csv(my_seq, gen_img, score)

### FOR LOOP

t = time.time()

for _ in range(0, NUM_STRUCTURES_IN_DATA_BASE):
    # Create DNA chain
    noise = noise_nucleotides()
    # Transform to RNA
    rna = from_DNA_to_RNA(noise)
    seq_A = "".join(rna)
    # Compute secondary structure
    (secondary_structure, _) = RNA.fold(seq_A)
    # Save FASTA amd Secondary strcuture
    save_pose_in_FASTA_format(seq_A)
    save_secondary_structure(secondary_structure)
    # Configure and preform the folding in a Rosetta's protocol
    os.system("$ROSETTA3/rna_denovo.default.macosclangrelease -fasta aptamer.txt -nstruct %s -minimize_rna %s -secstruct_file aptamer_sec.txt -out::file::silent my_rna_structures.out" % (NUM_STRUCTURES_PER_SEQUENCE,MINIMIZATION_RNA))
    # Minimize and extract the best one
    os.system("$RNA_TOOLS/silent_util/silent_file_sort_and_select.py my_rna_structures.out -select 1 -o aptamer_best.out")
    # To PDB in a Rosetta's protocol
    os.system("$ROSETTA3/score.default.macosclangrelease -in:file:silent aptamer_best.out -in::file::fullatom -out:suffix _prueba -out:output")
    # Extract pose from PDB
    atomes = extract_atomes_from_PDB()
    # Performns the RNA to DNA change
    output = from_RNA_to_DNA(atomes)
    # Saves the DNA into PDB format and extrat the pose
    new_pose = save_DNA_to_PDB(output)
    # Remove unused files
    remove_unused_files()
    # Save the pose, the sequence and the scoring in the csv
    save_poses_in_a_csv(new_pose, noise)
    
print("The data base has been created")
elapsed = time.time() - t
print("Elapsed time %d"%(elapsed))
