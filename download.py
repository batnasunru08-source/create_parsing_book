import requests
from lxml import html
import time
from urllib.parse import urljoin

# Настройки
START_URL = 'https://wuxiaworld.ru/apokalipsis-sistema-sinteza-zombi/glava-887-zamuzhem-za-chung-lingom/'
OUTPUT_FILE = 'Апокалипсис Система Синтеза Зомби 887.txt'
DELAY_SECONDS = 1.5
XPATH_NEXT_PAGE = '/html/body/main/div[2]/div/div[1]/a[2]'
XPATH_HEADER = '/html/body/div/div/nav/h1'

# Сюда впишешь фразы рекламы для удаления, например:
# "Читать новеллу", "Подписывайтесь", "Наш телеграм"
AD_KEYWORDS = [
    
    "Редактируется Читателями!",
    "Нет главы и т.п. - пиши в Комменты. Читать без рекламы бесплатно?!",
    "наш телеграм",
    "Апокалипсис: Система Синтеза Зомби",
    "Ранобэ Новелла"
    
]

def remove_ads_from_text(text):
    """Удаляет строки, содержащие рекламные ключевые слова."""
    clean_lines = []
    for line in text.split("\n"):
        if not any(key.lower() in line.lower() for key in AD_KEYWORDS):
            clean_lines.append(line)
    return "\n".join(clean_lines)

def get_page_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    print(f"Загружаем: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при загрузке страницы: {url}")
        return None, None, None

    tree = html.fromstring(response.content)

    # Получаем заголовок <h1>
    header_elements = tree.xpath(XPATH_HEADER)
    header_text = header_elements[0].text_content().strip() if header_elements else 'Без заголовка'
    print(f"▶ Заголовок: {header_text}")

    # Получаем основной текст главы
    content_div = tree.xpath('//*[@id="js-full-content"]//p')
    content_text = '\n'.join([p.text_content().strip() for p in content_div if p.text_content().strip()])

    # Убираем строки рекламы
    content_text = remove_ads_from_text(content_text)

    full_text = f"{header_text}\n\n{content_text}"

    # Ссылка на следующую страницу
    next_link = tree.xpath(XPATH_NEXT_PAGE)
    next_url = None
    if next_link:
        next_url = next_link[0].get('href')
        if next_url and not next_url.startswith('http'):
            next_url = urljoin(url, next_url)

    return full_text, next_url, header_text

def get_h1_from_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        tree = html.fromstring(response.content)
        header_elements = tree.xpath(XPATH_HEADER)
        return header_elements[0].text_content().strip() if header_elements else None
    except:
        return None

def crawl_all(start_url, output_file):
    current_url = start_url
    with open(output_file, 'w', encoding='utf-8') as f:
        while current_url:
            text, next_url, current_h1 = get_page_data(current_url)

            if not text:
                print("Не удалось получить текст со страницы.")
                break

            # Сохраняем текст главы
            f.write(text + "\n\n--- NEXT PAGE ---\n\n")

            # Проверяем заголовок следующей страницы после сохранения текущей
            if next_url:
                next_h1 = get_h1_from_url(next_url)
                if next_h1 == current_h1:
                    print(f"🛑 Заголовок следующей страницы совпадает с текущим: '{current_h1}'")
                    print("Парсинг завершён.")
                    break

            current_url = next_url
            time.sleep(DELAY_SECONDS)

    print(f"\n✅ Сохранено в файл: {output_file}")

if __name__ == '__main__':
    crawl_all(START_URL, OUTPUT_FILE)
