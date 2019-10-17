# IMPORTS 
from keras.utils.generic_utils import get_custom_objects
from keras.layers import Activation
from keras import backend as K
from pyrosetta import Pose, init, get_fa_scorefxn, pose_from_sequence
import os
import numpy as np
import csv

### STARTS ENVIRONMNETS
def starts_pyrosetta():
    # Starts pyrosetta environment
    init()
    # Defines the scoring function from rosetta
    scorefxn = get_fa_scorefxn()
    return scorefxn

def starts_Keras_environment():
    # Starts the Keras environment
    os.environ["KERAS_BACKEND"] = "tensorflow"  # Set Keras-Tensorflow environment
    K.set_image_dim_ordering("th") #(channels, rows, cols)


### SAVE PDBs AND CSVs FUNCTIONS
# Save the given sequence in a csv = 1 line contain: Sequence, Degrees and Score
def save_to_csv(seq, x, score, RESULTS_CSV, FIRST_TIME):
    headers = ("Sequence", "Degrees", "Score")
    table = [seq, x, score]
    if (FIRST_TIME == True):
        with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerow(table)
        FIRST_TIME = False
    else:
        with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(table)

# Save a pose in a pbd format
def create_pdb_and_save(pose, score, epoch, POSES_FOLDER):
    pose.dump_pdb(POSES_FOLDER+"pose_" +
                  str(epoch)+"_Scoring_"+str(score)+".pdb")

# Save the predicted figures (each x epochs) in a csv (per lines) 
def save_created_figures(epoch,my_generative,X_test, POSES_FOLDER, NUM_NUCLEOTIDES, RESULTS_CSV, FIRST_TIME, scorefxn):
    #noise = noise_nucleotides(1)
    idx = np.random.randint(0, X_test.shape[0], 1)
    X_test=X_test[idx]

    gen_img = my_generative.predict(X_test)
    pose_new = Pose()
    sequence = ""
    for no in range(0, NUM_NUCLEOTIDES):
        if X_test[0, 0, no] == 1:
            sequence = sequence+"A[ADE]"
        elif X_test[0, 1, no] == 1:
            sequence = sequence+"G[GUA]"
        elif X_test[0, 2, no] == 1:
            sequence = sequence+"C[CYT]"
        elif X_test[0, 3, no] == 1:
            sequence = sequence+"T[THY]"
    pose_new = pose_from_sequence(sequence)

    data=[]
    for k in range(0, NUM_NUCLEOTIDES):
        data.append(gen_img[0,0,k,0])
        pose_new.set_gamma(k+1, gen_img[0,0,k,0])
        data.append(gen_img[0,1,k,0])
        pose_new.set_epsilon(k+1, gen_img[0,1,k,0])
        data.append(gen_img[0,2,k,0])
        pose_new.set_delta(k+1, gen_img[0,2,k,0])
        data.append(gen_img[0,3,k,0])
        pose_new.set_chi(k+1, gen_img[0,3,k,0])
        data.append(gen_img[0,4,k,0])
        pose_new.set_zeta(k+1, gen_img[0,4,k,0])

    score = scorefxn(pose_new)
    save_to_csv(sequence, data, score, RESULTS_CSV, FIRST_TIME)
    create_pdb_and_save(pose_new, score, epoch, POSES_FOLDER)

### FUNCTION THAT MEASURES THE PERFORMANCE OF THE TRAIN 
# AND SAVES A RESULTS OF THE GENERATIVE NETWORK EACH SAMPLE_INTERVAL EPOCHS
def summarize_performance(epoch,X_test,Y_test,generative,discriminative, batch_size, POSES_FOLDER, NUM_NUCLEOTIDES, RESULTS_CSV, FIRST_TIME, scorefxn):
    fake = np.zeros((batch_size, 1))
    valid = np.ones((batch_size, 1))
    # Takes some test data and evaluate the discriminative network at this point (# epoch)
    idx = np.random.randint(0, X_test.shape[0], batch_size)
    sequences_DB = X_test[idx]
    degrees_DB = Y_test[idx]
    # For real data
    _, acc_real = discriminative.evaluate(x=[sequences_DB, degrees_DB],y=valid, verbose=0)
    # And wrong data
    degrees_GEN = generative.predict(sequences_DB)
    _, acc_fake = discriminative.evaluate(x=[sequences_DB, degrees_GEN],y=fake, verbose=0) 
    #Verbose=1 -> Progress bar

    # Summarize discriminator performance: 
    print(f"Accuracy real: {acc_real*100}% , fake: {acc_fake*100}%")
    save_created_figures(epoch=epoch,my_generative=generative,X_test=X_test, POSES_FOLDER=POSES_FOLDER, NUM_NUCLEOTIDES=NUM_NUCLEOTIDES, RESULTS_CSV=RESULTS_CSV, FIRST_TIME=FIRST_TIME, scorefxn=scorefxn)

### FUNCTION THAT EXTRACTS THE FINAL RESULTS
def extract_results(X_test, Z_test, generative, NUM_NUCLEOTIDES, FINAL_RESULTS_CSV, TYPE_NUCLEOTIDES, scorefxn):
    headers = ("Sequence", "Degrees", "Score DB", "Score Generated")
    with open(FINAL_RESULTS_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
    gen_imgs = generative.predict(X_test)
    for i in range(1,len(X_test)):
        pose_new = Pose()
        sequence = ""
        muestra = X_test[i]
        for no in range(0, NUM_NUCLEOTIDES):
            if muestra[0, no] == 1:
                sequence = sequence+"A[ADE]"
            elif muestra[1, no] == 1:
                sequence = sequence+"G[GUA]"
            elif muestra[2, no] == 1:
                sequence = sequence+"C[CYT]"
            elif muestra[3, no] == 1:
                sequence = sequence+"T[THY]"
        pose_new = pose_from_sequence(sequence)
        data=[]
        gen_img = gen_imgs[i]
        for k in range(0, NUM_NUCLEOTIDES):
            data.append(gen_img[0,k,0])
            pose_new.set_gamma(k+1, gen_img[0,k,0])
            data.append(gen_img[1,k,0])
            pose_new.set_epsilon(k+1, gen_img[1,k,0])
            data.append(gen_img[2,k,0])
            pose_new.set_delta(k+1, gen_img[2,k,0])
            data.append(gen_img[3,k,0])
            pose_new.set_chi(k+1, gen_img[3,k,0])
            data.append(gen_img[4,k,0])
            pose_new.set_zeta(k+1, gen_img[4,k,0])
        score = scorefxn(pose_new)
        table = [sequence, data, Z_test[i],score]
        with open(FINAL_RESULTS_CSV, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(table)

## ACTIVATION CUSTOM LAYER
# Custom layer: tanh * 360 degrees
def L_CUSTOM(x):
    act_Func = (K.sigmoid(x) * 360)
    # In order to save the ativation custom layer correctly in the networks (from 0 to 360 degrees)
    get_custom_objects().update({'L_CUSTOM': Activation(L_CUSTOM)})
    return act_Func