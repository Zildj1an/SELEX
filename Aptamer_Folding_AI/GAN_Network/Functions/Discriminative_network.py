# IMPORTS 
from keras.layers import Input, BatchNormalization, Dense, MaxPooling2D, Dropout, Flatten, Conv2D, concatenate
from keras.models import Model
from keras.optimizers import SGD
from Aux_train_functions import L_CUSTOM


# GLOBAL VARIABLES
#Discriminative network
NUM_FILTERS_SEQ = 50
NUM_FILTERS_STRUCT = 50
NUM_HIDDEN_SEQ = 20
NUM_HIDDEN_STRUCT = 20
NUM_HIDDEN_COMMON = 1
KERNEL_SIZES_SEQ = (2,1)
KERNEL_SIZES_STRUCT = (2,1)

#Optimizer Discriminative
LEARNING_RATE_D = 0.9
MOMENTUM_D = 0.9
DECAY_D = 0.0
DROPOUT_D = 0.5


### DISCRIMINATOR
# Creates the discriminator model
# It has 2 inputs and one output
def build_my_discriminator(NUM_NUCLEOTIDES, TYPE_NUCLEOTIDES, NUM_ANGLES):

    global NUM_FILTERS_SEQ, NUM_FILTERS_STRUCT, NUM_HIDDEN_SEQ, NUM_HIDDEN_STRUCT, NUM_HIDDEN_COMMON, KERNEL_SIZES_SEQ, KERNEL_SIZES_STRUCT, LEARNING_RATE_D, MOMENTUM_D, DECAY_D
    # It has 2 inputs -> 2 networks that are joint after
    
    # First network: Degrees network 
    # CNN Network

    # Define two sets of inputs 
    input_A_sequence = Input(shape=(TYPE_NUCLEOTIDES, NUM_NUCLEOTIDES,1))
    input_B_degrees = Input(shape=(NUM_ANGLES,NUM_NUCLEOTIDES,1))
    

    #BRANCH 1: STRUCT CONV----------------------------------------------
    # Input -> (5,50,1)
    x = Conv2D(NUM_FILTERS_STRUCT, KERNEL_SIZES_STRUCT, padding = "same", activation = "relu")(input_B_degrees)
    x = BatchNormalization(momentum=MOMENTUM_D)(x)
    x = Dropout(DROPOUT_D)(x)
    # Output -> (50,50,1)

    x = MaxPooling2D(pool_size=(10,1))(x)
    # Output -> (50,5,1)

    x = Conv2D(NUM_FILTERS_STRUCT*2, KERNEL_SIZES_STRUCT, padding = "same", activation = "relu") (x)
    x = BatchNormalization(momentum=MOMENTUM_D)(x)
    x = Dropout(DROPOUT_D)(x)
    # Output -> (100,10,1)

    x = MaxPooling2D(pool_size=(5,1))(x)
    # Output -> (100,1,1)
    
    
    # Flatten network
    # It pools the images into a continuous vector through Flattening. 
    # It takes the 2-D array, and converts them to a one dimensional single vector.
    x = Flatten()(x)
    # Output -> 100

    # Fully connected layer: Dense
    # It adds a fully connected layer, 
    # units define the number of nodes that should be present in this layer (hidden neurons)
    x = Dense(units = NUM_HIDDEN_STRUCT,activation="relu")(x)
    x = BatchNormalization(momentum=MOMENTUM_D)(x)
    degrees_output = Dropout(DROPOUT_D)(x)
    # Output -> 20

    #BRANCH 2: SEQ CONV--------------------------------------------
    
    # Second network: Sequence network => Sequence output
    # CNN network 
    # Convolution layer
    # Input -> (4,50,1)
    y = Conv2D( NUM_FILTERS_SEQ, KERNEL_SIZES_SEQ, data_format = "channels_first", padding = "same", activation="relu")(input_A_sequence)
    y = BatchNormalization(momentum=MOMENTUM_D)(y)
    y = Dropout(DROPOUT_D)(y)
    # Output -> (50,50,1)

    y = MaxPooling2D(pool_size=(5,1))(y)
    # Output -> (50,10,1)

    y = Conv2D( NUM_FILTERS_SEQ* 2, KERNEL_SIZES_SEQ, padding = "same", activation = "relu" ) (y)
    y = BatchNormalization(momentum=MOMENTUM_D)(y)
    y = Dropout(DROPOUT_D)(y)
    # Output -> (100,10,1)

    y = MaxPooling2D(pool_size=(10,1))(y)
    # Output -> (100,1,1)
    
    # Flatten network
    # It pools the images into a continuous vector through Flattening. 
    # It takes the 2-D array, and converts them to a one dimensional single vector.
    y = Flatten()(y)
    # Output -> 100

    # Fully connected layer: Dense
    # It adds a fully connected layer, 
    # units define the number of nodes that should be present in this layer
    y = Dense(units = NUM_HIDDEN_SEQ, activation="relu")(y)
    y = BatchNormalization(momentum=MOMENTUM_D)(y)
    sequence_output = Dropout(DROPOUT_D)(y)
    # Output -> 20

    #COMMON PART: DENSE--------------------------------------------
    # Construct both models
    seq = Model(input_A_sequence, sequence_output)
    deg = Model(input_B_degrees, degrees_output)
    # Combine the output of the two branches
    combined = concatenate([seq.output, deg.output])
    # Output -> 40
    
    # Apply a Fully-Conected layer and then a regression prediction on the combined outputs
    z = Dense(NUM_HIDDEN_COMMON, kernel_initializer = 'normal', activation = "sigmoid") (combined)
    # Output -> 1
    
    # The model accepts two inputs and the output is single value
    D = Model(inputs=[seq.input, deg.input], outputs=z)

    #Compile the model
    sgd = SGD( lr = LEARNING_RATE_D, momentum = MOMENTUM_D, decay = DECAY_D, nesterov = False )
    D.compile( loss = "mean_squared_error", optimizer = sgd, metrics = ['accuracy'])
    #D.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
    return D