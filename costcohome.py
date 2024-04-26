#import undetected_chromedriver as uc
from selenium import webdriver
from a_pandas_ex_css_selector_from_html import pd_add_css_selector_from_html
import re
from PrettyColorPrinter import add_printer
from selenium.webdriver.common.by import By
import pandas as pd
import warnings
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
warnings.filterwarnings("ignore", message="This pattern is interpreted as a regular expression.*")
add_printer(1)
pd_add_css_selector_from_html() 

if __name__ == "__main__":
    url_main = 'https://www.costco.ca'
    url = 'https://www.costco.ca/appliances.html'
    #driver = uc.Chrome(
    #)
    driver = webdriver.Chrome()
    driver.get(url)
    
    #pagination_re = 'nav[aria-label="pagination"]'
    URL_RE = r'<a\s+href="([^"]*)"'
    ID_PATTERN = r'div\[itemid="(\d+)"\](?![^\]]*\])'
    HREF_ID = r'href="([^"]*)"'
    PRODUCT_ID_RE = r'itemid="(\d+)"'
    BUTTON_RE = 'li[class="forward"]'

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.Q_selector_from_html(driver.page_source, parser="html.parser", ignore_tags=("html", "body"))
    df_output = pd.DataFrame(columns=['Date Scrape', 'Category', 'SKU', 'Costco Id', 'Product Id', 'Name', 'Price', 'Description', 'Url Scraped'])#,'Images Urls']) 
    find = r'div[class="col-xs-12 col-lg-6 col-xl-2"]'
    finder = df[df['selector']==find].drop(columns=['group_html','group_selector'])
    category_urls = finder['html'].str.extract(URL_RE, expand=False)


    for href_category in category_urls:
        driver.get(url_main+href_category)
        category = driver.find_element(By.CLASS_NAME, 't1-style').text\
                
        count_page = 0
        while True:
            df = pd.Q_selector_from_html(driver.page_source, parser="html.parser", ignore_tags=("html", "body"))
            links_selecionados = df[df['selector'].str.contains(ID_PATTERN, regex=True)]
            product_url = links_selecionados['html'].str.extract(HREF_ID, expand=False)
            costco_id = links_selecionados['selector'].str.extract(PRODUCT_ID_RE, expand=False)
            btn = df[df['selector'] == BUTTON_RE]
            next_btn = btn['html'].str.extract(HREF_ID, expand=False)
            
            data_to_append = [] 
            for href_value, costco_id in zip(product_url, costco_id) :
                driver.get(href_value)
                price_element = driver.find_element(By.ID, 'pull-right-price')
                if price_element.text.strip() == '':
                    price = 'Sign In to See Price'
                else:
                    price = price_element.text

                try:
                    sku_text = driver.find_element(By.ID, 'product-body-model-number').text
                    sku = re.sub(r'^Model\s+', '', sku_text)
                except NoSuchElementException:
                    sku = 'There is no SKU number'

                title = driver.find_element(By.CSS_SELECTOR, '.product-h1-container-v2').text
                desc = driver.find_element(By.ID, 'productDescriptions1').text
                product_id_text = driver.find_element(By.ID, 'product-body-item-number').text
                product_id = re.findall(r'\d+', product_id_text)  # Extrai apenas os números
                product_id = ''.join(product_id) if product_id else None
                print(f'Preço: {price}, Category: {category},SKU: {sku}, Costco Id: {costco_id}, Product Id: {product_id}  Name: {title}, Price: {price}  Description: {desc}, Url Scraped: {href_value}')
                data_to_append.append({'Date Scrape': current_date, 'Category': category,'SKU': sku, 'Costco Id': costco_id, 'Product Id': product_id,  'Name': title, 'Price': price,  'Description': desc, 'Url Scraped': href_value})#,'Images Urls': img_sources})

                
            if data_to_append:
                df_temp = pd.DataFrame(data_to_append)
                df_output = pd.concat([df_output, df_temp], ignore_index=True)
                
            if next_btn.empty:
                print("Moving to the next category...")
                break    
            # Navega para a próxima página se houver
            if next_btn.iloc[0]:
                driver.get(next_btn.iloc[0])
                count_page += 1
                print(f'Page {count_page} loaded')

for column in df_output.columns:
        if column in df_output.columns and df_output[column].dtype == 'object':
            df_output[column] = df_output[column].str.replace('\n', '')
df_output.to_csv('example.csv', index=False)
driver.quit()