### IMPORTS
# VienaRNA
import RNA

# Numpy
import numpy as np

# Check file exists
from pathlib import Path

# Pandas
import csv

# Threads
import threading
from threading import Thread

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
RESULTS_CSV = "Carpeta_en_uso/database"
ROSETA_FILES = "/Users/anuska/Desktop/IGEM/Rosetta/rosetta_src_code/"
NUM_STRUCTURES_PER_SEQUENCE = 100
NUM_STRUCTURES_IN_DATA_BASE = 10000
MINIMIZATION_RNA = "false"
THREADS = 4

# No change
ADENINE = "a"
GUANINE = "g"
CITOSINE = "c"
TYMINE = "t"
URACIL = "u"

### DEFINED FUNCTIONS
# FUNCTION THAT EXTRACT AND COMPILE ROSETTA AND RNA TOOLS
# os.system("export ROSETTA=%s " % (ROSETA_FILES))
# os.system("export RNA_TOOLS=$ROSETTA/tools/rna_tools/ ")
# os.system("export PATH=$RNA_TOOLS/bin/:$PATH ")
# os.system("export ROSETTA3=$ROSETTA/main/source/bin/ ")
# os.system("export PYTHONPATH=$PYTHONPATH:$RNA_TOOLS/bin/ ")
# os.system("source ~/.bashrc ")
# os.system("python $RNA_TOOLS/sym_link.py ")
# Console: export ROSETTA=/Users/anuska/Desktop/IGEM/Rosetta/rosetta_src_code/ ; export RNA_TOOLS=$ROSETTA/tools/rna_tools/ ; export PATH=$RNA_TOOLS/bin/:$PATH ; export ROSETTA3=$ROSETTA/main/source/bin/ ; export PYTHONPATH=$PYTHONPATH:$RNA_TOOLS/bin/ ; source ~/.bashrc ; python $RNA_TOOLS/sym_link.py

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

# Creates a DNA chain with a number of NUM_NUCLEOTIDES
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
    noise_copy = noise
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
def save_pose_in_FASTA_format(seq_A, file_Name):
    with open("aptamer"+file_Name+".txt", "w") as Myfile:
        Myfile.write(">" + "aptamer" + "\n" + seq_A + "\n")

# Saving secondary structure in txt
def save_secondary_structure(secondary_structure, file_Name):
    with open("aptamer_sec"+file_Name+".txt", "w") as Myfile:
        Myfile.writelines(secondary_structure)

# Extract the atomes from the pose saved in PDB format
def extract_atomes_from_PDB(file_Name):
    with open("S_000001_"+file_Name+"_0001.pdb", "r") as file_pdb:
        atomes = file_pdb.readlines()
    return atomes

# Save DNA to PDB format
def save_DNA_to_PDB(output, file_Name):
    with open("DNA_aptamer"+file_Name+".pdb", "w") as file_pdb:
        file_pdb.writelines(output)
    new_pose = pose_from_pdb("DNA_aptamer"+file_Name+".pdb")
    return new_pose

# Remove the unused files
def remove_unused_files(file_Name):
    os.system("rm my_rna_structures"+file_Name+".out")
    os.system("rm aptamer_sec"+file_Name+".txt")
    os.system("rm aptamer"+file_Name+".txt")
    os.system("rm S_000001_"+file_Name+"_0001.pdb")
    os.system("rm DNA_aptamer"+file_Name+".pdb")
    os.system("rm aptamer_best"+file_Name+".out")
    os.system("rm default"+file_Name+".sc")

# FUNCTIONS THAT SAVES THE DATA INTO CSV
# Extracts the angles from pose, opens csv and save: Save the given sequence in a csv
def save_to_csv(seq, x, score, file_Name):
    table = [seq, x, score]
    file_Name_csv = RESULTS_CSV + file_Name + ".csv"
    with open(file_Name_csv, "a", newline = "", encoding = "utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(table)

# Save the poses in a csv (per lines)
def save_poses_in_a_csv(pose, seq, file_Name):
    global NUM_NUCLEOTIDES, ADENINE, GUANINE, TYMINE, CITOSINE
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
    save_to_csv(my_seq, gen_img, score, file_Name)

### FOR LOOP
# Main loop that call all the fucntions, used by the threads
def for_loop_that_creates_csv(file_Name):
    for _ in range(0, NUM_STRUCTURES_IN_DATA_BASE):
        # Create DNA chain
        noise = noise_nucleotides()
        # Transform to RNA
        rna = from_DNA_to_RNA(noise)
        seq_A = "".join(rna)
        # Compute secondary structure
        (secondary_structure, _) = RNA.fold(seq_A)
        # Save FASTA amd Secondary strcuture
        save_pose_in_FASTA_format(seq_A, file_Name)
        save_secondary_structure(secondary_structure, file_Name)
        # Configure and preform the folding in a Rosetta's protocol
        os.system("$ROSETTA3/rna_denovo.default.linuxgccrelease -fasta aptamer%s.txt -nstruct %s -minimize_rna %s -secstruct_file aptamer_sec%s.txt -out::file::silent my_rna_structures%s.out" %(file_Name, NUM_STRUCTURES_PER_SEQUENCE, MINIMIZATION_RNA, file_Name, file_Name))
        # Minimize and extract the best one
        os.system("$RNA_TOOLS/silent_util/silent_file_sort_and_select.py my_rna_structures%s.out -select 1 -o aptamer_best%s.out" % (file_Name, file_Name))
        # To PDB in a Rosetta's protocol
        os.system("$ROSETTA3/score.default.linuxgccrelease -in:file:silent aptamer_best%s.out -in::file::fullatom -out:suffix _%s -out:output -out:file:scorefile default%s.sc" % (file_Name, file_Name,file_Name))
        # Extract pose from PDB
        atomes = extract_atomes_from_PDB(file_Name)
        # Performns the RNA to DNA change
        output = from_RNA_to_DNA(atomes)
        # Saves the DNA into PDB format and extrat the pose
        new_pose = save_DNA_to_PDB(output, file_Name)
        # Remove unused files
        remove_unused_files(file_Name)
        # Save the pose, the sequence and the scoring in the csv
        save_poses_in_a_csv(new_pose, noise, file_Name)

### THREADS PART
# Initialize threads and start them
t = time.time()  # Measure the used time
threads = []
my_t = None
for thread_csv in range(0, THREADS):
    my_t = Thread(target = for_loop_that_creates_csv, args = (str(thread_csv),))
    threads.append(my_t)
for my_t in range(0, THREADS):   
    threads[my_t].start()

# Create final database

headers = ("Sequence", "Degrees", "Score")
# Cretaes database headers if it does not exist
database = Path(RESULTS_CSV + ".csv")
if not (database.is_file() == 1):
    with open(RESULTS_CSV + ".csv", "w", newline = "", encoding = "utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

# Concatenate and Synchronize the threads
for thread_csv in range(0, THREADS):
    threads[thread_csv].join()
    os.system("cat " + RESULTS_CSV + str(thread_csv) + ".csv" + " >> " + RESULTS_CSV + ".csv")
    os.system("rm "+ RESULTS_CSV + str(thread_csv) +".csv")

# Communicate to the user that the database has been created
print("The data base has been created")
elapsed = time.time() - t
print("Elapsed time %d" % (elapsed))
