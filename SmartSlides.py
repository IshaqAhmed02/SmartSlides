# importing libraries
import cv2
import streamlit as st
from pdf2image import convert_from_path
from cvzone.HandTrackingModule import HandDetector


# Function to convert PDF to images
def convert_pdf_to_images(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300)
    images = []
    for i, page in enumerate(pages):
        image_path = f'page_{i}.jpg'
        page.save(image_path, 'JPEG')
        images.append(image_path)
    return images


# Streamlit interface

st.set_page_config(page_title="Gesture Controlled Presentation", layout="wide")
st.title("\tHand Gesture Controlled Presentation")  # title
st.sidebar.title("Navigation")  # title on sidebar
st.sidebar.markdown("Use the sidebar to navigate through the app.")

pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])  # Uploading file
if pdf_file:
    pdf_path = pdf_file.name
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())

    st.sidebar.write("Converting PDF to images...")
    presentation_images = convert_pdf_to_images(pdf_path)
    total_pages = len(presentation_images)

    st.sidebar.write(f"Total pages: {total_pages}")

    slide_number = st.sidebar.number_input("Slide Number", min_value=1, max_value=total_pages, value=1)
    image_path = presentation_images[slide_number - 1]
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    st.image(image, caption=f"Slide {slide_number}", use_column_width=True)

    st.sidebar.write("You can control the slides using hand gestures.")

    # Hand gesture detection
    stframe = st.empty()
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=1)

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img)

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            cx, cy = hand['center']

            if fingers == [0, 1, 0, 0, 0]:  # Forward gesture
                if slide_number > 1:
                    slide_number += 1
            elif fingers == [1, 0, 0, 0, 0]:  # Backward gesture
                if slide_number < total_pages:
                    slide_number -= 1

        image_path = presentation_images[slide_number - 1]
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        stframe.image(image, caption=f"Slide {slide_number}", use_column_width=True)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
