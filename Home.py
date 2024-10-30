"""
Módulo de visualização de dados por países do dashboard Elegant Restaurant.

Este módulo fornece uma interface visual para análise de dados de restaurantes
agrupados por país, incluindo:
- Métricas gerais por país
- Visualização geográfica de restaurantes
- Análises comparativas entre países

O módulo utiliza Streamlit para criar a interface e Plotly para as visualizações.
"""
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
    page_title='Home', 
    page_icon='🏠', 
    )   

df = pd.read_csv('dataset\zomato.csv')



# Funções de tratamento
def country_name(country_id):
    """
    Converte o código do país em seu nome correspondente.

    Parameters
    ----------
    country_id : int
        Código numérico que identifica o país.

    Returns
    -------
    str
        Nome do país correspondente ao código. Retorna "Unknown" se o código não for encontrado.

    Examples
    --------
    >>> country_name(1)
    'India'
    >>> country_name(999)
    'Unknown'
    """
    COUNTRIES = {
        1: "India", 14: "Australia", 30: "Brazil", 37: "Canada", 94: "Indonesia", 
        148: "New Zeland", 162: "Philippines", 166: "Qatar", 184: "Singapure", 
        189: "South Africa", 191: "Sri Lanka", 208: "Turkey", 214: "United Arab Emirates", 
        215: "England", 216: "United States of America",
    }
    return COUNTRIES.get(country_id, "Unknown")
def format_number(num):
    """
    Formata um número para uma string mais legível usando sufixos K e M.

    Parameters
    ----------
    num : int ou float
        Número a ser formatado.

    Returns
    -------
    str
        Número formatado com sufixo K para milhares ou M para milhões.

    Examples
    --------
    >>> format_number(1500)
    '1.5K'
    >>> format_number(1500000)
    '1.5M'
    >>> format_number(500)
    '500'
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"  # Exibe em milhões
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"  # Exibe em milhares
    else:
        return str(num)  # Retorna como string se for menor que mil

def create_price_type(price_range):
    """
    Converte o valor numérico da faixa de preço em uma categoria descritiva.

    Parameters
    ----------
    price_range : int
        Valor numérico de 1 a 4 representando a faixa de preço.

    Returns
    -------
    str
        Categoria de preço correspondente:
        - 1: "cheap"
        - 2: "normal"
        - 3: "expensive"
        - 4: "gourmet"

    Examples
    --------
    >>> create_price_type(1)
    'cheap'
    >>> create_price_type(4)
    'gourmet'
    """
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

def color_name(color_code):
    """
    Converte o código hexadecimal da cor em um nome descritivo.

    Parameters
    ----------
    color_code : str
        Código hexadecimal da cor (sem o #).

    Returns
    -------
    str
        Nome descritivo da cor. Retorna "unknown" se o código não for encontrado.

    Examples
    --------
    >>> color_name("3F7E00")
    'darkgreen'
    >>> color_name("INVALID")
    'unknown'
    """
    COLORS = {
        "3F7E00": "darkgreen", "5BA829": "green", "9ACD32": "lightgreen",
        "CDD614": "orange", "FFBA00": "red", "CBCBC8": "darkred", "FF7800": "darkred",
    }
    return COLORS.get(color_code, "unknown")

def rename_columns(dataframe):
    """
    Renomeia as colunas do DataFrame para o formato snake_case.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        DataFrame cujas colunas serão renomeadas.

    Returns
    -------
    pandas.DataFrame
        Cópia do DataFrame com as colunas renomeadas em formato snake_case.

    Examples
    --------
    >>> df = pd.DataFrame(columns=['First Name', 'Last Name'])
    >>> rename_columns(df).columns
    Index(['first_name', 'last_name'], dtype='object')
    """
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
    st.title('Elegant Restaurant')
    st.markdown('## Aqui você encontra os melhores restaurantes!')
    st.markdown("""---""")

    col1, col2, col3, col4, col5 = st.columns([2.2, 2, 2, 2,3 ], gap='large')  # Aumenta a largura da coluna 4

    
    with col1:
        #Restaurantes cadastrados.
        restaurantes_cadastrados = int(df['restaurant_id'].nunique())
        col1.metric('Restaurantes', restaurantes_cadastrados)
        
    with col2:
        #Países cadastrados.
        paises_cadastrados = int(df['country'].nunique())
        col2.metric('Países', paises_cadastrados)
        
    with col3:
        #Cidades cadastradas.
        cidades_cadastradas = int(df['city'].nunique())
        col3.metric('Cidades', cidades_cadastradas)
        
    with col4:
        # Avaliações feitas.
        avaliacoes_zomato = df['votes'].sum()
        formatted_votes = format_number(int(avaliacoes_zomato))
        col4.metric('Avaliações', formatted_votes)
        
    with col5:
        #Tipos de culinárias.
        tipos_culinarias = int(df['cuisines'].nunique())
        col5.metric('Tipos de culinárias', tipos_culinarias)
        
with st.container():
    st.markdown("""---""")
    st.markdown("### Country Maps")
    
    # Filtra o DataFrame para o país selecionado no selectbox
    if paises_selectbox == 'Todos os Países':
        df_pais = df  # Se "Todos os Países" estiver selecionado, use todo o DataFrame
    else:
        df_pais = df.loc[df['country'] == paises_selectbox, :]

    # Contagem de restaurantes no país selecionado
    total_restaurantes = df_pais.shape[0]

    # Inicia o mapa centralizado no país selecionado (média das localizações)
    if not df_pais.empty:
        central_location = [df_pais['latitude'].mean(), df_pais['longitude'].mean()]
        mapa = folium.Map(location=central_location, zoom_start=5)

        # Cluster de marcadores para agrupar os pontos dos restaurantes
        marker_cluster = MarkerCluster().add_to(mapa)
        
        # Adiciona marcadores para cada restaurante no país filtrado
        for index, location_info in df_pais.iterrows():
            folium.Marker(
                location=[location_info['latitude'], location_info['longitude']],
                popup=f"{location_info['restaurant_name']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

        # Adiciona marcador central com a contagem de restaurantes no país
        folium.Marker(
            location=central_location,
            popup=f"Total de restaurantes em {paises_selectbox}: {total_restaurantes}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(mapa)

        # Exibe o mapa no Streamlit
        folium_static(mapa, width=1024, height=600)
    else:
        st.write("Nenhum restaurante encontrado para o país selecionado.")

       


