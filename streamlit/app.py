import streamlit as st
import pandas as pd
import spacy

models = ["en_core_web_sm"]

# Load CSV file hosted on GitHub
@st.cache
def load_data(file_url):
    data = pd.read_csv(file_url, sep=';')
    data = data[data['category'] != 'null']
    data = data[data['category'].notnull()]
    return data

# Function to calculate the similarity between two products with spaCy
def calculate_similarity(text1, text2):
    nlp = spacy.load("en_core_web_sm")
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    similarity = doc1.similarity(doc2)
    return similarity

# App
def main():
    st.title("Similaridade de Produtos")

    # URL of the CSV file in your GitHub repository
    file_url = "streamlit/product-search-corpus-final.csv"

    # Load data
    data = load_data(file_url)

    # Filters to select two products
    product1_category = st.selectbox("Select the Product category 1", data["category"].unique())
    product1_title = st.selectbox("Select the Product title 1", data[data["category"] == product1_category]["title"].unique())

    product2_category = st.selectbox("Select the Product category 2", data["category"].unique())
    product2_title = st.selectbox("Select the Product title 2", data[data["category"] == product2_category]["title"].unique())

    # Get data for selected products
    product1_data = data[(data["category"] == product1_category) & (data["title"] == product1_title)].iloc[0]
    product2_data = data[(data["category"] == product2_category) & (data["title"] == product2_title)].iloc[0]

    # View product information
    st.subheader("Product 1:")
    st.write(product1_data)

    st.subheader("Product 2:")
    st.write(product2_data)

    # Calculate and display similarity between product texts without braces and quotes
    product1_data['features'] = product1_data['features'].replace('{', '').replace('}', '').replace('"', '')
    product2_data['features'] = product2_data['features'].replace('{', '').replace('}', '').replace('"', '')

    similarity_score = calculate_similarity((product1_data["features"] + '-' + product1_data["category"]), (product2_data["features"] + '-'  + product2_data["category"]))
    st.subheader("Similarity between products:")
    st.write(f"The similarity between products is: {similarity_score:.2%}")

if __name__ == "__main__":
    main()
