from flask import Flask, render_template, request, url_for
import os
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import tensorflow as tf
from flask import jsonify
from tensorflow.keras.models import load_model, Model
import numpy as np
import matplotlib.pyplot as plt
import cv2


model_path = 'FER_64.h5'
model = load_model(model_path)

app = Flask(__name__)


# Define Grad-CAM function
def get_gradcam_heatmap(model, img_array, last_conv_layer_name, pred_index=None):
    grad_model = Model(
        inputs=[model.inputs],
        outputs=[model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]

    heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_outputs), axis=-1)

    heatmap = np.maximum(heatmap, 0)
    heatmap /= tf.math.reduce_max(heatmap)
    return heatmap.numpy()


def display_gradcam(img, heatmap, alpha=0.0005):
    heatmap = np.uint8(255 * heatmap)
    jet = plt.cm.get_cmap("jet")

    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    jet_heatmap = tf.image.resize(jet_heatmap, (img.shape[0], img.shape[1]))
    jet_heatmap = tf.keras.preprocessing.image.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
    jet_heatmap = tf.keras.preprocessing.image.img_to_array(jet_heatmap)

    superimposed_img = jet_heatmap * 0.004 + img * (1 - alpha)
    superimposed_img = np.uint8(255 * superimposed_img / np.max(superimposed_img))

    return superimposed_img


@app.route('/', methods=['GET'])
def hello():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def predict():
    imagefile = request.files['imagefile']
    if imagefile:
        image_path = "./static/images/" + imagefile.filename
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        imagefile.save(image_path)

        img = load_img(image_path, target_size=(48, 48), color_mode="grayscale")
        im = img_to_array(img)
        im = np.expand_dims(im, axis=0)
        im = im / 255.

        classes = {
            0: 'angry',
            1: 'disgust',
            2: 'fear',
            3: 'happy',
            4: 'neutral',
            5: 'sad',
            6: 'surprise'
        }

        predicted_class = np.argmax(model.predict(im, verbose=0))
        predicted_class = classes[predicted_class]
        classification = f'Recognized emotion is {predicted_class}'

        last_conv_layer_name = 'conv2d_40'
        image_url = url_for('static', filename='images/' + imagefile.filename)
        heatmap = get_gradcam_heatmap(model, im, last_conv_layer_name)
        superimposed_img = display_gradcam(im, heatmap)
        heatmap_path = "./static/heatmap.jpg"
        cv2.imwrite(heatmap_path, cv2.cvtColor(superimposed_img, cv2.COLOR_RGB2BGR))

    else:
        classification = 'No image uploaded.'
        image_url = None

    return render_template('index.html', prediction=classification, image_url=image_url)


if __name__ == "__main__":
    app.run(debug=True, port=3000)
