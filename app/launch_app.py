# launch_app.py

from Determine_Fame import get_fame
import joblib
import streamlit as st
import numpy as np
import keras
import cv2
from PIL import Image

# Load your models
forest = joblib.load("ArtNum.joblib")
image_regressor = keras.models.load_model("Image_Regressor.h5")

st.title("Artist Prediction Model")

def load_input_ui():
    uploaded_file = st.file_uploader(label='Pick an image to test')
    if uploaded_file is not None:
        image_data = uploaded_file.getvalue()
        st.image(image_data, caption='Uploaded Image', use_column_width=True)
        image = Image.open(uploaded_file).convert("RGB")
        image_array = np.array(image)
    else:
        image_array = None

    artist = st.text_input("Artist Name")
    year = st.text_input("Year")
    art_nouveau = st.text_input("Art Nouveau")
    abstract_express = st.text_input("Abstract Expressionism")
    expressionism = st.text_input("Expressionism")
    feminist_art = st.text_input("Feminist Art")
    abstract = st.text_input("Abstract")
    conceptual = st.text_input("Conceptual")
    impressionism = st.text_input("Impressionism")
    baroque = st.text_input("Baroque")
    geometric_abstraction = st.text_input("Geometric Abstraction")
    cubism = st.text_input("Cubism")
    art_brut = st.text_input("Art Brut")
    environmental_art = st.text_input("Environmental Art")
    art_deco = st.text_input("Art Deco")

    submit = st.button('Submit')

    if submit:
        if not artist:
            st.error("Please enter the artist's name.")
            return

        # Get fame score using Determine_Fame.py
        with st.spinner("Fetching fame score..."):
            fame = get_fame(artist)
        
        # Prepare input data for the forest model
        input_data = [
            fame,
            year,
            abstract,
            abstract_express,
            art_brut,
            art_deco,
            art_nouveau,
            baroque,
            conceptual,
            cubism,
            environmental_art,
            expressionism,
            feminist_art,
            geometric_abstraction,
            impressionism
        ]

        # Validate input_data
        try:
            input_data = [int(fame)] + [int(x) if x else 0 for x in input_data[1:]]
        except ValueError:
            st.error("Please ensure all numerical inputs are valid integers.")
            return

        # Process image for the image regressor model
        if image_array is not None:
            try:
                image_processed = cv2.resize(image_array, (150, 150), interpolation=cv2.INTER_AREA)
                image_processed = np.expand_dims(image_processed, axis=0)
            except Exception as e:
                st.error(f"Error processing image: {e}")
                return
        else:
            st.error("Please upload an image.")
            return

        # Predict prices
        with st.spinner("Predicting prices..."):
            try:
                image_regr_price = image_regressor.predict(image_processed)[0][0]
                forest_price = forest.predict([input_data])[0]
                loss = 0.99
                predicted_price = image_regr_price * (1 - loss) + loss * forest_price
                predicted_price = round(predicted_price, 2)
                st.success(f"Predicted Sell Price (USD): ${predicted_price}")
            except Exception as e:
                st.error(f"Error during prediction: {e}")

def main():
    st.header("Upload Artwork and Provide Details")
    load_input_ui()

if __name__ == '__main__':
    main()
