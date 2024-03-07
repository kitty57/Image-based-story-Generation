import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from IPython.display import Markdown
import textwrap

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def generate_story(llm, hmessage,images):
    msg = llm.invoke([hmessage])
    return to_markdown(msg.content)

def main():
    input_option = st.radio("Input Option:", ("Upload Images", "Enter Image URLs"))

    # Input fields based on user choice
    if input_option == "Upload Images":
        uploaded_images = st.file_uploader("Upload Image(s):", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        image_urls = [None] * 4
    else:
        st.markdown("Enter the URLs of the images:")
        image_urls = []
        for i in range(4):
            image_url = st.text_input(f"Image {i+1} URL:")
            image_urls.append(image_url)

    # Display images if URLs are provided
    images = []
    for image_url in image_urls:
        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = response.content
                image = Image.open(BytesIO(image_data))
                images.append(image)
            else:
                st.error(f"Failed to fetch image from URL: {image_url}")

    # Display images in parallel
    if images:
        st.image(images, caption=[f"Image {i+1}" for i in range(len(images))], width=200)

        # Initialize Language Model
        llm = ChatGoogleGenerativeAI(model="gemini-pro-vision", google_api_key='YOUR_GOOGLE_API_KEY')

        # Generate story button
        if st.button("Generate Story"):
            # Create HumanMessage with image URLs
            hmessage = HumanMessage(
                content=[
                    {"type": "text",
                     "text": "Create a cohesive story that links the provided sequence of images together. Utilize the context of each image to generate text that seamlessly connects them into a coherent narrative."
                    },
                    {"type": "image_url",
                      "image_url": images[0]},
                    {"type": "image_url",
                     "image_url": images[1]},
                    {"type": "image_url",
                      "image_url": images[2]},
                    {"type": "image_url",
                      "image_url": images[3]},
                ]
            )

            # Generate and display story
            story = generate_story(llm, hmessage)
            st.markdown(story)

if __name__ == "__main__":
    main()

