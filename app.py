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


def main():
    st.markdown(
        """
    Drawable Canvas doesn't provided out-of-the-box image annotation capabilities, but we can hack something with session state,
    by mapping a drawing fill color to a label.

    Annotate pedestrians, cars and traffic lights with this one, with any color/label you want 
    (though in a real app you should rather provide your own label and fills :smile:).

    If you really want advanced image annotation capabilities, you'd better check [Streamlit Label Studio](https://discuss.streamlit.io/t/new-component-streamlit-labelstudio-allows-you-to-embed-the-label-studio-annotation-frontend-into-your-application/9524)
    """
    )
    bg_image = Image.open("test.png")
    label_color = (
        st.sidebar.color_picker("Annotation color: ", "#EA1010") + "77"
    )  # for alpha from 00 to FF
    label = st.sidebar.text_input("Label", "Default")
    mode = "transform" if st.sidebar.checkbox("Move ROIs", False) else "rect"

    canvas_result = st_canvas(
        fill_color=label_color,
        stroke_width=3,
        background_image=bg_image,
        height=480,
        width=480,
        drawing_mode=mode,
        key="color_annotation_app",
    )
    if canvas_result.json_data is not None:
        df = pd.json_normalize(canvas_result.json_data["objects"])
        if len(df) == 0:
            return
        st.session_state["color_to_label"][label_color] = label
        df["label"] = df["fill"].map(st.session_state["color_to_label"])
        st.dataframe(df[["top", "left", "width", "height", "fill", "label"]])

    with st.expander("Color to label mapping"):
        st.json(st.session_state["color_to_label"])