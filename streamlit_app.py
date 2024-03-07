import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from IPython.display import Markdown
import textwrap
import base64

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
    
def generate_story(llm, hmessage):
    msg = llm.invoke([hmessage])
    return msg.content

def main():
    st.title("Image-Based Storytelling with Language Model")
    st.markdown("Generate a story that links the provided sequence of images together.")
    
    # User input option
    input_option = st.radio("Input Option:", ("Upload Images", "Enter Image URLs"))
    
    # Initialize Language Model
    llm = ChatGoogleGenerativeAI(model="gemini-pro-vision", google_api_key='AIzaSyDlBFVsmV8pao6Ax-bcR0dc5h4CusiNCsc')
    
    # User input fields based on the selected option
    images = []
    if input_option == "Upload Images":
        uploaded_images = st.file_uploader("Upload Image(s):", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        if uploaded_images:
            for uploaded_image in uploaded_images:
                image = Image.open(BytesIO(uploaded_image.read()))
                images.append(image)
    else:
        st.markdown("Enter the URLs of the images:")
        for i in range(3):  # Assuming 3 images for this example
            image_url = st.text_input(f"Image {i+1} URL:")
            if image_url:
                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        images.append(image)
                    else:
                        st.error(f"Failed to fetch image from URL: {image_url}")
                except Exception as e:
                    st.error(f"Error fetching image from URL: {image_url}")

    # Display uploaded images or image URLs
    if images:
        st.image(images, caption=[f"Image {i+1}" for i in range(len(images))], width=200)

        # Generate story button
        if st.button("Generate Story"):
            hmessage = HumanMessage(
                content=[
                    {"type": "text",
                     "text": "Create a cohesive story that links the provided sequence of images together. Utilize the context of each image to generate text that seamlessly connects them into a coherent narrative."
                    }
                ]
            )
            
            for image in images:
                image_data = BytesIO()
                image.save(image_data, format="JPEG")
                image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data.getvalue()).decode()}"
                hmessage.content.append({"type": "image_url", "image_url": image_url})
            generated_story = generate_story(llm, hmessage)
            with st.expander("Generated Story", expanded=True):
              st.write(generated_story)

if __name__ == "__main__":
    main()
