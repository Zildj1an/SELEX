# IMPORTS
from keras.models import Model

### FREEZE MODELS
# Freeze models in order to save them
def freeze(model):
    for layer in model.layers:
        layer.trainable = False

        if isinstance(layer, Model):
            freeze(layer)

### SAVE MODELS AND ITS WEIGHTS:
def save_gan(my_gan, POSES_FOLDER):
    freeze(my_gan)
    # Serialize model to JSON and save the models
    my_gan_json = my_gan.to_json()
    with open(POSES_FOLDER+"gan.json", "w") as json_file:
        json_file.write(my_gan_json)

    # Serialize weights to HDF5 and save them
    my_gan.save_weights(POSES_FOLDER+"gan_weights.h5")

def save_D(my_discriminator, POSES_FOLDER):
    freeze(my_discriminator)
    # Serialize model to JSON and save the models
    my_discriminator_json = my_discriminator.to_json()
    with open(POSES_FOLDER+"discriminator.json", "w") as json_file:
        json_file.write(my_discriminator_json)

    # Serialize weights to HDF5 and save them
    my_discriminator.save_weights(POSES_FOLDER+"discriminator_weights.h5")

def save_G(my_generator, POSES_FOLDER):
    freeze(my_generator)
    # Serialize model to JSON and save the models
    my_generator_json = my_generator.to_json()
    with open(POSES_FOLDER+"generator.json", "w") as json_file:
        json_file.write(my_generator_json)

    # Serialize weights to HDF5 and save them
    my_generator.save_weights(POSES_FOLDER+"generator_weights.h5")