# !pip3 install tensorflow==1.9.0
# !pip3 install imblearn
# !pip3 install pyrosetta
# !pip3 install pandas

### Needed IMPORTS: 
# Numpy
# Pandas
# Pyrosetta
# Sklearn
from sklearn.model_selection import train_test_split


# From the "Functions" folder:
from Functions.Load_database import read_data_and_split_into_Degrees_Sequence_and_Scoring, reshape_degrees_360, reshape_scoring, reshape_sequence
from Functions.GAN_network import build_mygan
from Functions.Discriminative_network import build_my_discriminator
from Functions.Generative_network import build_my_generator
from Functions.Train_function import train
from Functions.Load_network_functions import load_D, load_G, load_gan
from Functions.Save_networks_functions import save_D, save_G, save_gan
from Functions.Aux_train_functions import extract_results, L_CUSTOM, starts_Keras_environment, starts_pyrosetta

### GLOBAL VARIABLES
#Folders
RESULTS_CSV = "Carpeta_en_uso/resultado.csv"
FINAL_RESULTS_CSV = "Carpeta_en_uso/final_results.csv"
DATA_BASE_CSV = "Carpeta_en_uso/database.csv"
POSES_FOLDER = "Carpeta_en_uso/"

#Data
NUM_NUCLEOTIDES = 50
TYPE_NUCLEOTIDES = 4
NUM_ANGLES = 5

# Fit model
EPOCHS = 20
BATCH_SIZE = 100
SAMPLE_INTERVAL = 1

# Starts KERAS and Pyrosetta environmnets
scorefxn = starts_pyrosetta()
starts_Keras_environment()

# Read the csv and split the data into X(sequences), y (degrees) and z(scoring)
sequence,degrees,scoring = read_data_and_split_into_Degrees_Sequence_and_Scoring(DATA_BASE_CSV=DATA_BASE_CSV)
# CHANNELS ORDER:
# Degrees: gamma, epsilon, delta, chi and zeta
# Nucleiotides: A, G, C and T

# Reshape the information in order to be readable by the networks:
scoring_reshaped = reshape_scoring(scoring=scoring)
#print(scoring_reshaped.shape) = (NUM_VALUES_DB,1)
degrees_reshaped=reshape_degrees_360(degrees=degrees, NUM_NUCLEOTIDES=NUM_NUCLEOTIDES, NUM_ANGLES=NUM_ANGLES)
#print(degrees_reshaped.shape) = (NUM_VALUES_DB,5,50)
sequence_reshaped=reshape_sequence(sequence=sequence, NUM_NUCLEOTIDES=NUM_NUCLEOTIDES, TYPE_NUCLEOTIDES=TYPE_NUCLEOTIDES)
#print(sequence_reshaped.shape) = (NUM_VALUES_DB,4,50)

#With the X and y construct 2 groups= train and test groups
X_train, X_test, Y_train, Y_test, Z_train, Z_test  = train_test_split(sequence_reshaped,degrees_reshaped, scoring_reshaped, test_size=0.1)

# Constructs the generator
my_generator = build_my_generator(NUM_NUCLEOTIDES=NUM_NUCLEOTIDES, TYPE_NUCLEOTIDES=TYPE_NUCLEOTIDES, NUM_ANGLES=NUM_ANGLES)
my_generator.summary()
## From (BATCH_SIZE, 4, 50, 1) to (BATCH_SIZE, 5, 50, 1)

# Constructs the discriminator
my_discriminator = build_my_discriminator(NUM_NUCLEOTIDES=NUM_NUCLEOTIDES, TYPE_NUCLEOTIDES=TYPE_NUCLEOTIDES, NUM_ANGLES=NUM_ANGLES)
my_discriminator.summary()

#Constructs the GAN model
my_gan = build_mygan(generator=my_generator, discriminator=my_discriminator, TYPE_NUCLEOTIDES=TYPE_NUCLEOTIDES, NUM_NUCLEOTIDES=NUM_NUCLEOTIDES)
my_gan.summary()

# Train the network with train group
train(X_train=X_train, Y_train=Y_train, X_test=X_test, Y_test=Y_test, generative=my_generator, discriminative=my_discriminator, GAN=my_gan, POSES_FOLDER=POSES_FOLDER, epochs=EPOCHS, batch_size=BATCH_SIZE, sample_interval=SAMPLE_INTERVAL, BATCH_SIZE=BATCH_SIZE, NUM_NUCLEOTIDES=NUM_NUCLEOTIDES, RESULTS_CSV=RESULTS_CSV, scorefxn=scorefxn)
# Estract the results with test group
extract_results(X_test=X_test,Z_test=Z_test,generative=my_generator, NUM_NUCLEOTIDES=NUM_NUCLEOTIDES, FINAL_RESULTS_CSV=FINAL_RESULTS_CSV, TYPE_NUCLEOTIDES=TYPE_NUCLEOTIDES, scorefxn=scorefxn)

# Save models
save_gan(my_gan=my_gan, POSES_FOLDER=POSES_FOLDER)
save_D(my_discriminator=my_discriminator, POSES_FOLDER=POSES_FOLDER)
save_G(my_generator=my_generator, POSES_FOLDER=POSES_FOLDER)

# Load models
new_gan = load_gan(POSES_FOLDER=POSES_FOLDER)
my_generator_new = load_G(POSES_FOLDER=POSES_FOLDER)
my_discriminator_new = load_D(POSES_FOLDER=POSES_FOLDER)