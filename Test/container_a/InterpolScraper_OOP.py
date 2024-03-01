from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import schedule
import time
from pika import BlockingConnection, ConnectionParameters

'''
Bu kod selenium kullanılarak interpol kırımızı listesindeki arananların verilerinin çekilmesini sağlar.Kod yazarken normal şekilde veriyi
alamadığım için başka bir alternetif buldum o da ilk sayfadaki bütün arananların sayfasına gidicek olan linkler alınır ondan sonra o linkler yeni
sekmede açılır ve o sekmeden aranan şahısın verileri alındıktan sonra sekme kapanır ve bu işlem her aranan için yapılır.Toplam veri alma işlemi güncel olarak
20-22 dk sürmektedir.Veriler alındıktan sonra .json dosyasına çevrilir ordan rabbitmq kullanılarak consumera veri aktarılır. Bu kod saat başı tekrar başlancak
şekilde ayarlanmıştır.

'''


class InterpolScraper:
    def __init__(self, url, output_file, queue_host, queue_name):
        self.url = url
        self.output_file = output_file
        self.queue_host = queue_host
        self.queue_name = queue_name
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        self.options.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.data = []

    def scrape_data(self):
        try:
            self.driver.get(self.url)
            self.driver.implicitly_wait(10)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="paginationPanel"]')))
            pagination = self.driver.find_element(By.XPATH, '//*[@id="paginationPanel"]')
            pages = pagination.find_elements(By.TAG_NAME, 'li')
            last_page = int(pages[-2].text)

            current_page = 1
            while current_page <= 2:
                print(f"Processing page {current_page}")
                self.process_page()
                print(f"Page {current_page} finished.")
                current_page += 1

                next_page = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'nextIndex')]")))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
                next_page.click()
                time.sleep(5.2)

        except TimeoutException as e:
            print("TimeoutException: ", e)

        finally:
            self.driver.quit()
            self.save_to_json()
            self.send_to_queue()

    def process_page(self):
        the_urls = self.driver.find_elements(By.XPATH, "//div[@class='redNoticesList__listWrapper']//a")
        links = [url.get_attribute('href') for url in the_urls]

        for link in links:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(link)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="singlePanel"]/div[2]/div/div[2]/div[1]/table/tbody/tr')))

            self.extract_data_from_table()

            time.sleep(5.2)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def extract_data_from_table(self):
        data_dict = {}
        table_rows = self.driver.find_elements(By.XPATH, '//*[@id="singlePanel"]/div[2]/div/div[2]/div[1]/table/tbody/tr')
        for row in table_rows:
            column_name = row.find_element(By.XPATH, './td[1]').text
            column_value = row.find_element(By.XPATH, './td[2]').text

            if column_name and column_value:
                data_dict[column_name] = column_value

        charge_element = self.driver.find_element(By.XPATH, '//*[@id="charge"]')
        charge_info = charge_element.text
        data_dict['Charge'] = charge_info if charge_info else 'N/A'

        self.data.append(data_dict)

    def save_to_json(self):
        with open(self.output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.data, jsonfile, ensure_ascii=False, indent=4)

    def send_to_queue(self):
        connection_params = ConnectionParameters(host=self.queue_host)
        with BlockingConnection(connection_params) as connection:
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name)
            for item in self.data:
                channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(item))

if __name__ == "__main__":
    def run_interpol_scraper():
        interpol_scraper = InterpolScraper("https://www.interpol.int/How-we-work/Notices/Red-Notices/View-Red-Notices", "interpol_data.json", "rabbitmq", "interpol_queue")
        interpol_scraper.scrape_data()

    run_interpol_scraper()

    schedule.every(1).hours.do(run_interpol_scraper)

    while True:
        schedule.run_pending()
        time.sleep(1)
