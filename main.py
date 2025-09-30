import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import os

# Создаем список для хранения всех товаров
all_products = []

for pages in range(1, 10):
    url = f'https://obuv-tut2000.ru/magazin/folder/zhenskaya-obuv-optom-{pages}'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    data = soup.find_all('form', class_='shop2-product-item product-item')

    for i in data:
        # Получаем ссылку на страницу товара
        product_link_elem = i.find('a', href=True)
        if product_link_elem:
            product_url = urljoin('https://obuv-tut2000.ru', product_link_elem['href'])
            
            # Переходим на страницу товара
            product_response = requests.get(product_url)
            product_soup = BeautifulSoup(product_response.text, 'lxml')
            
            # УНИФИЦИРОВАННЫЙ ПОИСК ВСЕХ ХАРАКТЕРИСТИК
            # Ищем вид обуви в блоках param-item
            type_boots = "Не указан"
            param_items = product_soup.find_all('div', class_='param-item')
            for param in param_items:
                title_elem = param.find('div', class_='param-title')
                if title_elem and 'вид обуви' in title_elem.get_text(strip=True).lower():
                    body_elem = param.find('div', class_='param-body')
                    if body_elem:
                        type_boots = body_elem.get_text(strip=True)
                    break

            # Артикул
            article_elem = product_soup.find('div', class_='shop2-product-article')
            article = article_elem.get_text(' ', strip=True) if article_elem else "Не указан"
            
            # Цвет
            color_elem = product_soup.find('div', class_='option-item cvet odd')
            color = color_elem.get_text(' ', strip=True) if color_elem else "Не указан"
            
            # Страна
            country_elem = product_soup.find('div', class_='gr-vendor-block')
            country = country_elem.get_text(' ', strip=True) if country_elem else "Не указан"
            
            # Сезон
            season_elem = product_soup.find('div', class_='option-item sezon even')
            season = season_elem.get_text(' ', strip=True) if season_elem else "Не указан"
            
            # Материал верха
            material_elem = product_soup.find('div', class_='option-item material_verha_960 odd')
            material = material_elem.get_text(' ', strip=True) if material_elem else "Не указан"
            
            # Размеры
            size_elem = product_soup.find('div', class_='option-item razmery_v_korobke even')
            size = size_elem.get_text(' ', strip=True) if size_elem else "Не указан"
        else:
            # Значения по умолчанию если нет ссылки на товар
            article = "Не указан"
            color = "Не указан"
            country = "Не указан"
            season = "Не указан"
            type_boots = "Не указан"
            material = "Не указан"
            size = "Не указан"

        # Данные с основной страницы
        name_elem = i.find('div', class_='gr-product-name')
        name = name_elem.get_text(' ', strip=True) if name_elem else "Не указано"
        
        price_elem = i.find('div', class_='product-price')
        price = price_elem.get_text(' ', strip=True).replace('руб.', '') if price_elem else "Не указана"
        
        # Добавляем товар в список
        all_products.append({
            'Наименование': name,
            'Цена': price,
            'Размеры': size,
            'Материал верха': material,
            'Артикул': article,
            'Вид обуви': type_boots,
            'Сезон': season,
            'Цвет': color,
            'Страна': country
        })
        
        print(f"Обработан товар: {name}")
# Сохраняем в Excel файл в папку Загрузки
if all_products:
    # Получаем путь к папке Загрузки
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    # Создаем DataFrame
    df = pd.DataFrame(all_products)
    
    # Сохраняем в Excel
    file_path = os.path.join(downloads_path, 'обувь_товары.xlsx')
    df.to_excel(file_path, index=False)
    
    print(f"\n Файл успешно сохранен: {file_path}")
    print(f" Всего обработано товаров: {len(all_products)}")
else:
    print(" Товары не найдены")
