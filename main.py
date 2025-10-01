#DEVELOPERS: Ponasenko E., Loseva E., Limanova E.

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import pandas as pd
import os
import time
import ru_local as ru


all_products = []


def get_search_query() -> str:
    """
    Get search query from user input.
    
    Returns:
        str: User-entered search query
    """
    search_text = input(ru.SEARCH_PROMPT).strip()
    return search_text


def extract_product_details(product_url: str) -> dict:
    """
    Extract detailed product information from product page.
    
    Args:
        product_url (str): URL of product page
        
    Returns:
        dict: Dictionary with detailed product information
    """
    product_response = requests.get(product_url)
    product_soup = BeautifulSoup(product_response.text, 'lxml')


    type_boots = ru.NOT_SPECIFIED
    param_items = product_soup.find_all('div', class_='param-item')
    for param in param_items:
        title_elem = param.find('div', class_='param-title')
        if title_elem and 'вид обуви' in title_elem.get_text(strip=True).lower():
            body_elem = param.find('div', class_='param-body')
            if body_elem:
                type_boots = body_elem.get_text(strip=True)
            break


    article_elem = product_soup.find('div', class_='shop2-product-article')
    article = article_elem.get_text(' ', strip=True) if article_elem else ru.NOT_SPECIFIED


    color_elem = product_soup.find('div', class_='option-item cvet odd')
    color = color_elem.get_text(' ', strip=True) if color_elem else ru.NOT_SPECIFIED


    country_elem = product_soup.find('div', class_='gr-vendor-block')
    country = country_elem.get_text(' ', strip=True) if country_elem else ru.NOT_SPECIFIED


    season_elem = product_soup.find('div', class_='option-item sezon even')
    season = season_elem.get_text(' ', strip=True) if season_elem else ru.NOT_SPECIFIED

  
    material_elem = product_soup.find('div', class_='option-item material_verha_960 odd')
    material = material_elem.get_text(' ', strip=True) if material_elem else ru.NOT_SPECIFIED


    size_elem = product_soup.find('div', class_='option-item razmery_v_korobke even')
    size = size_elem.get_text(' ', strip=True) if size_elem else ru.NOT_SPECIFIED
    
    return {
        'type_boots': type_boots,
        'article': article,
        'color': color,
        'country': country,
        'season': season,
        'material': material,
        'size': size
    }


def extract_basic_product_info(product_element) -> dict:
    """
    Extract basic product information from product card.
    
    Args:
        product_element: BeautifulSoup product element
        
    Returns:
        dict: Dictionary with basic product information
    """
    name_elem = product_element.find('div', class_='gr-product-name')
    name = name_elem.get_text(' ', strip=True) if name_elem else ru.NOT_SPECIFIED

    price_elem = product_element.find('div', class_='product-price')
    price = price_elem.get_text(' ', strip=True).replace('руб.', '') if price_elem else ru.NOT_SPECIFIED_FEMININE
    
    return {
        'name': name,
        'price': price
    }


def get_product_url(product_element) -> str:
    """
    Extract product page URL from product element.
    
    Args:
        product_element: BeautifulSoup product element
        
    Returns:
        str: Product page URL or None if not found
    """
    product_link_elem = product_element.find('a', href=True)
    if product_link_elem:
        return urljoin('https://obuv-tut2000.ru', product_link_elem['href'])
    return None


def save_to_excel(products: list, filename: str = 'обувь_товары.xlsx') -> str:
    """
    Save products list to Excel file in Downloads folder.
    
    Args:
        products (list): List of dictionaries with product information
        filename (str): Filename for saving
        
    Returns:
        str: Full path to saved file
    """
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    df = pd.DataFrame(products)

    df['Цена_число'] = pd.to_numeric(df[ru.PRICE].str.replace(' ', '').replace('', '0'), errors='coerce')
    df = df.sort_values('Цена_число')
    df = df.drop('Цена_число', axis=1)

    file_path = os.path.join(downloads_path, filename)
    df.to_excel(file_path, index=False)
    
    return file_path


def main():
    """
    Main function of shoe products parser.
    Performs search, data collection and saving to Excel file.
    """
    search_text = get_search_query()
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

        print(ru.PAGE_INFO.format(page, len(data)))

        for product_element in data:
            product_url = get_product_url(product_element)
            
            if product_url:
                product_details = extract_product_details(product_url)
                
                basic_info = extract_basic_product_info(product_element)
                
                all_products.append({
                    ru.NAME: basic_info['name'],
                    ru.PRICE: basic_info['price'],
                    ru.SIZES: product_details['size'],
                    ru.MATERIAL: product_details['material'],
                    ru.ARTICLE: product_details['article'],
                    ru.TYPE: product_details['type_boots'],
                    ru.SEASON: product_details['season'],
                    ru.COLOR: product_details['color'],
                    ru.COUNTRY: product_details['country']
                })

                print(ru.PROCESSED_PRODUCT.format(basic_info['name']))
            else:

                basic_info = extract_basic_product_info(product_element)
                all_products.append({
                    ru.NAME: basic_info['name'],
                    ru.PRICE: basic_info['price'],
                    ru.SIZES: ru.NOT_SPECIFIED,
                    ru.MATERIAL: ru.NOT_SPECIFIED,
                    ru.ARTICLE: ru.NOT_SPECIFIED,
                    ru.TYPE: ru.NOT_SPECIFIED,
                    ru.SEASON: ru.NOT_SPECIFIED,
                    ru.COLOR: ru.NOT_SPECIFIED,
                    ru.COUNTRY: ru.NOT_SPECIFIED
                })

        page += 1
        time.sleep(1)  # пауза, чтобы не нагружать сайт

    if all_products:
        file_path = save_to_excel(all_products)
        
        print(ru.FILE_SAVED.format(file_path))
        print(ru.TOTAL_PRODUCTS.format(len(all_products)))
    else:
        print(ru.NO_PRODUCTS)


if __name__ == "__main__":
    main()
