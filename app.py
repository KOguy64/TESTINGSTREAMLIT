import base64
import json
import os
import re
import time
import uuid
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from svgpathtools import parse_path
import tensorflow as tf

if "button_id" not in st.session_state:
        st.session_state["button_id"] = ""
        
st.markdown(
    """
This is room position detection thingy
"""
)
try:
    Path("tmp/").mkdir()
except FileExistsError:
    pass

# Regular deletion of tmp files
# Hopefully callback makes this better
now = time.time()
N_HOURS_BEFORE_DELETION = 1
for f in Path("tmp/").glob("*.png"):
    st.write(f, os.stat(f).st_mtime, now)
    if os.stat(f).st_mtime < now - N_HOURS_BEFORE_DELETION * 3600:
        Path.unlink(f)

if st.session_state["button_id"] == "":
    st.session_state["button_id"] = re.sub(
        "\d+", "", str(uuid.uuid4()).replace("-", "")
    )

button_id = st.session_state["button_id"]
file_path = f"tmp/{button_id}.png"

custom_css = f""" 
    <style>
        #{button_id} {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: rgb(255, 255, 255);
            color: rgb(38, 39, 48);
            padding: .25rem .75rem;
            position: relative;
            text-decoration: none;
            border-radius: 4px;
            border-width: 1px;
            border-style: solid;
            border-color: rgb(230, 234, 241);
            border-image: initial;
        }} 
        #{button_id}:hover {{
            border-color: rgb(246, 51, 102);
            color: rgb(246, 51, 102);
        }}
        #{button_id}:active {{
            box-shadow: none;
            background-color: rgb(246, 51, 102);
            color: white;
            }}
    </style> """
model = tf.saved_model.load("model")

bg = Image.open("test.png")
bg = bg.convert("RGB")
data = st_canvas(update_streamlit=True, key="png_export", height=480, width=480, background_image=bg)
if (st.button("Analyse")):
    if data is not None and data.image_data is not None:
        img_data = data.image_data
        im = Image.fromarray(img_data.astype("uint8"), mode="RGBA")
        bg.paste(im, (0,0), im)
        st.image(bg)
        bg.save("out.png", "PNG")

        # buffered = BytesIO()
        # im.save(buffered, format="PNG")
        # img_data = buffered.getvalue()
        # try:
        #     # some strings <-> bytes conversions necessary here
        #     b64 = base64.b64encode(img_data.encode()).decode()
        # except AttributeError:
        #     b64 = base64.b64encode(img_data).decode()

        output = tf.io.read_file("out.png")
        output = tf.image.decode_png(output, channels = 1)

        #output  = tf.keras.utils.img_to_array(bg)
        #output = tf.image.rgb_to_grayscale(output)
        #output = tf.cast(output * 255, tf.uint8)
        
        output = tf.image.resize(output, [32, 32])
        output = (255.0 - output) / 255.0
        
        output = tf.expand_dims(output, axis = 0)
        #st.caption(output)
        #st.caption(list(output.numpy()))

        st.caption(model.serve(output))
else:
    st.caption("Didn't do something")