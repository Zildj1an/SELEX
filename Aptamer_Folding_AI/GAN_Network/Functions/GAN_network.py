# IMPORTS
from keras.layers import Input
from keras.models import Model
from keras.optimizers import SGD

#Optimizer GAN
LEARNING_RATE = 0.7
MOMENTUM = 0.9
DECAY = 0.0
DROPOUT = 0.4

# The discriminator is freeze in GAN model,
# because in the train, it only trains the generative part, the discriminative is trained outside the GAN
def set_trainability(model, trainable=False):
    model.trainable = trainable
    for layer in model.layers:
        layer.trainable = trainable

# Creates the GAN model
def build_mygan(generator, discriminator, TYPE_NUCLEOTIDES, NUM_NUCLEOTIDES):
    global LEARNING_RATE, DECAY
    set_trainability(discriminator, False)
    # The input is teh same that the generative network
    GAN_in = Input(shape=(TYPE_NUCLEOTIDES, NUM_NUCLEOTIDES,1))
    # Constructs the generator part
    x = generator(GAN_in)
    # Constructs the discriminator part (which input is the sequence and the degrees from the output of the generative network)
    GAN_out = discriminator([GAN_in,x])
    # Contsruct the model
    GAN = Model(GAN_in, GAN_out)
    # The model es compiled

    sgd = SGD( lr = LEARNING_RATE, momentum = MOMENTUM, decay = DECAY, nesterov = False )
    GAN.compile( loss = "mean_squared_error", optimizer = sgd, metrics = ['accuracy'] )
    #GAN.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
    return GAN

# In order to constatate if the network works:
# first_gan_data = my_gan.predict(noise)