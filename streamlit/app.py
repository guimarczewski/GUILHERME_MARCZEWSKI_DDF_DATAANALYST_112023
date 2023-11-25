import streamlit as st
import pandas as pd
import spacy

models = ["en_core_web_sm"]

# Carregar dados do arquivo CSV hospedado no GitHub
@st.cache
def load_data(file_url):
    data = pd.read_csv(file_url, sep=';')
    data = data[data['category'] != 'null']
    data = data[data['category'].notnull()]
    return data

# Função para calcular a similaridade entre dois textos usando spaCy
def calculate_similarity(text1, text2):
    nlp = spacy.load("en_core_web_sm")
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    similarity = doc1.similarity(doc2)
    return similarity

# Função principal do aplicativo
def main():
    st.title("Similaridade de Produtos")

    # URL do arquivo CSV no seu repositório do GitHub
    file_url = "streamlit/product-search-corpus-final.csv"

    # Carregar dados
    data = load_data(file_url)

    # Filtros para selecionar dois produtos
    product1_category = st.selectbox("Selecione a categoria do Produto 1", data["category"].unique())
    product1_title = st.selectbox("Selecione o título do Produto 1", data[data["category"] == product1_category]["title"].unique())

    product2_category = st.selectbox("Selecione a categoria do Produto 2", data["category"].unique())
    product2_title = st.selectbox("Selecione o título do Produto 2", data[data["category"] == product2_category]["title"].unique())

    # Obter dados dos produtos selecionados
    product1_data = data[(data["category"] == product1_category) & (data["title"] == product1_title)].iloc[0]
    product2_data = data[(data["category"] == product2_category) & (data["title"] == product2_title)].iloc[0]

    # Exibir informações dos produtos
    st.subheader("Produto 1:")
    st.write(product1_data)

    st.subheader("Produto 2:")
    st.write(product2_data)

    # Calcular e exibir a similaridade entre os textos dos produtos sem as chaves e aspas
    product1_data['features'] = product1_data['features'].apply(lambda x: x.replace('{', '').replace('}', '').replace('"', ''))
    product2_data['features'] = product2_data['features'].apply(lambda x: x.replace('{', '').replace('}', '').replace('"', ''))
    similarity_score = calculate_similarity((product1_data["features"] + '-' + product1_data["category"]), (product2_data["features"] + '-'  + product2_data["category"]))
    st.subheader("Similaridade entre os produtos:")
    st.write(f"A similaridade entre os produtos é: {similarity_score:.2%}")

if __name__ == "__main__":
    main()
