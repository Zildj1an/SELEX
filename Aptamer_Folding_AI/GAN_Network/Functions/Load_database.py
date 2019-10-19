import pandas as pd
import numpy as np

# CHANNELS ORDER:
# Degrees: gamma, epsilon, delta, chi and zeta
# Nucleiotides: A, G, C and T

### LOADING FUNCTIONS FROM DATABASE
# Read the csv and split the data into X(sequences) and y (scoring)

def read_data_and_split_into_Degrees_Sequence_and_Scoring(DATA_BASE_CSV):
    df = pd.read_csv(DATA_BASE_CSV)
    df.head()
    deg = df["Degrees"].values
    sco = df["Score"].values
    seq = df["Sequence"].values
    return seq, deg,sco


def reshape_degrees(degrees, NUM_NUCLEOTIDES, NUM_ANGLES):
    new_array=[]
    for i in range(0,len(degrees)):
        sentence =degrees[i]
        aux = sentence.split(',')
        aux[0] = aux[0].replace("["," ")
        aux[249] = aux[249].replace("]"," ")
        my_array=[]
        for item in aux:
            my_array.append(float(item))
        gamma=[]
        epsilon=[]
        delta=[]
        chi=[]
        zeta=[]
        j=0
        while j<((NUM_ANGLES*NUM_NUCLEOTIDES)-1):
            gamma.append(my_array[j])
            j=j+1
            epsilon.append(my_array[j])
            j=j+1
            delta.append(my_array[j])
            j=j+1
            chi.append(my_array[j])
            j=j+1
            zeta.append(my_array[j])
            j=j+1
        new_array.append([gamma,epsilon,delta,chi,zeta])
    reshape_array=np.asarray(new_array)
    return reshape_array.reshape((len(degrees),NUM_ANGLES,NUM_NUCLEOTIDES,1))

# In order to transform all the angles to positive numbers
def reshape_degrees_360(degrees, NUM_NUCLEOTIDES, NUM_ANGLES):
    new_array=[]
    for i in range(0,len(degrees)):
        sentence =degrees[i]
        aux = sentence.split(',')
        aux[0] = aux[0].replace("["," ")
        aux[249] = aux[249].replace("]"," ")
        my_array=[]
        for item in aux:
            my_array.append(float(item))
        gamma=[]
        epsilon=[]
        delta=[]
        chi=[]
        zeta=[]
        j=0
        while j<((NUM_ANGLES*NUM_NUCLEOTIDES)-1):
            if my_array[j] > 0:
                gamma.append(my_array[j])
            else:
                gamma.append(my_array[j]+360)
            j=j+1
            if my_array[j] > 0:
                epsilon.append(my_array[j])
            else:
                epsilon.append(my_array[j]+360)
            j=j+1
            if my_array[j] > 0:
                delta.append(my_array[j])
            else:
                delta.append(my_array[j]+360)
            j=j+1
            if my_array[j] > 0:
                chi.append(my_array[j])
            else:
                chi.append(my_array[j]+360)
            j=j+1
            if my_array[j] > 0:
                zeta.append(my_array[j])
            else:
                zeta.append(my_array[j]+360)
            j=j+1
        new_array.append([gamma,epsilon,delta,chi,zeta])
    reshape_array=np.asarray(new_array)
    return reshape_array.reshape((len(degrees),NUM_ANGLES,NUM_NUCLEOTIDES,1))

def reshape_sequence(sequence, NUM_NUCLEOTIDES, TYPE_NUCLEOTIDES):
    new_array=[]
    for i in range(0,len(sequence)):
        sentence =sequence[i]
        sentence=sentence.split("]")
        aux=np.asarray(sentence)
        noise=np.zeros([TYPE_NUCLEOTIDES,NUM_NUCLEOTIDES])
        j=0
        while j<(NUM_NUCLEOTIDES):
            if aux[j]=="A[ADE":
                noise[0,j]=1
            elif aux[j]=="G[GUA":
                noise[1,j]=1
            elif aux[j]=="C[CYT":
                noise[2,j]=1
            elif aux[j]=="T[THY":
                noise[3,j]=1
            j=j+1
        new_array.append(noise)
    reshape_array=np.asarray(new_array)
    return reshape_array.reshape((len(sequence),TYPE_NUCLEOTIDES,NUM_NUCLEOTIDES,1))

def reshape_scoring(scoring):
    new_array=[]
    for i in range(0,len(scoring)):
        score = scoring[i]
        aux=np.asarray(score)
        new_array.append(aux)
    reshape_array = np.asarray(new_array)
    return reshape_array.reshape((len(scoring),1))