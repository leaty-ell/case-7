import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import pandas as pd
import os
import time

import ru_local as ru

# Создаем список для хранения всех товаров
all_products = []

# Получаем поисковый запрос от пользователя
search_text = input(ru.SEARCH_PROMPT).strip()
encoded_text = quote(search_text)

page = 1
while True:
    url = f'https://obuv-tut2000.ru/magazin/search?p={page}&gr_smart_search=1&search_text={encoded_text}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    # Находим товары на текущей странице
    data = soup.find_all('form', class_='shop2-product-item product-item')
    if not data:  # если товаров больше нет → выходим
        break

    print(f"\n{ru.PAGE_INFO.format(page=page, count=len(data))}")

    for i in data:
        # Получаем ссылку на страницу товара
        product_link_elem = i.find('a', href=True)
        if product_link_elem:
            product_url = urljoin('https://obuv-tut2000.ru', product_link_elem['href'])

            # Переходим на страницу товара
            product_response = requests.get(product_url)
            product_soup = BeautifulSoup(product_response.text, 'lxml')

            # Вид обуви
            type_boots = ru.NOT_SPECIFIED
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
            article = article_elem.get_text(' ', strip=True) if article_elem else ru.NOT_SPECIFIED

            # Цвет
            color_elem = product_soup.find('div', class_='option-item cvet odd')
            color = color_elem.get_text(' ', strip=True) if color_elem else ru.NOT_SPECIFIED

            # Страна
            country_elem = product_soup.find('div', class_='gr-vendor-block')
            country = country_elem.get_text(' ', strip=True) if country_elem else ru.NOT_SPECIFIED

            # Сезон
            season_elem = product_soup.find('div', class_='option-item sezon even')
            season = season_elem.get_text(' ', strip=True) if season_elem else ru.NOT_SPECIFIED

            # Материал верха
            material_elem = product_soup.find('div', class_='option-item material_verha_960 odd')
            material = material_elem.get_text(' ', strip=True) if material_elem else ru.NOT_SPECIFIED

            # Размеры
            size_elem = product_soup.find('div', class_='option-item razmery_v_korobke even')
            size = size_elem.get_text(' ', strip=True) if size_elem else ru.NOT_SPECIFIED
        else:
            # Значения по умолчанию если нет ссылки на товар
            article = ru.NOT_SPECIFIED
            color = ru.NOT_SPECIFIED
            country = ru.NOT_SPECIFIED
            season = ru.NOT_SPECIFIED
            type_boots = ru.NOT_SPECIFIED
            material = ru.NOT_SPECIFIED
            size = ru.NOT_SPECIFIED

        # Данные с основной страницы
        name_elem = i.find('div', class_='gr-product-name')
        name = name_elem.get_text(' ', strip=True) if name_elem else ru.NOT_SPECIFIED

        price_elem = i.find('div', class_='product-price')
        price = price_elem.get_text(' ', strip=True).replace('руб.', '') if price_elem else ru.NOT_SPECIFIED

        # Добавляем товар в список
        all_products.append({
            ru.NAME: name,
            ru.PRICE: price,
            ru.SIZES: size,
            ru.MATERIAL: material,
            ru.ARTICLE: article,
            ru.BOOT_TYPE: type_boots,
            ru.SEASON: season,
            ru.COLOR: color,
            ru.COUNTRY: country
        })

        print(f"{ru.PROCESSED_PRODUCT}: {name}")

    page += 1
    time.sleep(1)  # пауза, чтобы не нагружать сайт

# Сохраняем в Excel файл в папку Загрузки
if all_products:
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    df = pd.DataFrame(all_products)

    # сортировка по цене
    df[ru.PRICE_NUM] = pd.to_numeric(df[ru.PRICE].str.replace(' ', '').replace('', '0'), errors='coerce')
    df = df.sort_values(ru.PRICE_NUM)
    df = df.drop(ru.PRICE_NUM, axis=1)

    file_path = os.path.join(downloads_path, ru.FILE_NAME)
    df.to_excel(file_path, index=False)

    print(f"\n{ru.SUCCESS_SAVE.format(path=file_path)}")
    print(f"{ru.TOTAL_PRODUCTS.format(count=len(all_products))}")
else:
    print(ru.NO_PRODUCTS_FOUND)


if __name__ == "__main__":
    main()
