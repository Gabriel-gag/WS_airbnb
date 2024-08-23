from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import pandas as pd

# Configuração do WebDriver
options = Options()
options.add_argument('window-size=600,1000')

navegador = webdriver.Chrome(options=options)

navegador.get('https://www.airbnb.com.br')

# Aguarda 2 segundos para a página carregar
sleep(2)

# Aguarda até que o botão "Qualquer lugar" esteja clicável
wait = WebDriverWait(navegador, 10)
elemento = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Qualquer lugar')]")))
elemento.click()

sleep(0.2)
elemento = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Buscar destinos')]")))
elemento.click()

sleep(0.2)
elemento = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Buscar destinos']")))
elemento.click()

try:
    input_element = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='/homes-where-input']")))
    input_element.send_keys('São Paulo')
    input_element.send_keys(Keys.ENTER)

    sleep(0.2)
    next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='dates-footer-primary-btn']")))
    next_button.click()    
    buttons = navegador.find_elements(By.TAG_NAME, 'button')

    # Seleciona o último botão da lista
    if buttons:
        next_button = buttons[-1]
        next_button.click()
    else:
        print("Nenhum botão encontrado na página.")

    sleep(4)
    page_content = navegador.page_source

    site = BeautifulSoup(page_content, 'html.parser')

    dados_hospedagens = []

    hospedagens = site.findAll('div', attrs={'itemprop': 'itemListElement'})

    for hospedagem in hospedagens:
        # Descrição e URL
        hospedagem_descricao = hospedagem.find('meta', attrs={'itemprop': 'name'})
        hospedagem_url = hospedagem.find('meta', attrs={'itemprop': 'url'})

        hospedagem_descricao = hospedagem_descricao['content']
        hospedagem_url = hospedagem_url['content']


        print('Descrição: ', hospedagem_descricao)
        print('URL: ', hospedagem_url)

        # Detalhes e data
        try:
            elementos_informacoes = hospedagem.select("div[data-testid='listing-card-subtitle'] span.a8jt5op")
            if len(elementos_informacoes) >= 2:
                hospedagem_detalhes = elementos_informacoes[0].text
                hospedagem_data = elementos_informacoes[1].text
                detalhes = f"{hospedagem_detalhes}, {hospedagem_data}"
                print('Detalhes: ', detalhes)
            else:
                print('Detalhes não encontrados.')

        except Exception as e:
            print('Erro ao obter detalhes:', e)

        # Avaliação
        try:
            hospedagem_avaliacao = hospedagem.find_all('span')[-1].text
            print('Avaliação: ', hospedagem_avaliacao)
        except:
            print('Avaliação não encontrada.')

        # Preço original e com desconto
        preco_original = "Não disponível"
        preco_desconto = "Não disponível"

        try:
            elemento_preco_original = hospedagem.select_one("span._1aejdbt")
            if elemento_preco_original:
                preco_original = elemento_preco_original.text
        except:
            pass  # Não faz nada se não encontrar o elemento

        try:
            elemento_preco_desconto = hospedagem.select_one("span._11jcbg2")
            if elemento_preco_desconto:
                preco_desconto = elemento_preco_desconto.text
                # Substitui o preço original pelo preço com desconto se o desconto estiver disponível
                preco_original = preco_desconto
        except:
            pass  # Não faz nada se não encontrar o elemento

        print(f"Preço: {preco_original}")
        print()
        dados_hospedagens.append([hospedagem_descricao, hospedagem_url, hospedagem_detalhes,hospedagem_data, hospedagem_avaliacao,preco_original])
    dados=(pd.DataFrame(dados_hospedagens,columns=['Descrição','URL','Detalhes','Data','Avaliação','Preço']))
    dados.to_csv('hospedagens.csv', index=False)
except TimeoutException:
    print("Elemento de entrada não encontrado no tempo especificado.")

finally:
    input("Pressione Enter para sair")
    navegador.quit()
