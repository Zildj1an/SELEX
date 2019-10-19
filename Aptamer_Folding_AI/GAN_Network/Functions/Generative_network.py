# IMPORTS
from keras.layers import Input, BatchNormalization, Activation, MaxPooling2D, Dropout, Flatten, Conv2D, Conv2DTranspose, UpSampling2D
from keras.models import Model
from keras.optimizers import SGD
from Aux_train_functions import L_CUSTOM

# GENERATIVE NETWORK

#Generative network
KERNEL_SIZES_GEN = [(2,1),(5,1)]

#Optimizer Generative
LEARNING_RATE_G = 0.9
MOMENTUM_G = 0.9
DECAY_G = 0.0
DROPOUT_G = 0.2

### GENERATOR
# Build the generator model : CNN WITH DIABOLO FORM
def build_my_generator(NUM_NUCLEOTIDES, TYPE_NUCLEOTIDES, NUM_ANGLES): 
    
    NUM_FILTERS_GEN = NUM_ANGLES*TYPE_NUCLEOTIDES

    global KERNEL_SIZES_GEN, LEARNING_RATE_G, MOMENTUM_G, DECAY_G, DROPOUT_G
    
    # Construct the model
    # Input -> (4,50,1)
    base_pairs = Input(shape=(TYPE_NUCLEOTIDES, NUM_NUCLEOTIDES, 1))
    # Applies the model to the data:
    # CNN with diabolo form: 2 parts -> convolution and deconvolution
    # Convolution part:
    # Convolution layer
    x = Conv2D(NUM_FILTERS_GEN, KERNEL_SIZES_GEN[0], data_format = "channels_first", padding="same",activation="relu")(base_pairs)
    x = BatchNormalization(momentum=MOMENTUM_G)(x)
    x = Dropout(DROPOUT_G)(x)
    # Conv1 : 1. number of filters,
    # 2.shape of filters 
    # 3."same"-> results in padding the input such that the output has the same length as the original input.
    # Relu: rectifier function
    # Output => (20,50,1)

    # Pooling layer: 
    # Reduce the size of the images as much as possible: it reduces the complexity of the model without reducing it’s performance.
    x = MaxPooling2D(pool_size=(2,1))(x)
    # Output => (20,25,1)

    x = Conv2D(NUM_FILTERS_GEN * 2, KERNEL_SIZES_GEN[1], padding = "same", activation = "relu") (x)
    x = BatchNormalization(momentum=MOMENTUM_G)(x)
    x = Dropout(DROPOUT_G)(x)
    #strides= 5
    # Output => (40, 25, 1)
    
    x = MaxPooling2D(pool_size=(5,1))(x)
    # Output => (40, 5, 1)

    x = Conv2D(NUM_FILTERS_GEN * 3, KERNEL_SIZES_GEN[1], padding = "same", activation = "relu") (x)
    x = BatchNormalization(momentum=MOMENTUM_G)(x)
    x = Dropout(DROPOUT_G)(x)
    # Output => (80, 5, 1)
    
    x = MaxPooling2D(pool_size=(5,1))(x)
    # Output => (80, 1, 1)

    # Deconvolution part:
    # Unpooling layer (pooling adversary)
    x = UpSampling2D(size=(2,1))(x)
    # Output => (80, 2, 1)
     
    # Deconvolution layer
    x = Conv2DTranspose(NUM_FILTERS_GEN*2, KERNEL_SIZES_GEN[1], padding = "same", activation = "relu")(x)
    x = BatchNormalization(momentum=MOMENTUM_G)(x)
    x = Dropout(DROPOUT_G)(x)
    # Output => (40, 2, 1)
    # Dilation_rate = Unpooling layer (pooling adversary)

    x = UpSampling2D(size=(5,1))(x)
    # Output => (40, 10, 1)

    x = Conv2DTranspose(NUM_FILTERS_GEN, KERNEL_SIZES_GEN[1], padding="same",activation="relu")(x)
    x = BatchNormalization(momentum=MOMENTUM_G)(x)
    x = Dropout(DROPOUT_G)(x)
    # Output => (20, 10, 1)

    x = UpSampling2D(size= (5,1))(x)
    # Output => (20, 50, 1)


    x = Conv2DTranspose(5, KERNEL_SIZES_GEN[0], padding="same",activation="relu")(x)
    x = BatchNormalization(momentum=MOMENTUM_G)(x)
    x = Activation(L_CUSTOM)(x)
    degrees = Dropout(DROPOUT_G)(x)
    # Output -> (5,50,1)
    
    # Construct the model with the input and the output
    G = Model(base_pairs, degrees)

    # Compile the constyructed model
    sgd = SGD( lr = LEARNING_RATE_G, momentum = MOMENTUM_G, decay = DECAY_G, nesterov = False )
    G.compile( loss = "mean_squared_error", optimizer = sgd, metrics = ['accuracy'])
    #G.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
    # 1. optimizer parameter is to choose the stochastic gradient descent algorithm.
    # 2. loss parameter is to choose the loss function.
    # 3. The metrics parameter is to choose the performance metric.

    return G

# Create sequences (#batch_size) from random nucleotides in order to probe the generative network
def noise_nucleotides(batch_size):
    noise = np.zeros([batch_size, TYPE_NUCLEOTIDES, NUM_NUCLEOTIDES])
    for i in range(0, batch_size):
        # Create random nucleotides (A,G,C,T) = (1,2,3,4)
        value = np.random.choice((1, 2, 3, 4))
        j=0
        while j<(NUM_NUCLEOTIDES):
            if value==1:
                noise[i,0,j]=1
            elif value==2:
                noise[i,1,j]=1
            elif value==3:
                noise[i,2,j]=1
            elif value==4:
                noise[i,3,j]=1
            j=j+1
    return noise.reshape((batch_size,TYPE_NUCLEOTIDES,NUM_NUCLEOTIDES,1)) #(BATCH_SIZE,4,50,1)

#noise=noise_nucleotides(BATCH_SIZE, NUM_NUCLEOTIDES,TYPE_NUCLEOTIDES)

# In order to constatate if the network works:
#first_generated_data = my_generator.predict(noise)