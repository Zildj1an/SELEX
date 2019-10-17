# IMPORTS
import numpy as np
from Aux_train_functions import summarize_performance

# Variables
FIRST_TIME = True

### TRAIN
# Train the model
def train(X_train,Y_train,Y_test,X_test, generative, discriminative, GAN, epochs, batch_size, sample_interval, POSES_FOLDER, BATCH_SIZE, NUM_NUCLEOTIDES, RESULTS_CSV, scorefxn):
    global FIRST_TIME
    # Adversarial ground truths -> in order t cretate the training set for teh discriminator
    fake = np.zeros((batch_size, 1)) #-> For to database images
    valid = np.ones((batch_size, 1)) #-> For to generated images with the generative network

    for epoch in range(epochs):
        # Discriminator
        # Select a random batch of images from the database
        idx = np.random.randint(0, X_train.shape[0], batch_size)
        sequences_DB = X_train[idx]
        degrees_DB = Y_train[idx]

        # Generate a batch of new images from the known sequences with the generator
        degrees_GEN = generative.predict(sequences_DB)

        # Generates training set for the discriminator: takes generated and original images 
        # with its sentesnces and assign the valid or not valid digit.
        # And train the discriminator and update its model weights
        #set_trainability(my_discriminator, True)
        discriminative.fit(x=[sequences_DB,degrees_DB],y=valid,batch_size=batch_size,epochs=50,verbose=1)
        discriminative.fit(x=[sequences_DB,degrees_GEN],y=fake,batch_size=batch_size,epochs=50,verbose=1)
        #my_discriminator.train_on_batch(x=[sequences_DB,degrees_DB],y=valid)
        #my_discriminator.train_on_batch(x=[sequences_DB,degrees_GEN],y=fake)
        #set_trainability(my_discriminator, False)
        #d_loss_real,_ = my_discriminator.train_on_batch([sequences_DB,degrees_DB], valid)
        #d_loss_fake,_ = my_discriminator.train_on_batch([sequences_DB,degrees_GEN], fake)
        #d_loss = 0.5 *(d_loss_real + d_loss_fake)

        # Generator
        # Train the generator (to have the discriminator label samples as valid)
        # and update its weights
        #g_loss, _ = GAN.train_on_batch(sequences_DB, valid)
        GAN.fit(x=sequences_DB,y=valid,batch_size=batch_size,epochs=100,verbose=1)
        #GAN.train_on_batch(x=sequences_DB,y=valid)

        # Plot the progress:
        #print("> Epoch: %d, D loss: %.3f G loss:%.3f" %(epoch, d_loss, g_loss))
    
        # If at save interval => save a generated image sample in this step and plot the accuracy
        if not (epoch % sample_interval) or (epoch == (epochs-1)):
            summarize_performance(epoch=epoch,generative=generative, discriminative=discriminative, X_test=X_test, Y_test=Y_test, batch_size=(int(0.1*BATCH_SIZE)+1), POSES_FOLDER=POSES_FOLDER, NUM_NUCLEOTIDES=NUM_NUCLEOTIDES,RESULTS_CSV=RESULTS_CSV, scorefxn=scorefxn, FIRST_TIME=FIRST_TIME)