from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
import json
btn = types.KeyboardButton
inBtn = types.InlineKeyboardButton
#------ Main -------#
def mainBtn():
    buttons = [
            [
            btn(text = "⭐️Все Скрипты⭐️"),
            btn(text = "👊 Профиль")
            ],
            [btn(text = "🔥 Элементы для креосов 🔥") ],
            [
            btn(text="О Сервисе ❤️")
            ]
            ]
        
    main_mark = types.ReplyKeyboardMarkup(keyboard=buttons)
    return main_mark

def Profile():
    buttons = [
        # [btn(text = "😎Купленное😎"),btn(text = "🤝Пополнить счет")],
        [btn(text = "На главную братишка")]
    ]
    main_mark = types.ReplyKeyboardMarkup(keyboard=buttons)
    return main_mark

def Rules():
    buttons = [
        [inBtn(text = "🎇 Я красава и я все прочитал, давайте работать 🎇", callback_data="Rule")]
    ]
    rulesMark = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return rulesMark

def About():
    buttons = [
        [inBtn(text = "Информация о создателе", callback_data="About_Me")],
        [inBtn(text = "Что такое iCreo Health?", callback_data="About_Ecosystem")]
    ]
    rulesMark = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return rulesMark

def Scripts():
    buttons = [
        [inBtn(text = "Разрезка изображения", callback_data="ImageDivider")]
    ]
    rulesMark = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return rulesMark

def ExitFromImageMatrix():
    buttons = [
        [inBtn(text = "Выйти из работы скрипта", callback_data="AgreeWindow_Exit")]
    ]
    rulesMark = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return rulesMark

def Accept():
    buttons = [
        [inBtn(text = "Подтверждаю", callback_data="AgreeWindow_Yes")],
        [inBtn(text = "Отправить другое изображение", callback_data="AgreeWindow_No")],
        [inBtn(text = "Выйти из работы скрипта", callback_data="AgreeWindow_Exit")],
        [inBtn(text = "Перезапуск с заводскими параметрами", callback_data="AgreeWindow_Rejoin")]
    ]
    rulesMark = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return rulesMark
def Accept2():
    buttons = [
        [inBtn(text = "Запуск с заводскими параметрами", callback_data="AgreeWindow_Rejoin")]
    ]
    rulesMark = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return rulesMark
#------ Goods -------#
def AllGoodsBtn():
    GoodsBtn = [[inBtn(text= "Хочу Анимации экслюзивного провайдера", url= "https://t.me/DeFaustus", callback_data="goods_exlusive")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=GoodsBtn)
    return keyboard





