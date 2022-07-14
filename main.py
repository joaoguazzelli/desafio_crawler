# vamos caregar o modulo pandas
import pandas as pd
# importar biblioteca do pandas datareader
from pandas_datareader import data as pdr
# importar a bliblioteca Numpy
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader._utils import RemoteDataError

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os.path

from selenium.webdriver.common.by import By


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)


def get_cdi():
    driver.get(
        'https://www.google.com/search?q=CDI+hoje&oq=CDI+hoje&aqs=chrome.0.69i59l2.1941j0j1&sourceid=chrome&ie=UTF-8')
    div_data = driver.find_element(by=By.CLASS_NAME, value='hgKElc')
    div_data = div_data.text.split(' ')
    for i in div_data:
        if '%' in i:
            div_data = i
            break
    div_data = div_data.replace(",", ".").replace("%", "")
    # time.sleep(5)
    div_data = float(div_data)
    return div_data


def get_varejo():
    driver.get(
        "https://sistemaswebb3-listados.b3.com.br/listedCompaniesPage/search?language=pt-br&segment"
        "=VGVjaWRvcy4lMjBWZXN0dSVDMyVBMXJpbyUyMGUlMjBDYWwlQzMlQTdhZG9z")
    div_data = driver.find_elements(by=By.CLASS_NAME, value="card-title2")
    code_names = []
    for i in div_data:
        code_names.append(f'{i.accessible_name}3.SA')

    driver.get(
        "https://sistemaswebb3-listados.b3.com.br/listedCompaniesPage/search?language=pt-br&segment"
        "=UHJvZHV0b3MlMjBEaXZlcnNvcw%3D%3D")
    div_data = driver.find_elements(by=By.CLASS_NAME, value="card-title2")
    for i in div_data:
        code_names.append(f'{i.accessible_name}3.SA')

    driver.get(
        "https://sistemaswebb3-listados.b3.com.br/listedCompaniesPage/search?language=pt-br&segment"
        "=RWxldHJvZG9tJUMzJUE5c3RpY29z")
    div_data = driver.find_elements(by=By.CLASS_NAME, value="card-title2")
    for i in div_data:
        code_names.append(f'{i.accessible_name}3.SA')

    return code_names


def get_capm(code, cdi):

    carteira = [code, '^BVSP']

    mdata = pd.DataFrame()
    for t in carteira:
        mdata[t] = pdr.DataReader(t, data_source='yahoo')['Adj Close']

    # vamos criar um data frame novo com os dados de retorno em log... sabemos que em log é o melhor jeito se for
    # ativos individuais
    df_log = np.log(mdata / mdata.shift(1))
    # print(df_log.head())

    # vamos cria uma matriz de covariancai com o metodo (.cov)
    cov = df_log.cov() * 250

    # vamos obter a covariancia com o mercador, dando o numero floot
    cov_com_mercado = cov.iloc[0, 1]

    # vamos obter a variancia anualizado o nosso indice Ibov( Nossa carteria de Mercado)
    var_mercado = df_log['^BVSP'].var() * 250

    beta_acao = cov_com_mercado / var_mercado

    print(f'beta = {beta_acao}')

    alpha_jensen = cdi * (1 - beta_acao)
    print(f'alpha de jensen = {alpha_jensen}')

    retorno_esp_min = cdi + beta_acao * 0.08
    retorno_esp_min = str(round(retorno_esp_min, 5) * 100) + '%'
    dicionario = {"codigo": code, "beta": beta_acao, "alpha_de_jensen": alpha_jensen, "retorno_esp_min": retorno_esp_min}
    return dicionario


def analise(dicionario):
    alfas = []
    for k in dicionario:
        for n, j in k.items():
            if n == 'alpha_de_jensen':
                alfas.append(j)
    maior = max(alfas)
    print(maior)
    for k in dicionario:
        if k["alpha_de_jensen"] == maior:
            return k





cdi = get_cdi()
codes = get_varejo()
print(codes)
capm_values = []
for i in codes:
    try:
        x = get_capm(i, cdi)
        capm_values.append(x)
    except RemoteDataError:
        print(f"the following stock couldn't be fetched: {i}")

melhor_opcao = analise(capm_values)

print(melhor_opcao)