from flask import Flask, jsonify, request
from flask_cors import CORS
import tensorflow as tf
from keras import layers
import os 
import base64


app = Flask(__name__)
CORS(app)

#Moved the enitre model to the Flask app file
def generateImage():
        def build_generator(noise_dim):
            inputs1 = layers.Input(shape=(noise_dim,))
            label_input = layers.Input(shape=(1,))

            label_embedding = layers.Embedding(5, 10)(label_input)
            label_embedding = layers.Flatten()(label_embedding)

            concatenated_input = layers.Concatenate()([inputs1, label_embedding])
            x = layers.Dense(512 * 4 * 4, use_bias=False)(concatenated_input)
            x = layers.Reshape((4, 4, 512))(x)

            x = layers.Conv2DTranspose(64 * 8, kernel_size=5, strides=2, padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.LeakyReLU(0.2)(x)

            x = layers.Conv2DTranspose(64 * 4, kernel_size=5, strides=2, padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.LeakyReLU(0.2)(x)

            x = layers.Conv2DTranspose(64 * 2, kernel_size=5, strides=2, padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.LeakyReLU(0.2)(x)
 
            x = layers.Conv2DTranspose(64 * 1, kernel_size=5, strides=2, padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.LeakyReLU(0.2)(x)
            x = layers.Dropout(0.3)(x)

            outputs = layers.Conv2D(3, kernel_size=5, padding='same', activation="tanh", dtype='float32')(x)

            model = tf.keras.Model(inputs=[inputs1, label_input], outputs=outputs, name='generator')
           
            return model


        number_of_images_to_generate = 1
        class_number = 3
    
        gen = build_generator(128)  # This loads a blank neural network with our architecture
        gen.load_weights("generator.h5")  # This loads the weights from training
        noise = tf.random.normal([number_of_images_to_generate, 128])
        label = tf.constant([class_number])
        image = gen([noise, label])
        img = image.numpy()
        img = tf.squeeze(img, axis=0)
        tf.keras.utils.save_img("test.jpeg", img)


# POST to send the user prompt 
@app.route("/hi", methods=["POST"])
def home():
     data = request.get_json()
     prompt = data.get("prompt")

     
     


     generateImage()

     imagePath = "test.jpeg"
     try:
          with open(imagePath, "rb") as imageFile:
            imageEncoded = base64.b64encode(imageFile.read()).decode()
            imageData = f"data:image/jpeg;base64,{imageEncoded}"
            return jsonify({"image": imageData})
     except FileNotFoundError:
            return jsonify({"error": "Failed to load image"}), 500
          
     # return send_file('test.jpeg')

    

if __name__ == "__main__":
    app.run(debug=True)
