import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import os
import ru_local as ru


def get_search_url(search_text: str) -> str:
    """
    Generate search URL based on user input.

    Args:
        search_text (str): Text to search for products

    Returns:
        str: Complete search URL
    """
    return f'https://obuv-tut2000.ru/magazin/search?gr_smart_search=1&search_text={search_text}'


def parse_product_details(product_url: str) -> dict:
    """
    Parse detailed product information from product page.

    Args:
        product_url (str): URL of the product page

    Returns:
        dict: Dictionary containing product characteristics
    """
    product_response = requests.get(product_url)
    product_soup = BeautifulSoup(product_response.text, 'lxml')
    
    product_details = {
        'type_boots': ru.NOT_SPECIFIED,
        'article': ru.NOT_SPECIFIED,
        'color': ru.NOT_SPECIFIED,
        'country': ru.NOT_SPECIFIED,
        'season': ru.NOT_SPECIFIED,
        'material': ru.NOT_SPECIFIED,
        'size': ru.NOT_SPECIFIED
    }
    
    param_items = product_soup.find_all('div', class_='param-item')
    for param in param_items:
        title_elem = param.find('div', class_='param-title')
        if title_elem and ru.SHOE_TYPE_SEARCH in title_elem.get_text(strip=True).lower():
            body_elem = param.find('div', class_='param-body')
            if body_elem:
                product_details['type_boots'] = body_elem.get_text(strip=True)
            break


    article_elem = product_soup.find('div', class_='shop2-product-article')
    if article_elem:
        product_details['article'] = article_elem.get_text(' ', strip=True)
    

    color_elem = product_soup.find('div', class_='option-item cvet odd')
    if color_elem:
        product_details['color'] = color_elem.get_text(' ', strip=True)
    

    country_elem = product_soup.find('div', class_='gr-vendor-block')
    if country_elem:
        product_details['country'] = country_elem.get_text(' ', strip=True)
    

    season_elem = product_soup.find('div', class_='option-item sezon even')
    if season_elem:
        product_details['season'] = season_elem.get_text(' ', strip=True)
    

    material_elem = product_soup.find('div', class_='option-item material_verha_960 odd')
    if material_elem:
        product_details['material'] = material_elem.get_text(' ', strip=True)
    

    size_elem = product_soup.find('div', class_='option-item razmery_v_korobke even')
    if size_elem:
        product_details['size'] = size_elem.get_text(' ', strip=True)
    
    return product_details


def parse_main_page_data(product_element) -> tuple:
    """
    Extract basic product information from main page element.

    Args:
        product_element: BeautifulSoup element containing product data

    Returns:
        tuple: Name and price of the product
    """
    name_elem = product_element.find('div', class_='gr-product-name')
    name = name_elem.get_text(' ', strip=True) if name_elem else ru.NOT_SPECIFIED_NAME
    
    price_elem = product_element.find('div', class_='product-price')
    if price_elem:
        price = price_elem.get_text(' ', strip=True).replace('руб.', '')
    else:
        price = ru.NOT_SPECIFIED_PRICE
    
    return name, price


def create_dataframe(products_data: list) -> pd.DataFrame:
    """
    Create and sort DataFrame from products data.

    Args:
        products_data (list): List of dictionaries containing product information

    Returns:
        pd.DataFrame: Sorted DataFrame with product data
    """
    df = pd.DataFrame(products_data)
    

    df[ru.PRICE_NUM] = pd.to_numeric(
        df[ru.PRICE].str.replace(' ', '').replace('', '0'), 
        errors='coerce'
    )
    
    df = df.sort_values(ru.PRICE_NUM)
    
    df = df.drop(ru.PRICE_NUM, axis=1)
    
    return df


def save_to_excel(dataframe: pd.DataFrame, filename: str) -> str:
    """
    Save DataFrame to Excel file in Downloads folder.

    Args:
        dataframe (pd.DataFrame): DataFrame to save
        filename (str): Name of the output file

    Returns:
        str: Full path to the saved file
    """
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    file_path = os.path.join(downloads_path, filename)
    dataframe.to_excel(file_path, index=False)
    
    return file_path


def main():
    """
    Main function to orchestrate the web scraping process.
    
    Steps:
    1. Get search query from user
    2. Fetch and parse search results
    3. Extract product details from individual pages
    4. Compile data and save to Excel file
    """
    all_products = []

    search_text = input(ru.SEARCH_PROMPT)
    url = get_search_url(search_text)
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    product_elements = soup.find_all('form', class_='shop2-product-item product-item')


    for product_element in product_elements:
        # Get product page URL
        product_link_elem = product_element.find('a', href=True)
        
        if product_link_elem:
            product_url = urljoin('https://obuv-tut2000.ru', product_link_elem['href'])
            product_details = parse_product_details(product_url)
        else:
            product_details = {
                'type_boots': ru.NOT_SPECIFIED,
                'article': ru.NOT_SPECIFIED,
                'color': ru.NOT_SPECIFIED,
                'country': ru.NOT_SPECIFIED,
                'season': ru.NOT_SPECIFIED,
                'material': ru.NOT_SPECIFIED,
                'size': ru.NOT_SPECIFIED
            }


        name, price = parse_main_page_data(product_element)
        

        all_products.append({
            ru.NAME: name,
            ru.PRICE: price,
            ru.SIZES: product_details['size'],
            ru.UPPER_MATERIAL: product_details['material'],
            ru.ARTICLE: product_details['article'],
            ru.SHOE_TYPE: product_details['type_boots'],
            ru.SEASON: product_details['season'],
            ru.COLOR: product_details['color'],
            ru.COUNTRY: product_details['country']
        })
        
        print(f"{ru.PROCESSED_PRODUCT}: {name}")

    
    if all_products:
        df = create_dataframe(all_products)
        file_path = save_to_excel(df, ru.FILE_NAME)
        
        print(f"\n{ru.FILE_SAVED}: {file_path}")
        print(f"{ru.TOTAL_PROCESSED}: {len(all_products)}")
    else:
        print(ru.NO_PRODUCTS_FOUND)


if __name__ == "__main__":
    main()
