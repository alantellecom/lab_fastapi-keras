import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
import numpy as np

from passlib.context import CryptContext

def preprocess_image(image_path):
    img = keras.preprocessing.image.load_img(image_path, target_size=(32, 32))
    img = keras.preprocessing.image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    return tf.convert_to_tensor(img)

pwd_cxt = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_pass(hashed_password,plain_password):
    return pwd_cxt.verify(plain_password,hashed_password)