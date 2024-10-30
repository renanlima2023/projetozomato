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
    page_title='Cidades', 
    page_icon='🏙️', 
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
st.header(' 🏙️Cidades')


# Carregar e exibir a imagem na barra lateral
#image_path = r'C:\Users\renan\OneDrive\DS\python\projetozomato\images\logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

# Exibir texto na barra lateral
st.sidebar.markdown('### Elegant Restaurant')
st.sidebar.markdown('## Food Experience')
st.sidebar.markdown("""---""")



#==================================
# Layout Streamlit
#==================================


with st.container():
    st.markdown("""---""")
    col1, col2, col3 = st.columns([1, 1, 1], gap='large')  # Define col1, col2 e col3

    with col1:
        # Filtro de seleção de país na barra lateral
        paises_selectbox = st.sidebar.selectbox(
            'Selecione o País',
            options=['Todos os Países'] + sorted(df['country'].unique().tolist()),  # Inclui opção para todos os países
            index=0,  # "Todos os Países" será a primeira opção
            key="country_select"
        )

# Filtrando o DataFrame de acordo com os filtros de país
if paises_selectbox == 'Todos os Países':
    # Contar o número de restaurantes em cada cidade globalmente
    cidades_counts = df['city'].value_counts().reset_index()
else:
    # Filtrar o DataFrame pelo país selecionado e contar o número de restaurantes em cada cidade
    df_filtrado = df[df['country'] == paises_selectbox]
    cidades_counts = df_filtrado['city'].value_counts().reset_index()

# Renomear as colunas
cidades_counts.columns = ['city', 'restaurant_count']

# Limitar às 10 cidades com mais restaurantes
top_10_cidades = cidades_counts.head(10)

# Criação do gráfico de barras
fig_cidades = px.bar(
    top_10_cidades,
    x='city',
    y='restaurant_count',
    text='restaurant_count',
    labels={'city': 'Cidade', 'restaurant_count': 'Número de Restaurantes'},
    title=f'Top 10 Cidades com Mais Restaurantes em {paises_selectbox}'
)

# Customização do gráfico
fig_cidades.update_traces(
    marker_color='lightblue',  # Cor das barras
    marker_line_color='black',  # Cor da borda das barras
    marker_line_width=1.5,  # Largura da borda
    textposition='outside'  # Posição do texto fora das barras
)

fig_cidades.update_layout(
    plot_bgcolor='rgb(22,31,44)',  # Cor de fundo do gráfico
    paper_bgcolor='rgb(22,31,44)',  # Cor de fundo fora do gráfico
    font=dict(color='white'),  # Cor do texto
    title_font=dict(size=18, color='white', family="Arial"),
    xaxis=dict(title='', color='white', showgrid=False),  # Remove título do eixo x e grades
    yaxis=dict(title='Número de Restaurantes', color='white', showgrid=True)  # Mantém título do eixo y
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig_cidades, use_container_width=True)

# Define uma nova linha para colunas col2 e col3
col2, col3 = st.columns([1, 1], gap='large')

with col2:
    # Filtro de restaurantes com avaliação média entre 4.0 e 4.9
    restaurantes_bem_avaliados = df[(df['aggregate_rating'] >= 4.0) & (df['aggregate_rating'] <= 4.9)]
    media_avaliacao = restaurantes_bem_avaliados.groupby('restaurant_name')['aggregate_rating'].mean().reset_index()
    media_avaliacao = media_avaliacao.sort_values(by='aggregate_rating', ascending=False).head(7)
     # Gráfico em col2
    fig_media_avaliacao = px.bar(
        media_avaliacao,
        x='restaurant_name',
        y='aggregate_rating',
        text='aggregate_rating',
        labels={'restaurant_name': 'Restaurante', 'aggregate_rating': 'Média de Avaliação'},
        title='Média de Avaliação por Restaurante ( entre 4.0 e 4.9)',
        width=600,  # Ajuste a largura
        height=400   # Ajuste a altura, se necessário
    )
    fig_media_avaliacao.update_traces(
        marker_color='lightgreen', 
        marker_line_color='white', 
        marker_line_width=1.5, 
        textposition='auto'
    )
    fig_media_avaliacao.update_layout(
        plot_bgcolor='rgb(22,31,44)', 
        paper_bgcolor='rgb(22,31,44)', 
        font=dict(color='white', size=12),  # Definindo a cor do texto para branco
        title_font=dict(size=15, color='white', family="Arial")  # Título em branco
    )
    st.plotly_chart(fig_media_avaliacao, use_container_width=True)

with col3:
    # Filtro de restaurantes com avaliação média entre 0 e 3.9
    restaurantes_mal_avaliados = df[(df['aggregate_rating'] >= 0) & (df['aggregate_rating'] <= 3.9)]
    media_avaliacao_mal = restaurantes_mal_avaliados.groupby('restaurant_name')['aggregate_rating'].mean().reset_index()
    media_avaliacao_mal = media_avaliacao_mal.sort_values(by='aggregate_rating', ascending=False).head(7)
    fig_media_avaliacao_mal = px.bar(
        media_avaliacao_mal,
        x='restaurant_name',
        y='aggregate_rating',
        text='aggregate_rating',
        labels={'restaurant_name': 'Restaurante', 'aggregate_rating': 'Média de Avaliação'},
        title='Média de Avaliação por Restaurante (entre 0 e 3.9)',
        width=600,  # Ajuste a largura
        height=400   # Ajuste a altura, se necessário
    )
    fig_media_avaliacao_mal.update_traces(
        marker_color='salmon', 
        marker_line_color='white', 
        marker_line_width=1.5, 
        textposition='auto'
    )
    fig_media_avaliacao_mal.update_layout(
        plot_bgcolor='rgb(22,31,44)', 
        paper_bgcolor='rgb(22,31,44)', 
        font=dict(color='white', size=12),  # Definindo a cor do texto para branco
        title_font=dict(size=15, color='white', family="Arial")  # Título em branco
    )
    st.plotly_chart(fig_media_avaliacao_mal, use_container_width=True)

# Finalmente, col4
with st.container():  # Criar um novo container para col4
    col4 = st.columns(1)  # Definindo col4 como uma única coluna

    with col4[0]:  # Usando o primeiro índice da lista de colunas
        # Cidades com mais restaurantes com tipos de culinária distintas
        df_filtrado_culinarias = df[df['cuisines'] != 'Not Informed']
        top_culinarias = df_filtrado_culinarias.groupby('city')['cuisines'].nunique().reset_index()
        top_culinarias.columns = ['Cidade', 'Quantidade de Culinárias Distintas']
        top_culinarias = top_culinarias.sort_values(by='Quantidade de Culinárias Distintas', ascending=False).head(10)
        fig_culinarias = px.bar(
            top_culinarias,
            x='Cidade',
            y='Quantidade de Culinárias Distintas',
            text='Quantidade de Culinárias Distintas',
            title='Top 10 Cidades com Mais Tipos de Culinária Distintas'
        )
        fig_culinarias.update_traces(marker_color='lightblue', marker_line_color='black', marker_line_width=1.5, textposition='outside')
        fig_culinarias.update_layout(plot_bgcolor='rgb(22,31,44)', paper_bgcolor='rgb(22,31,44)', font=dict(color='white'))
        st.plotly_chart(fig_culinarias, use_container_width=True)





