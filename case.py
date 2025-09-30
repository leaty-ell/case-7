import requests
from bs4 import BeautifulSoup

search_text = input("Введите поисковый запрос: ")
url = f'https://obuv-tut2000.ru/magazin/search?gr_smart_search=1&search_text={search_text}'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
data = soup.find_all('form', class_='shop2-product-item product-item')
for i in data:
    name = i.find('div', class_='gr-product-name').get_text(' ', strip=True)
    price = i.find('div', class_='product-price').get_text(' ', strip=True).replace('руб.', '')
    size_block = i.find('div', class_='option-item razmery_v_korobke even')
    if size_block:
        size = size_block.find('div', class_='option-body').get_text(strip=True)
    else:
        size = "Не указан"
    material_block = i.find('div', class_='option-item material_verha_960 odd')
    if material_block:
        material = material_block.find('div', class_='option-body').get_text(strip=True)
    else:
        material = "Не указан"
    print(name + '\n' + price + '\n' + size + '\n' + material + '\n\n')
