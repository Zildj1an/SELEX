# install ViennaRNA-2.4.13
# conda install -c bioconda viennarna
# conda install -c conda-forge bash

# IMPORTS
# ViennaRNA
import RNA

# Os
import os

# Numpy
import numpy as np

# CSV
import csv

# Pyrosetta
from pyrosetta import init, get_fa_scorefxn, pose_from_sequence, pose_from_pdb
from pyrosetta.teaching import *
init()
scorefxn = get_fa_scorefxn()

# GLOBAL VARIABLES
# Change
NUM_NUCLEOTIDES = 50
RESULTS_CSV = "Carpeta_en_uso/database.csv"
ROSETA_FILES = "/Users/anuska/Desktop/IGEM/Rosetta/rosetta_src_code/"
NUM_STRUCTURES_PER_SEQUENCE = 100

# No change
ADENINE = "a"
GUANINE = "g"
CITOSINE = "c"
TYMINE = "t"
URACIL = "u"
FIRST_TIME = False

# FUNCTION THAT CREATES A RANDOM DNA - ONE CHAIN
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

# Perform the DNA to RNA change
def from_DNA_to_RNA(noise):
    global NUM_NUCLEOTIDES, TYMINE
    for i in range(0, NUM_NUCLEOTIDES):
        if noise[i] == TYMINE:
            noise[i] = URACIL
    return noise

# Creates a doiuble RNA (NOT used now)
def RNAby2(rna):
    chainB = []
    global NUM_NUCLEOTIDES, ADENINE, GUANINE, URACIL, CITOSINE
    for i in range(0, NUM_NUCLEOTIDES):
        if rna[i] == ADENINE:
            chainB.append(CITOSINE)
        elif rna[i] == CITOSINE:
            chainB.append(ADENINE)
        elif rna[i] == URACIL:
            chainB.append(GUANINE)
        elif rna[i] == GUANINE:
            chainB.append(URACIL)
    return chainB[::-1]

# Create DNA chain
noise = noise_nucleotides()
# Transform to RNA
rna = from_DNA_to_RNA(noise)
seq_A = "".join(rna)

# SECONDARY STRUCTURE FROM RNA
# compute minimum free energy (MFE) and corresponding structure
(secondary_structure, mfe) = RNA.fold(seq_A)

# print output
print("Structure: %s \nMinimum free energy: %f " % (secondary_structure, mfe))

# Saving FASTA and dtb formats in txt
with open("aptamer.txt", "w") as Myfile:
    Myfile.write(">" + "aptamer" + "\n" + seq_A + "\n")
with open("aptamer_sec.txt", "w") as Myfile:
    Myfile.writelines(secondary_structure)

# PERFORM THE 3D FOLDING OF RNA
# export and configure Roseatta RNA_TOOLS
os.system("export ROSETTA=%s"%(ROSETA_FILES))
os.system("export RNA_TOOLS=$ROSETTA/tools/rna_tools/")
os.system("export PATH=$RNA_TOOLS/bin/:$PATH")
os.system("export ROSETTA3=$ROSETTA/main/source/bin/")
os.system("export PYTHONPATH=$PYTHONPATH:$RNA_TOOLS/bin/")
os.system("source ~/.bashrc")
os.system("python $RNA_TOOLS/sym_link.py")

# Configure and preform the folding in a Rosetta's protocol
os.system("$ROSETTA3/rna_denovo.default.macosclangrelease -fasta aptamer.txt -nstruct %s -minimize_rna -secstruct_file aptamer_sec.txt -out::file::silent my_rna_structures.out"%(NUM_STRUCTURES_PER_SEQUENCE))
# Minimize and extract the best one
os.system("$RNA_TOOLS/silent_util/silent_file_sort_and_select.py my_rna_structures.out -select 1 -o aptamer_best.out")
# To PDB in a Rosetta's protocol
os.system("$ROSETTA3/score.default.macosclangrelease -in:file:silent aptamer_best.out -in::file::fullatom -out:output")

# PERFORM THE RNA TO DNA TRANSFORMATION
# From RNA to DNA
with open("S_000001_0001.pdb", "r") as file_pdb:
    atomes = file_pdb.readlines()

# (Lyon Igem code)
def from_RNA_to_DNA(atomes):
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

output = from_RNA_to_DNA(atomes)
# Save DNA
with open("DNA_aptamer.pdb", "w") as file_pdb:
    file_pdb.writelines(output)

# Extract pose from DNA in PDB format
new_pose = pose_from_pdb("DNA_aptamer.pdb")

# Scoring
pose = pose_from_sequence(seq_A)
scoring_2 = scorefxn(new_pose)
scoring_1 = scorefxn(pose)
print(scoring_1)
print(scoring_2)

# SAVE THE DNA TO CSV
# Remove the unused files
os.system("rm my_rna_structures.out")
os.system("rm aptamer_sec.txt")
os.system("rm aptamer.txt")
os.system("rm S_000001_0001.pdb")
#os.system("rm DNA_aptamer.pdb")
os.system("rm aptamer_best.out")
os.system("rm default.sc")

# Extract the angles from pose
# Open csv and save: Save the given sequence in a csv
# First line contain: Sequence, Degrees and Score
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
    global NUM_NUCLEOTIDES, ADENINE, GUANINE, TYMINE, CITOSINE
    gen_img = []
    for k in range(0, NUM_NUCLEOTIDES):
        gen_img.append(pose.gamma(k+1))
        gen_img.append(pose.epsilon(k+1))
        gen_img.append(pose.zeta(k+1))
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

save_poses_in_a_csv(new_pose, seq_A)
