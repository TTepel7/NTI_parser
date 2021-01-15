# подключение библиотеки vk_api для python
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import parse
import requests
import io


def keyboard_list(current_page=1):
    # создание клавиатуры
    keyboard = VkKeyboard(one_time=False, inline=False)
    keyboard.add_button(
        label="Справка",
        color=VkKeyboardColor.PRIMARY
    )
    keyboard.add_line()
    keyboard.add_button(
        label="Первая страница",
        color=VkKeyboardColor.SECONDARY,
        payload={"type": "first_page", "page": 1},
    )
    if current_page > 1:
        keyboard.add_button(
            label="Назад",
            color=VkKeyboardColor.NEGATIVE,
            payload={"type": "back_page", "page": current_page-1},
        )
    keyboard.add_button(
        label="Вперед",
        color=VkKeyboardColor.POSITIVE,
        payload={"type": "next_page", "page": current_page+1},
    )
    return keyboard


def announce_keyboard(url):
    # создание кнопок в сообщении
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button(
        label="Подробнее",
        color=VkKeyboardColor.SECONDARY,
        payload={"type": "announce_url", "url": url},
    )
    return keyboard

# Подключение к серверам
vk_session = vk_api.VkApi(
    token='', api_version='5.126')
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

START_TEXT = "Привет, для начала просмотра новостей с сайта НТИ (ф) УрФУ необходимо с помощью кнопок навигаций просматривать страницы новостей, если необходимо прочитать про новость подробнее необходимо нажать на кнопку рядом с ней."

# Загрузка изображенний
upload = vk_api.VkUpload(vk_session)

for event in longpoll.listen():
    # бексконечный цикл получения информации с серверов ВК
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        # событие получения нового сообщения
        if event.text == "Начать" or event.text == "начать" or event.text == "Справка":
            vk.messages.send(
                peer_id=event.peer_id,
                random_id=get_random_id(),
                keyboard=keyboard_list().get_keyboard(),
                message=START_TEXT
            )
        elif(hasattr(event, "payload")):
            # если в сообщении есть полезная нагрузка
            payload = json.loads(event.payload)
            if payload['type'] == "first_page" or payload['type'] == "next_page" or payload['type'] == "back_page":
                announces_list = parse.get_announces_list(payload['page'])
                for announce in announces_list:
                    # вывод всех новостей по очереди
                    vk.messages.send(
                        peer_id=event.peer_id,
                        random_id=get_random_id(),
                        keyboard=announce_keyboard(
                            announce['url']).get_keyboard(),
                        message=announce['name']
                    )
                vk.messages.send(
                    peer_id=event.peer_id,
                    random_id=get_random_id(),
                    keyboard=keyboard_list(payload['page']).get_keyboard(),
                    message="Страница №"+str(payload['page'])
                )
            elif payload['type'] == "announce_url":
                # нажата кнопка подробнее
                announce_full = parse.get_announce_content(payload['url'])
                message = announce_full['text']
                if len(announce_full['imgs']) > 0:
                    # новость содержит изображения
                    attachments = []
                    for img in announce_full['imgs']:
                        img_get = requests.get(img).content
                        f = io.BytesIO(img_get)
                        vk_img = upload.photo_messages(f, event.peer_id)
                        attachments.append("photo{}_{}".format(
                            vk_img[0]['owner_id'], vk_img[0]['id']))
                    vk.messages.send(
                        peer_id=event.peer_id,
                        random_id=get_random_id(),
                        message=message,
                        attachment=",".join(attachments)
                    )
                elif len(announce_full['videos']) > 0:
                    # новость содержит видео
                    message += " " + \
                        " ".join(announce_full['videos'])
                    vk.messages.send(
                        peer_id=event.peer_id,
                        random_id=get_random_id(),
                        message=message
                    )
                else:
                    vk.messages.send(
                        peer_id=event.peer_id,
                        random_id=get_random_id(),
                        message=message
                    )
