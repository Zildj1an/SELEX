### OPEN MODELS AND THEIR WEIGHTS 
from keras.models import model_from_json

def load_G(POSES_FOLDER):
# Load JSON and create model
    json_file = open(POSES_FOLDER+"generator.json", "r")
    loaded_generator = json_file.read()
    json_file.close()
    my_generator_new = model_from_json(loaded_generator)

    # Load weights into the new models
    my_generator_new.load_weights(POSES_FOLDER+"generator_weights.h5")

    # Model compilation
    my_generator_new.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

    return my_generator_new

def load_D(POSES_FOLDER):
    # Load JSON and create model
    json_file = open(POSES_FOLDER+"discriminator.json", "r")
    loaded_discriminator = json_file.read()
    json_file.close()
    my_discriminator_new = model_from_json(loaded_discriminator)

    # Load weights into the new models
    my_discriminator_new.load_weights(POSES_FOLDER+"discriminator_weights.h5")

    # Model compilation 
    my_discriminator_new.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
    
    return my_discriminator_new


def load_gan(POSES_FOLDER):
    # Load JSON and create model
    json_file = open(POSES_FOLDER+"gan.json", "r")
    loaded_gan = json_file.read()
    json_file.close()
    my_gan_new = model_from_json(loaded_gan)

    # Load weights into the new models
    my_gan_new.load_weights(POSES_FOLDER+"gan_weights.h5")

    # Model compilation
    my_gan_new.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

    return my_gan_new

# Evaluate loaded models on test data:
# The models are used with a random nucleotides data => checks that the model is loaded and works 
#noise=noise_nucleotides(1)
#new_gan = my_gan_new.predict(noise)
#print(new_gan)

#new_value = my_generator_new.predict(noise)
#print(new_value)

#new_pred = my_discriminator_new.predict([noise,new_value])
#print(new_pred)