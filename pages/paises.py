import pandas as pd
import numpy as np
import streamlit as st
from haversine import haversine
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title='Países', 
    page_icon='🌍', 
    layout='wide'
    )

df = pd.read_csv('dataset\zomato.csv')





# Funções de tratamento
def country_name(country_id):
    COUNTRIES = {
        1: "India", 14: "Australia", 30: "Brazil", 37: "Canada", 94: "Indonesia", 
        148: "New Zeland", 162: "Philippines", 166: "Qatar", 184: "Singapure", 
        189: "South Africa", 191: "Sri Lanka", 208: "Turkey", 214: "United Arab Emirates", 
        215: "England", 216: "United States of America",
    }
    return COUNTRIES.get(country_id, "Unknown")

def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

def color_name(color_code):
    COLORS = {
        "3F7E00": "darkgreen", "5BA829": "green", "9ACD32": "lightgreen",
        "CDD614": "orange", "FFBA00": "red", "CBCBC8": "darkred", "FF7800": "darkred",
    }
    return COLORS.get(color_code, "unknown")

def rename_columns(dataframe):
    df = dataframe.copy()
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    return df

# 1. Remoção de duplicatas
df = df.drop_duplicates(subset='Restaurant ID')

# 2. Tratamento de valores nulos
df['Cuisines'] = df['Cuisines'].fillna('Not Informed')
df['Rating text'] = df['Rating text'].fillna('Not Rated')
df['Average Cost for two'] = df['Average Cost for two'].fillna(0)

# 3. Conversão de tipos
df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce')
df['Average Cost for two'] = pd.to_numeric(df['Average Cost for two'], errors='coerce')
df['Aggregate rating'] = pd.to_numeric(df['Aggregate rating'], errors='coerce')

# 4. Substituição de códigos por nomes
df['country_name'] = df['Country Code'].apply(country_name)
df['Price Category'] = df['Price range'].apply(create_price_type)
df['Color Name'] = df['Rating color'].apply(color_name)


# 5. Tratamento da coluna Cuisines (pegando apenas a primeira culinária)
df['Cuisines'] = df['Cuisines'].apply(lambda x: str(x).split(',')[0].strip())

# 6. Renomeação das colunas para snake_case
df = rename_columns(df)
# Após renomeação, ajuste o nome da coluna 'country_name' para 'country'
df.rename(columns={'country_name': 'country'}, inplace=True)

# 7. Remoção de colunas redundantes ou desnecessárias
colunas_para_remover = ['country_code', 'rating_color', 'switch_to_order_menu']
df = df.drop(columns=colunas_para_remover)

# 8. Ordenação do dataframe
df = df.sort_values('restaurant_id')

# 9. Reset do índice
df = df.reset_index(drop=True)

# Verificação dos dados tratados
#print("Shape após tratamento:", df.shape)
#print("\nInformações do DataFrame:")
#print(df.info())



#==================================
# Barra Lateral Streamlit
#==================================
st.header(' 🌍 Países')


# Carregar e exibir a imagem na barra lateral
#image_path = r'C:\Users\renan\OneDrive\DS\python\projetozomato\images\logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

# Exibir texto na barra lateral
st.sidebar.markdown('### Elegant Restaurant')
st.sidebar.markdown('## Food Experience')
st.sidebar.markdown("""---""")

options = ['Todos os Países'] + sorted(df['country'].unique())

# Filtro de seleção de país na barra lateral
paises_selectbox = st.sidebar.selectbox(
    'Selecione o País',
    options=options, 
    index=0  # "Todos" será a primeira opção
)



#==================================
# Layout Streamlit
#==================================

with st.container():
    st.markdown("""---""")
    col1, col2= st.columns(2, gap='large')
    

    with col1:
        
        # Contagem de restaurantes por país e seleção dos 6 maiores
        country_counts = df['country'].value_counts().reset_index()
        country_counts.columns = ['País', 'Quantidade de Restaurantes']
        country_counts = country_counts.sort_values('Quantidade de Restaurantes', ascending=False).head(6)  # Mantém apenas os 6 primeiros

# ==================================
# Gráfico de Barras com Plotly Express
# ==================================
fig = px.bar(
    country_counts,
    x='País',
    y='Quantidade de Restaurantes',
    text='Quantidade de Restaurantes',  # Adiciona os números dentro das barras
    labels={'País': 'País', 'Quantidade de Restaurantes': 'Quantidade de Restaurantes'},
    title='Quantidade de Restaurantes Registrados por País'
)

# Customização para aproximar do visual da imagem
fig.update_traces(
    marker_color='blue',  # Cor das barras
    marker_line_color='black',  # Cor da borda das barras
    marker_line_width=1.5,  # Largura da borda
    textposition='outside'  # Posição do texto fora das barras
)

fig.update_layout(
    plot_bgcolor='rgb(22,31,44)',  # Cor de fundo do gráfico
    paper_bgcolor='rgb(22,31,44)',  # Cor de fundo fora do gráfico
    font=dict(color='white'),  # Cor do texto
    title_font=dict(size=18, color='white', family="Arial"),
    xaxis=dict(title='', color='white', showgrid=False),  # Remove título do eixo x e grades
    yaxis=dict(title='', color='white', showgrid=False)  # Remove título do eixo y e grades
)

# ==================================
# Exibi o gráfico no Streamlit
# ==================================
st.plotly_chart(fig, use_container_width=True)

with col2:
    
    # Contagem de cidades únicas por país e seleção dos 6 maiores
    
    city_counts = df.groupby('country')['city'].nunique().reset_index()
    city_counts.columns = ['País', 'Quantidade de Cidades']
    city_counts = city_counts.sort_values('Quantidade de Cidades', ascending=False).head(6)  # Mantém apenas os 6 primeiros

# ==================================
# Gráfico de Barras com Plotly Express
# ==================================
fig = px.bar(
    city_counts,
    x='País',
    y='Quantidade de Cidades',
    text='Quantidade de Cidades',  # Adiciona os números dentro das barras
    labels={'País': 'País', 'Quantidade de Cidades': 'Quantidade de Cidades'},
    title='Quantidade de Cidades Registradas por País'
)

# Customização para aproximar do visual da imagem
fig.update_traces(
    marker_color='blue',  # Cor das barras
    marker_line_color='black',  # Cor da borda das barras
    marker_line_width=1.5,  # Largura da borda
    textposition='outside'  # Posição do texto fora das barras
)

fig.update_layout(
    plot_bgcolor='rgb(22,31,44)',  # Cor de fundo do gráfico
    paper_bgcolor='rgb(22,31,44)',  # Cor de fundo fora do gráfico
    font=dict(color='white'),  # Cor do texto
    title_font=dict(size=18, color='white', family="Arial"),
    xaxis=dict(title='', color='white', showgrid=False),  # Remove título do eixo x e grades
    yaxis=dict(title='', color='white', showgrid=False)  # Remove título do eixo y e grades
)

# ==================================
# Exibir o gráfico no Streamlit
# ==================================
st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.markdown("""---""")
    col1, col2= st.columns(2, gap='large')      

    with col1:
        #Média de avaliações feitas por país
        
  
  
# Cálculo da média de avaliações por país
        average_votes = df.groupby('country')['votes'].mean().reset_index()
        average_votes.columns = ['País', 'Média de Avaliações']

        # Mantém apenas os 6 países com as maiores médias de avaliações
    average_votes = average_votes.sort_values('Média de Avaliações', ascending=False).head(6)

# Criação do gráfico de barras
fig = px.bar(
    average_votes,
    x='País',
    y='Média de Avaliações',
    text='Média de Avaliações',
    labels={'País': 'País', 'Média de Avaliações': 'Média de Avaliações'},
    title='Média de Avaliações Feitas por País '
)

# Customização do gráfico
fig.update_traces(
    
    marker_color='blue',  # Cor das barras
    marker_line_color='black',  # Cor da borda das barras
    marker_line_width=1.5,  # Largura da borda
    textposition='outside'  # Posição do texto fora das barras
)

fig.update_layout(
    plot_bgcolor='rgb(22,31,44)',  # Cor de fundo do gráfico
    paper_bgcolor='rgb(22,31,44)',  # Cor de fundo fora do gráfico
    font=dict(color='white'),  # Cor do texto
    title_font=dict(size=18, color='white', family="Arial"),
    xaxis=dict(title='', color='white', showgrid=False),  # Remove título do eixo x e grades
    yaxis=dict(title='', color='white', showgrid=False)  # Remove título do eixo y e grades
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)


with col2:
        # Média de preço de um prato para duas pessoas por país.
        
    # Cálculo da média do preço de um prato para duas pessoas por país
    average_cost = df.groupby('country')['average_cost_for_two'].mean().reset_index()
    average_cost.columns = ['País', 'Média de Preço para Duas Pessoas']

# Mantém apenas os 6 países com as maiores médias de preço
    average_cost = average_cost.sort_values('Média de Preço para Duas Pessoas', ascending=False).head(6)

# Criação do gráfico de barras
fig_cost = px.bar(
    average_cost,
    x='País',
    y='Média de Preço para Duas Pessoas',
    text='Média de Preço para Duas Pessoas',
    labels={'País': 'País', 'Média de Preço para Duas Pessoas': 'Média de Preço'},
    title='Média de Preço de um Prato para Duas Pessoas por País '
)

# Customização do gráfico
fig_cost.update_traces(
    marker_color='blue',  # Cor das barras
    marker_line_color='black',  # Cor da borda das barras
    marker_line_width=1.5,  # Largura da borda
    textposition='outside'  # Posição do texto fora das barras
)

fig_cost.update_layout(
    plot_bgcolor='rgb(22,31,44)',  # Cor de fundo do gráfico
    paper_bgcolor='rgb(22,31,44)',  # Cor de fundo fora do gráfico
    font=dict(color='white'),  # Cor do texto
    title_font=dict(size=18, color='white', family="Arial"),
    xaxis=dict(title='', color='white', showgrid=False),  # Remove título do eixo x e grades
    yaxis=dict(title='', color='white', showgrid=False)  # Remove título do eixo y e grades
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig_cost, use_container_width=True)
    

