import requests
from bs4 import BeautifulSoup

# Ссылка на католог новостей НТИ, в конце адресса можно добавить номер страницы
NTI_ANNOUNCE_URL="http://nti.urfu.ru/page/Index/ru/announces/"
NTI_BASE_URL="http://nti.urfu.ru"

def get_announces_list(page=1):
    response=requests.get(NTI_ANNOUNCE_URL+str(page))
    soup=BeautifulSoup(response.text,'html.parser')
    # получение списка объявлений
    announces=soup.find_all('div',class_="announce")
    # создание массива для хранения короткой информации о новостях
    announces_list=[]
    for announce in announces:
        # заполнение словаря
        info=dict()
        info["name"]=announce.find("span").text
        info["url"]=announce.find("a").get('href')
        announces_list.append(info)
    
    return announces_list

