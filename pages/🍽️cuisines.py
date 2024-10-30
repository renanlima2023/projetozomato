import pandas as pd
import numpy as np
import random
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
    page_title='Cozinhas', 
    page_icon='🍽️', 
    layout='wide'
    )

df = pd.read_csv('dataset/zomato.csv')



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
st.header(' 🍽️Cozinhas')


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

# Slider de seleção de quantidade de restaurantes
quantidade_restaurantes = st.sidebar.slider(
    'Selecione a quantidade de restaurantes',
    min_value=1,
    max_value=20,
    value=10
)

# Obtém as opções de culinária
cuisine_options = sorted(df['cuisines'].unique())

# Filtra as melhores culinárias com base nas avaliações
best_rated_cuisines = df.loc[df.groupby('cuisines')['aggregate_rating'].idxmax()]
top_cuisines = best_rated_cuisines.nlargest(5, 'aggregate_rating')['cuisines'].tolist()

# Seleciona as melhores como padrão
default_selection = top_cuisines

# Selecionar os tipos de culinária
culinarias_selectbox = st.sidebar.multiselect(
    'Selecione os tipos de culinária',
    options=cuisine_options,
    default=default_selection  # As melhores culinárias são selecionadas por padrão
)

#==================================
# Layout Streamlit
#==================================

with st.container():
    st.markdown('#### Aqui você encotras os principais tipos de culinária dos melhores restaurantes!')
    st.markdown("""---""")



# Filtra o DataFrame com base nas seleções do usuário
if culinarias_selectbox:
    # Filtra por país se não for "Todos os Países"
    if paises_selectbox != 'Todos os Países':
        filtered_restaurants = df[(df['country'] == paises_selectbox) & (df['cuisines'].isin(culinarias_selectbox))]
    else:
        filtered_restaurants = df[df['cuisines'].isin(culinarias_selectbox)]
    
    # Encontra as melhores avaliações por culinária nas opções filtradas
    if not filtered_restaurants.empty:
        best_rated_cuisines = filtered_restaurants.loc[filtered_restaurants.groupby('cuisines')['aggregate_rating'].idxmax()]
        
        # Ordena as culinárias por avaliação e seleciona as 5 melhores
        top_cuisines = best_rated_cuisines.nlargest(5, 'aggregate_rating')
        
        # Cria 5 colunas para exibir a melhor avaliação de cada culinária
        col1, col2, col3, col4, col5 = st.columns(5, gap='large')

        # Exibe cada culinária e sua nota na coluna correspondente
        with col1:
            if not top_cuisines.empty:
                cuisine1 = top_cuisines.iloc[0]
                st.markdown(f"**Culinária {cuisine1['cuisines']}**: {cuisine1['restaurant_name']} - {cuisine1['aggregate_rating']}/5.0")
            else:
                st.markdown("**Culinária 1**: Nenhum restaurante encontrado")

        with col2:
            if len(top_cuisines) > 1:
                cuisine2 = top_cuisines.iloc[1]
                st.markdown(f"**Culinária {cuisine2['cuisines']}**: {cuisine2['restaurant_name']} - {cuisine2['aggregate_rating']}/5.0")
            else:
                st.markdown("**Culinária 2**: Nenhum restaurante encontrado")

        with col3:
            if len(top_cuisines) > 2:
                cuisine3 = top_cuisines.iloc[2]
                st.markdown(f"**Culinária {cuisine3['cuisines']}**: {cuisine3['restaurant_name']} - {cuisine3['aggregate_rating']}/5.0")
            else:
                st.markdown("**Culinária 3**: Nenhum restaurante encontrado")

        with col4:
            if len(top_cuisines) > 3:
                cuisine4 = top_cuisines.iloc[3]
                st.markdown(f"**Culinária {cuisine4['cuisines']}**: {cuisine4['restaurant_name']} - {cuisine4['aggregate_rating']}/5.0")
            else:
                st.markdown("**Culinária 4**: Nenhum restaurante encontrado")

        with col5:
            if len(top_cuisines) > 4:
                cuisine5 = top_cuisines.iloc[4]
                st.markdown(f"**Culinária {cuisine5['cuisines']}**: {cuisine5['restaurant_name']} - {cuisine5['aggregate_rating']}/5.0")
            else:
                st.markdown("**Culinária 5**: Nenhum restaurante encontrado")
    else:
        st.markdown("Nenhum restaurante encontrado com os filtros aplicados.")
else:
    st.markdown("Por favor, selecione ao menos uma culinária.")


# Mostra os 10 melhores restaurantes sem depender do top_cuisines
with st.container():
    st.markdown("""---""")
    
    # Define o título com base na quantidade de restaurantes a serem exibidos
    st.markdown(f"### Top {quantidade_restaurantes} Melhores Restaurantes:")

    # Aplica o filtro de país se selecionado
    if paises_selectbox != 'Todos os Países':
        # Filtra para o país selecionado
        filtered_restaurants = df[df['country'] == paises_selectbox]
    else:
        # Se "Todos os Países" estiver selecionado, use o DataFrame completo
        filtered_restaurants = df

    # Filtra os melhores restaurantes de acordo com a avaliação
    best_overall = filtered_restaurants.nlargest(quantidade_restaurantes, 'aggregate_rating')

    # Verifica se há restaurantes disponíveis após o filtro
    if best_overall.empty:
        st.markdown("Nenhum restaurante encontrado para o país selecionado.")
    else:
        # Mostra as colunas desejadas
        st.dataframe(best_overall[['restaurant_name', 'country', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating']])

    
with st.container():
    st.markdown("""---""")
    st.markdown("### Top 10 Melhores Tipos de Culinária:")
    
    # Calcula a média de avaliação por culinária e arredonda para 1 casa decimal
    average_ratings = df.groupby('cuisines', as_index=False)['aggregate_rating'].mean().round(1)
    
    # Seleciona as 10 melhores culinárias com base na média de avaliação
    top_cuisines = average_ratings.nlargest(10, 'aggregate_rating')     
    
    # Verifica se há culinárias suficientes para exibir
    if top_cuisines.empty:
        st.markdown("Nenhuma culinária encontrada.")
    else:
        # Cria o gráfico
        fig = px.bar(
            top_cuisines, 
            x='cuisines', 
            y='aggregate_rating', 
            text='aggregate_rating', 
            color='aggregate_rating', 
            title='Top 10 Melhores Tipos de Culinária (Baseado na Média de Avaliação)'
        )
        
        # Arredonda os valores exibidos no gráfico para uma casa decimal
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)


  

with st.container():
    st.markdown("""---""")
    st.markdown("### Top 10 Piores Tipos de Culinária:")
    
    # Calcula a média de avaliação por culinária e arredonda para 1 casa decimal
    average_ratings = df.groupby('cuisines', as_index=False)['aggregate_rating'].mean().round(1)
    
    # Seleciona as 10 piores culinárias com base na média de avaliação
    bottom_cuisines = average_ratings.nsmallest(10, 'aggregate_rating')
    
    # Verifica se há culinárias suficientes para exibir
    if bottom_cuisines.empty:
        st.markdown("Nenhuma culinária encontrada.")
    else:
        # Cria o gráfico com cores modificadas
        fig = px.bar(
            bottom_cuisines, 
            x='cuisines', 
            y='aggregate_rating', 
            text='aggregate_rating', 
            color='aggregate_rating', 
            title='Top 10 Piores Tipos de Culinária',
            color_continuous_scale=px.colors.sequential.Reds  # Usando a paleta de cores vermelha
        )
        
        # Arredonda os valores exibidos no gráfico para uma casa decimal
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)



