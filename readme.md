# Projeto Streamlit

Este projeto utiliza dados do Zomato para análises de restaurantes, distribuídos em diversas cidades e países. O objetivo é fornecer uma visão geral dos dados de restaurantes, permitindo a filtragem por país e cidade, bem como uma análise de avaliações e tipos de culinária.

# Requisitos 
- Python
- Git
-Streamlit

## Instalação

Siga etapas para ocnfigurar o projeto em sua máquina local:
1. Clone o repositório
````
git clone git@github.com:renanlima2023/projetozomato.git

````
2. Navegue até diretório do projeto:
````
cd projetozomato

````
3. Crie um ambiente virtual:
   ```
   python -m venv .venv
   ```

4. Ative o ambiente virtual:
   - No Windows:
     ```
     .venv\Scripts\activate
     ```
   - No macOS e Linux:
     ```
     source .venv/bin/activate
     ```

5. Instale as dependências do projeto (assumindo que existe um arquivo requirements.txt):
   ```
   pip install -r requirements.txt

   ```

## Uso

Para rodar o projeto execute o comando:
streamlit run Home.py

## Estrutura do Projeto 

 `dataset\zomato.csv`: Arquivo no formato csv.
 `images\logo.jpg`: Logotipo
 `pages\`: Contém arquivos auxiliares de tratamento de dados e visualização.
 `Home.py`: Script responsável pela lógica e exibição de dados por países.