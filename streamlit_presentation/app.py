import streamlit as st
from pptx import Presentation
from pptx.util import Inches
import pandas as pd
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

@st.cache
def load_data(file_url):
    """functio to load csv file"""
    data = pd.read_csv(file_url, sep=';')
    return data

def add_image(slide, image, left, top, width):
    """function to add an image to the PowerPoint slide and specify its position and width"""
    slide.shapes.add_picture(image, left=left, top=top, width=width)

def replace_text(replacements, slide):
    """function to replace text on a PowerPoint slide. Takes dict of {match: replacement, ... } and replaces all matches"""
    # Iterate through all shapes in the slide
    for shape in slide.shapes:
        for match, replacement in replacements.items():
            if shape.has_text_frame:
                if (shape.text.find(match)) != -1:
                    text_frame = shape.text_frame
                    for paragraph in text_frame.paragraphs:
                        whole_text = "".join(run.text for run in paragraph.runs)
                        whole_text = whole_text.replace(str(match), str(replacement))
                        for idx, run in enumerate(paragraph.runs):
                            if idx != 0:
                                p = paragraph._p
                                p.remove(run._r)
                        if bool(paragraph.runs):
                            paragraph.runs[0].text = whole_text

def generate_gpt_response(gpt_input, max_tokens):
    """function to generate a response from GPT-3. Takes input and max tokens as arguments and returns a response"""
    # Create an instance of the OpenAI class
    chat = ChatOpenAI(openai_api_key=st.secrets["openai_credentials"]["API_KEY"], model='gpt-4-1106-preview',
                      temperature=0, max_tokens=max_tokens)

    # Generate a response from the model
    response = chat.predict_messages(
        [SystemMessage(content='You are a helpful expert in products and sales.'),
         HumanMessage(
             content=gpt_input)])

    return response.content.strip()

def generate_gpt_image(gpt_image_prompt):
    """function to generate a image from GPT-3. Takes input as argument and returns a response"""
    # Create an instance of the OpenAI class
    response = openai.Image.create(
        prompt=f"build a image that best represent this review or answer to this review: {gpt_image_prompt}",
        n=1,
        size="512x512",
        response_format='b64_json'
    )
    return response['data'][0]['b64_json']

def plot_image(b64_image_data):
    """function to decode the b64 data. Takes input as argument and returns a response"""
    # Decode the base64 data
    image_data = base64.b64decode(b64_image_data)

    # Create a PIL image object and plot the image
    image = Image.open(io.BytesIO(image_data))

    return image

def dict_from_string(response):
    """function to parse GPT response with competitors tickers and convert it to a dict"""
    # Find a substring that starts with '{' and ends with '}', across multiple lines
    match = re.search(r'\{.*?\}', response, re.DOTALL)

    dictionary = None
    if match:
        try:
            # Try to convert substring to dict
            dictionary = ast.literal_eval(match.group())
        except (ValueError, SyntaxError):
            # Not a dictionary
            return None
    return dictionary

def convert_to_nested_dict(input_dict, nested_key):
    """function to convert a dictionary to a nested dictionary. Takes a dictionary and a nested key as arguments and returns a dictionary"""
    output_dict = {}
    for key, value in input_dict.items():
        output_dict[key] = {nested_key: value}
    return output_dict

def shorten_summary(text):
    # Split the text into sentences using a regular expression pattern
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    # Return the first two sentences or less if there are fewer sentences
    sen = ' '.join(sentences[:2])

    # if the summary is less than 350 characters, return the summary
    if len(sen) <= 400:
        return sen
    else:
        # if the summary is more than 350 characters, return the first 350 characters and truncate the last word
        truncated_sen = text[:400].rsplit(' ', 1)[0] + '...'
        return truncated_sen

def fix_text_capitalization(text):
    fixed_text = text.lower().capitalize()
    return fixed_text

def app():
    st.write(st.secrets["openai_credentials"]["API_KEY"])
    file_url = "streamlit_presentation/product-search-corpus-final.csv"
    ppt_file = st.file_uploader("Upload your PowerPoint file", type=["pptx"])

    if ppt_file:
        data = load_data(file_url)
        gpt_input = data.iloc[0]['text']
        company_name = generate_gpt_response(gpt_input, 100)

        presentation = Presentation(ppt_file)
        slide = presentation.slides[0]
        replace_text({"{company}": company_name}, slide)

        presentation.save("updated_ppt.pptx")
        st.success("PowerPoint file updated successfully!")

        # Add download button for the ppt file
        st.markdown(get_ppt_download_link("updated_ppt.pptx", "updated_ppt.pptx"), unsafe_allow_html=True)

if __name__ == "__main__":
    app()
