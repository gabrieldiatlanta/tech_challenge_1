import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout = 'wide')

## Funções

def formata_valor(valor):
    return f'US$ {round(valor,2):,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

def formata_numero(numero):
    return "{:,}".format(numero).replace(',', '.')

# Função para verificar se a Quantidade é crescente dentro de cada grupo
def is_increasing(group):
    return group['Quantidade'].is_monotonic_increasing

def plota_grafico_pais_valor_ano_linha(data, cor, pais, divisor=1):
    sns.lineplot(x=data['Ano'], y=data['Valor']/divisor, data=data, marker='o', lw=3, color=cor)
    # Adiciona título
    if divisor == 1:
        ax.set_title(f'Total em dólares (US$) de vinhos importados pelo(a) {pais}', loc='left', fontsize=12)
    elif divisor == 1_000_000:
        ax.set_title(f'Total em milhões de dólares (US$) de vinhos importados pelo(a) {pais}', loc='left', fontsize=12)

    # Configurações adicionais do gráfico
    ax.set_xlabel('', fontsize=10)
    ax.set_ylabel('Valor em dólares', fontsize=10)
    ax.set_xticks(data['Ano'])

    # Ajusta o tamanho da fonte dos ticks
    ax.tick_params(axis='x', labelsize=8)  # Tamanho da fonte dos ticks do eixo x
    ax.tick_params(axis='y', labelsize=8)  # Tamanho da fonte dos ticks do eixo y
    plt.xticks(rotation=45)

    sns.despine()
    ax.grid(True, linestyle='--') 

## Manipulação e criação do dataframe

df = pd.read_csv('ExpVinho.csv',sep=';')

# Criando uma lista de anos duplicados
anos = [str(ano) for ano in range(1970, 2024)]

# Inicializando listas para armazenar os resultados
ids = []
paises = []
anos_list = []
quantidades = []
valores = []

# Iterando sobre cada linha do DataFrame
for i, row in df.iterrows():
    id_pais = row[:2]
    for ano_index in range(len(anos)):
        ids.append(id_pais[0])
        paises.append(id_pais[1])
        anos_list.append(anos[ano_index])
        quantidades.append(row[2 + 2 * ano_index])
        valores.append(row[2 + 2 * ano_index + 1])

# Criando o DataFrame resultante
df_resultado = pd.DataFrame({
    'Id': ids,
    'País': paises,
    'Ano': anos_list,
    'Quantidade': quantidades,
    'Valor': valores
})

# Convertendo a coluna 'Ano' de string para inteiro
df_resultado['Ano'] = df_resultado['Ano'].astype(int)

#adicionando a coluna Brasil
df_resultado['Pais Origem'] = 'Brasil'

#reordenando as colunas
# Reordenando as colunas
new_order = ['Id', 'Pais Origem', 'País', 'Ano', 'Quantidade', 'Valor']
df_resultado = df_resultado[new_order]

df_resultado.columns = ['Id', 'Origem', 'Destino', 'Ano', 'Quantidade', 'Valor']

#filtrando apenas a partir do ano 2009
df_resultado = df_resultado.query('Ano >= 2009')

df_resultado_agrupado_destino = df_resultado.groupby(by=['Origem','Destino']).sum(['Quantidade','Valor']).reset_index()

df_resultado_agrupado_destino.drop(['Ano','Id'],axis=1,inplace=True)

#ordenar por Quantidade e Valor
df_resultado_agrupado_destino = df_resultado_agrupado_destino.sort_values(by=['Valor','Quantidade'], ascending=False).reset_index(drop=True)

#agrupamento por ano
df_exp_por_ano = df_resultado.groupby('Ano').sum(['Quantidade', 'Valor'])
df_exp_por_ano = df_exp_por_ano.drop('Id', axis=1)
df_exp_por_ano = df_exp_por_ano.reset_index()

#dataframe criado para analisar os países em crescimento
df_resultado_analise_crescimento = df_resultado.copy()

# manter no dataframe apenas os paises nos quais a quantidade de exportação segue sempre em crescimento
# Função para verificar se a Quantidade é crescente dentro de cada grupo
# Agrupar por Destino e aplicar a função de verificação
df_resultado_analise_crescimento_apos_filtro = df_resultado_analise_crescimento.groupby('Destino').filter(is_increasing)
df_analise_crescimento = df_resultado_analise_crescimento_apos_filtro.query('Destino != "Brasil"')
# Agrupar por Destino e calcular o somatório de Quantidade para cada grupo
quantity_sum = df_analise_crescimento.groupby('Destino')['Quantidade'].sum()

# Filtrar os Destinos cujo somatório de Quantidade é >= 100
valid_destinos = quantity_sum[quantity_sum >= 100].index

# Manter apenas as linhas do dataframe original com os Destinos válidos
df_analise_crescimento = df_analise_crescimento[df_analise_crescimento['Destino'].isin(valid_destinos)]
df_analise_crescimento = df_analise_crescimento.query('Ano >= 2018')

# Montando os dataframes dos 3 países que apresentam crescimento acima de 100 dólares

df_arabia_saudita = df_analise_crescimento.query('Destino == "Arábia Saudita"')
df_liberia = df_analise_crescimento.query('Destino == "Libéria"')
df_malavi = df_analise_crescimento.query('Destino == "Malavi"')

# Montando os dataframes dos top-6 importadores
df_paraguai = df_resultado.query('Destino == "Paraguai"')
df_russia = df_resultado.query('Destino == "Rússia"')
df_estados_unidos = df_resultado.query('Destino == "Estados Unidos"')
df_china = df_resultado.query('Destino == "China"')
df_reino_unido = df_resultado.query('Destino == "Reino Unido"')
df_espanha = df_resultado.query('Destino == "Espanha"')

## Front-end

st.title("Análise da exportação de vinhos de mesa da Vinícola")
st.write("""
Prezados(as) investidores e acionistas,

Apresentamos aos senhores(as) a análise da nossa recém-criada área de Data Analytics, cujo foco é apoiar nossa empresa na tomada de decisões estratégicas e no fortalecimento de nossa posição no mercado global de vinhos.

Nosso objetivo é fornecer uma visão detalhada e informada sobre as exportações de vinhos, destacando não apenas os volumes exportados, mas também os fatores externos que podem impactar nosso desempenho.

Com base em dados dos últimos 15 anos (2009 a 2023), analisamos a quantidade em litros de vinhos exportados para diferentes regiões do mundo, além dos valores em dólares (US$) das exportações.

Segue abaixo a tabela contendo as informações de país de origem, país de destino, quantidade em litros de vinho exportado e o valor em US$, ordenados de forma decrescente em relação aos valores:
""")


df_formatado = df_resultado_agrupado_destino.copy()
df_formatado['Valor'] = df_formatado['Valor'].map(formata_valor)
df_formatado['Quantidade'] = df_formatado['Quantidade'].map(formata_numero)

st.dataframe(df_formatado, width=1250)

st.write("""
A análise inicial aborda o volume total de litros de vinho exportados anualmente nos últimos 15 anos, oferecendo uma visão detalhada das tendências ao longo do tempo nessa variável específica.

Ao analisar esses dados, é possível identificar movimentações significativas, fornecendo insights valiosos sobre o desempenho da Vinícola.

Segundo o gráfico 'Total em quantidade (litros) de vinhos exportados' abaixo, observamos um alto pico de exportações em 2009, correspondente a aproximadamente 25 milhões de litros exportados. Um dos motivos significativos que impactaram nesse cenário foi o estabelecimento de mecanismos, através do PEP (Prêmio de Escoamento da Produção do Governo Federal), para impulsionar a comercialização, resultando em um alto crescimento [1] [2].

Isso demonstra a importância de estabelecer parcerias estratégicas e atuar junto ao Governo Federal para a criação de políticas econômicas favoráveis ao setor, destacando como a colaboração entre o setor público e privado pode resultar em benefícios significativos para a Vinícola.
""")

fig, ax = plt.subplots(figsize=(6, 3))

sns.lineplot(x=df_exp_por_ano['Ano'], y=df_exp_por_ano['Quantidade']/1000000, data=df_exp_por_ano, marker='o', lw=3, color='purple')

# Adiciona título
ax.set_title('Total em quantidade (litros) de vinhos exportados', loc='left', fontsize=12)

# Configurações adicionais do gráfico
ax.set_xlabel('', fontsize=10)
ax.set_ylabel('Quantidade em milhões de litros', fontsize=10)
ax.set_xticks(df_exp_por_ano['Ano'])
ax.set_ylim(0, 30)

# Ajusta o tamanho da fonte dos ticks
ax.tick_params(axis='x', labelsize=8)  # Tamanho da fonte dos ticks do eixo x
ax.tick_params(axis='y', labelsize=8)  # Tamanho da fonte dos ticks do eixo y
plt.xticks(rotation=45)

sns.despine()
ax.grid(True, linestyle='--') 

# Mostrando o gráfico no Streamlit
st.pyplot(fig)

st.write("""
Além disso, no gráfico 'Total em dólares (US$) de vinhos exportados', abaixo apresentado, verificamos em 2013 um recorde do valor das exportações em dólares de mais de 22,5 milhões de dólares, um aumento de mais de quatro vezes o valor de exportação no ano anterior.

Uma das justificativas desse recorde é o foco na construção da imagem da marca como produtora de vinhos de alta qualidade, além da abertura de novos canais de distribuição que fortalecem o aumento do volume exportado, seguindo o exemplo de nossa concorrente, o Grupo Miolo [3].

Isso nos leva a concluir a importância do investimento em marketing e promoção, na participação em feiras e eventos, no estabelecimento de parcerias e representantes locais nos países-alvos, e na garantia de uma infraestrutura logística eficiente e confiável.
""")

fig, ax = plt.subplots(figsize=(6, 3.08))

sns.lineplot(x=df_exp_por_ano['Ano'], y=df_exp_por_ano['Valor']/1000000, data=df_exp_por_ano, marker='o', lw=3, color='green')

# Adiciona título
ax.set_title('Total em dólares (US$) de vinhos exportados', loc='left', fontsize=12)

# Configurações adicionais do gráfico
ax.set_xlabel('', fontsize=10)
ax.set_ylabel('Valor em milhões de dólares', fontsize=10)
ax.set_xticks(df_exp_por_ano['Ano'])
ax.set_ylim(0, 25)

# Ajusta o tamanho da fonte dos ticks
ax.tick_params(axis='x', labelsize=8)  # Tamanho da fonte dos ticks do eixo x
ax.tick_params(axis='y', labelsize=8)  # Tamanho da fonte dos ticks do eixo y
plt.xticks(rotation=45)

sns.despine()
ax.grid(True, linestyle='--') 

# Mostrando o gráfico no Streamlit
st.pyplot(fig)

st.write("""
Prosseguindo com a análise, o gráfico abaixo apresenta os 10 maiores exportadores de vinho da Vinícola em termos de valor em dólares (US$) de 2009 à 2023:
""")

# Gráfico de barras do top 10 importadores   

fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(x=df_resultado_agrupado_destino['Valor'].head(10) / 1000000,
            y=df_resultado_agrupado_destino['Destino'].head(10),
            data=df_resultado_agrupado_destino, orient='h',
            hue=df_resultado_agrupado_destino['Destino'].head(10),
            palette='viridis')

# Configurações adicionais do gráfico
ax.set_xlabel('', fontsize=18)
ax.set_ylabel('', fontsize=18)
ax.set_xlim(0, 55)

# Ajusta o tamanho da fonte dos ticks
ax.tick_params(bottom=False, labelbottom=False)
ax.tick_params(axis='y', labelsize=14)  # Tamanho da fonte dos ticks do eixo y

# Adiciona título
ax.set_title('Top 10 maiores importadores de vinho em dólares (US$)\n2009 à 2023', loc='left', fontsize=20)

# Adicionar os valores no final das barras
for index, value in enumerate(df_resultado_agrupado_destino['Valor'].head(10) / 1000000):
    ax.text(value, index, f'{round(value,2)} milhões de doláres', va='center', ha='left')

sns.despine()
ax.grid(True, linestyle='--') 

# Mostrando o gráfico no Streamlit
st.pyplot(fig)

st.write("""
O Paraguai se destaca como o maior importador de vinho da Vinícola, com um valor total de 42,86 milhões de dólares. Isso ressalta a forte demanda do Paraguai por nossos vinhos.
         
Rússia ocupa o segundo lugar, importando vinhos do Brasil no valor de 23,15 milhões de dólares. A diferença entre o Paraguai e Rússia é significativa, com o Paraguai importando quase o dobro do valor.
         
Estados Unidos é o terceiro maior importador, com 9,31 milhões de dólares, seguido por China (4,9 milhões de dólares) e Reino Unido (4,64 milhões de dólares). Esses países mostram uma demanda moderada por nossos vinhos.

Outros países na lista incluem Espanha (3,81 milhões de dólares), Haiti (3,2 milhões de dólares), Países Baixos (3,01 milhões de dólares), Japão (2,26 milhões de dólares) e Alemanha (2,15 milhões de dólares).

Observa-se uma grande diferença nos valores de importação entre os dois primeiros países (Paraguai e Rússia) e os demais países na lista. O valor de exportação para os Estados Unidos, por exemplo, é menos da metade do valor exportado para a Rússia.
""")

 

st.write("""
Aprofundando a análise nos 6 maiores importadores da Vinícola, apresentamos em gráficos as movimentações dos valores de exportação ao longo dos anos:
""")

coluna1, coluna2, coluna3 = st.columns(3)

with coluna1:
    fig, ax = plt.subplots(figsize=(6, 3.4))

    plota_grafico_pais_valor_ano_linha(df_paraguai, "red", "Paraguai", 1_000_000)
    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(6, 3.05))

    plota_grafico_pais_valor_ano_linha(df_china, "gold", "China", 1_000_000)
    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

with coluna2:
    fig, ax = plt.subplots(figsize=(6, 3.35))

    plota_grafico_pais_valor_ano_linha(df_russia, "blue", "Rússia", 1_000_000)

    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(6, 3.35))

    plota_grafico_pais_valor_ano_linha(df_reino_unido, "pink", "Reino Unido", 1_000_000)
    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

with coluna3:
    fig, ax = plt.subplots(figsize=(6, 3.05))

    plota_grafico_pais_valor_ano_linha(df_estados_unidos, "black", "Estados Unidos")

    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(6, 3.15))

    plota_grafico_pais_valor_ano_linha(df_reino_unido, "green", "Espanha", 1_000_000)
    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

st.write("""
Considerando os dados apresentados, com finalidade de buscar insights valiosos para a Vinícola, realizamos o mapeamento das forças, fraquezas, oportunidades e ameaças (SWOT).         
         """)

st.subheader("Forças")

st.write("""
Apesar do Paraguai apresentar uma declínio nas importações de 2021 à 2023, no geral apresenta uma tendência de crescimento, que mostra uma forte e consistente demanda ao longo dos anos. Demonstrando assim uma base sólida de consumidores nesse mercado.
         
Picos notáveis em certos anos, como os da Rússia, Estados Unidos Reino Unido e Espanha, indicam a capacidade da vinícola de capitalizar oportunidades de mercado quando surgem.         
         """)

st.subheader("Fraquezas")

st.write("""

O gráfico da Rússia mostra picos seguidos de quedas acentuadas, indicando vulnerabilidade às flutuações econômicas e políticas que afetam as exportações, como por exemplo o impacto da Guerra Russo-Ucraniana em 2014 e 2022 nas importações de vinho. [4]

A China e os Estados Unidos mostram flutuações frequentes, sugerindo uma falta de estabilidade na demanda.

Além desses pontos, a Vinícola deve ficar atenta a forte dependência de mercados como o do Paraguai, pois pode comprometer as receitas se houver mudanças políticas, econômicas ou regulatórias adversas nesse país. Inclusive mudanças no perfil do consumidor ou potenciais concorrências que possam afetar nossa posição.
""")

st.subheader("Oportunidades")

st.write("""

Verificamos uma expansão e estabilização em mercados emergentes. Mercados como o da China mostram um crescimento potencial, apesar de valores absolutos menores, sugerindo que há espaço para aumentar a penetração de mercado com estratégias adequadas de marketing e distribuição.

Além disso, destacamos a exploração de novos mercados, que serão analisados de forma oportuna nessa apresentação.
""")

st.subheader("Ameaças")

st.write("""

Mercados como a da Rússia são altamente voláteis devido a questões políticas e econômicas que podem impactar severamente as exportações

A crescente competição de outros países produtores de vinho pode ameaçar a participação de mercado da Vinícola, especialmente em mercados onde as flutuações são grandes, como dos Estados Unidos e da China.
         
""")



st.write("""

É crucial reconhecer que, embora existam mercados fortes como o Paraguai e oportunidades em expansão como a China, há também riscos consideráveis devido à volatilidade e dependência de mercados específicos.

Estratégias para estabilizar mercados voláteis, diversificar a base de consumidores e investir em marketing focado em qualidade e valor serão fundamentais para sustentar e aumentar o crescimento das exportações.

Assim apresentamos abaixo 3 mercados que merecem uma atenção especial:
                  
""")

coluna1, coluna2, coluna3 = st.columns(3)

with coluna1:
    fig, ax = plt.subplots(figsize=(6, 3.08))

    plota_grafico_pais_valor_ano_linha(df_liberia, "red", "Libéria")
    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

with coluna2:
    fig, ax = plt.subplots(figsize=(6, 3.48))

    plota_grafico_pais_valor_ano_linha(df_arabia_saudita, "green", "Arábia Saudita")

    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

with coluna3:
    fig, ax = plt.subplots(figsize=(6, 3.05))

    plota_grafico_pais_valor_ano_linha(df_malavi, "black", "Malavi")

    # Mostrando o gráfico no Streamlit
    st.pyplot(fig)

st.write("""

Analisando o mercado da Libéria, observamos uma tendência de crescimento consistente desde 2018. No entanto, verificamos que a Vinícola ainda pode explorar melhor esse mercado, visto que o Brasil não está entre os maiores exportadores de vinho para o país. [5]

Constatamos, portanto, que existe uma demanda interna significativa pelo consumo de vinho na Libéria. Assim, a Vinícola deve direcionar um foco especial para esse mercado, com o objetivo de aprimorar as estratégias e métodos para uma maior exploração e penetração.

Ressaltamos também que em 2023 a Vinícola exportou pela primeira vez em 15 anos para novos países, destacando entre esses, a Arábia Saudita e o Malavi.        

Na Arábia Saudita houve uma abertura econômica, o país tem implementado uma série de reformas para modernizar a economia e atrair turistas. Isso inclui a possível flexibilização das leis sobre bebidas alcoólicas em resorts específicos, o que pode ter criado uma nova demanda por vinhos importados. [6]

Além disso, o exemplo do Malavi demonstra a importância da diversificação dos mercados de exportação, com intuito de reduzir a dependência de mercados tradicionais e explorar novas oportunidades. Isso inclui iniciativas para promover nossos produtos em regiões menos exploradas, como a África e o Oriente Médio.

A Vinícola tem potencial para ganhar espaço no mercado de vinhos da Libéria, Arábia Saudita e Malavi, além de outros países não tradicionais. Especialmente se investimos em entender o mercado local, estabelecer boas parcerias e promover a qualidade dos nossos produtos.       
                  
""")

st.subheader("Conclusão")

st.write("""

A análise das exportações de vinhos da Vinícola entre 2009 e 2023 destaca um crescimento consistente em mercados como a Libéria e o surgimento de novos mercados como a Arábia Saudita e o Malavi, que apresentam grandes potenciais ainda pouco explorados.

Apesar de forças como a demanda estável do Paraguai e picos de importação em outros países, há fraquezas notáveis, como a volatilidade política e econômica na Rússia e flutuações nas importações da China e Estados Unidos.
         
A Vinícola deve focar em estratégias de marketing robustas e parcerias estratégicas para expandir em mercados emergentes e estabilizar as exportações, maximizando o crescimento global e diversificando mercados para reduzir a dependência de mercados tradicionais.
                 
""")

st.info("Análise realizada pelo Grupo 1 - Integrantes: Antônio Gabriel Di Atlanta Valente e Vanessa Larize Alves de Carvalho")
st.write("Referências:")
st.write("[1] https://comexdobrasil.com/mercado-mostra-reacao-na-comercializacao-de-vinhos-em-2009/")
st.write("[2] https://revistacultivar.com.br/artigos/atuacao-do-brasil-no-mercado-vitivinicola-mundial-n-panorama-2009")
st.write("[3] https://www.meuvinho.com.br/news/547/grupo-miolo-atinge-valor-recorde-nas-exportacoes-em-2013%21")
st.write("[4] https://pt.wikipedia.org/wiki/Guerra_Russo-Ucraniana")
st.write("[5] https://oec.world/en/profile/bilateral-product/wine/reporter/lbr")
st.write("[6] https://en.vogue.me/culture/saudi-arabia-serves-alcohol-sindalah-line-neom-beach-resort-wine-champagne-cocktails/")