import requests
from bs4 import BeautifulSoup

# Ссылка на католог новостей НТИ, в конце адресса можно добавить номер страницы
NTI_ANNOUNCE_URL = "http://nti.urfu.ru/page/Index/ru/announces/"
NTI_BASE_URL = "http://nti.urfu.ru"


def get_announces_list(page=1):
    # получение и преобразование HTML кода
    response = requests.get(NTI_ANNOUNCE_URL+str(page))
    soup = BeautifulSoup(response.text, 'html.parser')
    # получение списка объявлений
    announces = soup.find_all('div', class_="announce")
    # создание массива для хранения короткой информации о новостях
    announces_list = []
    for announce in announces:
        # заполнение словаря
        info = dict()
        info["name"] = announce.find("span").text
        info["url"] = NTI_BASE_URL + announce.find("a").get('href')
        announces_list.append(info)
    # возвращаем массив словарей
    return announces_list


def get_announce_content(url):
    # получение и преобразование HTML кода
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    anonce_content = soup.find('div', class_="content")
    # создание словаря для хранения информации
    content = dict()
    # сохранение заголовка новости
    anonce_header = anonce_content.find('div', class_="content-header")
    content["title"] = anonce_header.find("h1").text
    # сохранение даты и автора новости
    content["date_author"] = anonce_header.find("div").text
    # сохранение основного блока информации
    content["text"] = anonce_content.find('div', class_="content-body").text

    # блок хранение картинок
    anonce_img = anonce_content.find_all('img')
    imgs = []
    for img in anonce_img:
        imgs.append(NTI_BASE_URL + img.get('src'))
    content["imgs"] = imgs
    
    # блок хранения видео
    anonce_video = anonce_content.find_all('iframe')
    videos=[]
    for video in anonce_video:
        videos.append(video.get('src'))
    content["videos"]=videos

    return content

