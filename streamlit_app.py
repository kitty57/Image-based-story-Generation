import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from IPython.display import Markdown
import textwrap

def generate_story(llm, hmessage):
    msg = llm.invoke([hmessage])
    return to_markdown(msg.content)
def get_image_url(uploaded_image):
    # Convert uploaded image to URL
    image_url = None
    if uploaded_image is not None:
        img_data = uploaded_image.read()
        img_bytes = BytesIO(img_data)
        img = Image.open(img_bytes)
        image_url = save_image_to_tempfile(img)
    return image_url

def save_image_to_tempfile(image):
    # Save image to temporary file and return URL
    with BytesIO() as output:
        image.save(output, format="JPEG")
        data = output.getvalue()
    return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"

def main():
    # Set up Streamlit layout
    st.title("Image-Based Storytelling with Language Model")
    st.markdown("Choose how you want to input images:")

    # User input option
    input_option = st.radio("Input Option:", ("Upload Images", "Enter Image URLs"))

    # Input fields based on user choice
    if input_option == "Upload Images":
        uploaded_images = st.file_uploader("Upload Image(s):", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        image_urls = [None] * 4
        images = []
        if uploaded_images:
            for uploaded_image in uploaded_images:
                image_url = get_image_url(uploaded_image)
                images.append(image_url)

    else:
        st.markdown("Enter the URLs of the images:")
        image_urls = []
        for i in range(4):
            image_url = st.text_input(f"Image {i+1} URL:")
            image_urls.append(image_url)
        for image_url in image_urls:
            if image_url:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = response.content
                    image = Image.open(BytesIO(image_data))
                    images.append(image)
                else:
                    st.error(f"Failed to fetch image from URL: {image_url}")

    st.image(images, caption=[f"Image {i+1}" for i in range(len(images))], width=200)

    # Initialize Language Model
    llm = ChatGoogleGenerativeAI(model="gemini-pro-vision", google_api_key='AIzaSyDlBFVsmV8pao6Ax-bcR0dc5h4CusiNCsc')

    # Generate story button
    if st.button("Generate Story") and images:
        hmessage = HumanMessage(
            content=[
                {"type": "text",
                 "text": "Create a cohesive story that links the provided sequence of images together. Utilize the context of each image to generate text that seamlessly connects them into a coherent narrative."
                },
                {"type": "image_url",
                "image_url": images[0] if len(images) > 0 else None},
                {"type": "image_url",
                "image_url": images[1] if len(images) > 1 else None},
                {"type": "image_url",
                "image_url": images[2] if len(images) > 2 else None},
                {"type": "image_url",
                "image_url": images[3] if len(images) > 3 else None},
            ]
        )
        with st.expander("Generated Story"):
            story = generate_story(llm, hmessage)
            st.markdown(story)

if __name__ == "__main__":
    main()
