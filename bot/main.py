from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram import exceptions
import logging
from aiogram.filters.command import Command
import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile


import io
from PIL import Image, ImageDraw
import sys
import zipfile
import numpy as np
import time

from aiohttp import web
from aiocryptopay import AioCryptoPay, Networks

sys.path.append("H:\\icreo\\lol\\")
import imageMatrix
import messages
from Tkn import Token, cryptoToken
import markups
import ErrorsHandler
import dataBase

#------ PARAMETRS BLOCK ------#
bot = Bot(token = Token)
dp = Dispatcher()
router = Router()


class Payment(StatesGroup):
    choose_sum = State()
    createInvoice = State()

#------ START BLOCK ------#
@dp.message(Command('start'))
async def start(message: types.Message, id=0):
    tgid = message.from_user.id if id==0 else id
    await message.answer(messages.hello(message.from_user.full_name), reply_markup=markups.mainBtn(), parse_mode="Markdown")

@dp.message(Command('send_broadcast'))
async def sendBroadcast(message: types.Message):
    if message.from_user.id == 1239679779:
        text = message.text.format()
        text = message.text.replace("/send_broadcast","")
        await dataBase.sendBroadcast(bot.send_message, text)
    else:
        await message.answer("Доступно только разработчику -> @Me4tatelnitca")

@dp.message(F.text.contains("На главную"))
async def Main(message: types.Message):
    await message.answer(text = "*На главной, Выбираем что хотим, рынок все-таки*",reply_markup=markups.mainBtn(), parse_mode="Markdown")

#------ INFO BLOCK ------#
@dp.message(F.text == "О Сервисе ❤️")
async def info_messages(message: types.Message):
    await message.reply(messages.about(), reply_markup=markups.About(), parse_mode="HTML")

@dp.callback_query(F.data.contains('About'))
async def About(callbback: types.CallbackQuery):
    data = callbback.data.split('_')[1]
    if(data == 'Me'):
        try: await callbback.message.edit_text(messages.AboutMe(), reply_markup=markups.About(), parse_mode="HTML")
        except: await callbback.answer()
    if(data == "Ecosystem"):
        try: await callbback.message.edit_text(messages.Ecosystem(), reply_markup=markups.About(), parse_mode="HTML")
        except: await callbback.answer()

@dp.message(F.text == "👊 Профиль")
async def info_messages(message: types.Message):
        await message.reply(messages.InfoProfile(message.from_user.id, message.from_user.first_name), reply_markup=markups.Profile(), parse_mode="Markdown")

#------ GOODS BLOCK -----#

@dp.message(F.text == "🔥 Элементы для креосов 🔥")
async def func(message: types.Message):
    await message.answer("*Все информация тут: @GamblElements*", reply_markup=markups.AllGoodsBtn(), parse_mode="Markdown")

#Scripts
@dp.message(F.text == "⭐️Все Скрипты⭐️")
async def AllScripts(message: types.Message):
    await message.answer("*Выберите скрипт с которым хотите начать работу.*", reply_markup=markups.Scripts(), parse_mode="Markdown")

class ImageDivider(StatesGroup):
    sendImage = State()
    getImage = State()

@dp.callback_query(F.data.contains('ImageDivider'))
async def About(callbback: types.CallbackQuery, state: FSMContext):
    await callbback.message.edit_text("*Отправьте фотографию (не сжимая) с которой начнем работу*", parse_mode="Markdown")
    await state.set_state(ImageDivider.sendImage)

@dp.message(ImageDivider.sendImage)
async def Step1(message: types.Message, state: FSMContext):
    try:
        if not message.document.mime_type.__contains__("png"):
            raise imageMatrix.IncorrectType(message.document.mime_type)
        file_id = message.document.file_id 
        file = await bot.get_file(file_id)
        file_path = file.file_path
        nameFile = message.document.file_name
        binary = io.BytesIO()
        await bot.download_file(file_path, binary)
        image = Image.open(binary).convert("RGBA")
        imageExport = image.copy()
        msg = await message.reply(text="🤝 Файл получен. Ожидайте отправки макета разрезки.")
        await state.update_data(BarId = msg.message_id, BarText = msg.text)
        await state.update_data(image = image)
        await state.update_data(imageExport = imageExport)
        # await state.update_data(userId = message.document)
        await state.update_data(nameFile = nameFile.replace('.png', '.zip'))
        await state.update_data(idChat = message.chat.id)
        await state.set_state(ImageDivider.getImage)
        await Step2(state, message)
    except imageMatrix.IncorrectType as Exp:
        await message.answer(text = f"*{str(Exp)}*\nОжидаю отправки корректного файла",reply_markup=markups.ExitFromImageMatrix(), parse_mode="Markdown")
    except AttributeError:
        await message.answer(text = f"*Неккоректный тип файла\nОжидаю отправки корректного файла*",reply_markup=markups.ExitFromImageMatrix(), parse_mode="Markdown")
    except exceptions.TelegramServerError:
        await message.answer(text = f"*Ошибка на стороне сервера Телеграмм*",reply_markup=markups.ExitFromImageMatrix(), parse_mode="Markdown")
    except Exception as Ex:
        await message.answer(text=f"*Возникла непредвиденная ошибка.*", parse_mode="Markdown")
        await ErrorsHandler.ExceptionHandler(Ex,message.from_user.id,"imageDivider")
        await AllScripts(message)

async def Step2(state: FSMContext, message: types.Message, percent = 40):
    async def Cutter(matrix,direction="Left",setAlpha=0,checkSum=0,step=2, dataChat = {}, state = state):
        try:
            height,width = matrix.shape
            PointsWeight = height*width / 100
            Percent = percent
            TIMEOUT = 60 #seconds
            CutterizeINFO = []
            config = {"Left": {"CheckLine":"Linear","CaptureImage": "LeftTop"}}
            for StartY in range(0, height, step):
                StartX = imageMatrix.CheckLine(Line=matrix[StartY], dir = config[direction]["CheckLine"])
                if StartX == False: continue
                checkSum=0
                startTime = time.time()
                while True:
                    # print(checkSum)
                    if startTime+TIMEOUT<time.time(): raise asyncio.exceptions.CancelledError
                    try: temp = imageMatrix.CaptureImage(matrix, StartX, StartY, checkSum, setAlpha, direction=config[direction]["CaptureImage"])            
                    except imageMatrix.DiagonalException as e: break
                    except Exception as e: ErrorsHandler.ExceptionHandler(e,message.from_user.id,"imageDivider");break
                    ImageToAllPoints = abs((temp[2] - temp[0]) * (temp[3] - temp[1])) / PointsWeight
                    if ImageToAllPoints > Percent: 
                        if checkSum < 500:
                            checkSum+=10
                        elif checkSum < 1500:
                            checkSum+=20
                        elif checkSum < 5000:
                            checkSum+=50
                        else:
                            checkSum+=100
                    else: 
                        matrix = imageMatrix.LogicalCut(matrix=matrix, massive=temp)
                        CutterizeINFO.append(temp)
                        break

                progress = StartY*100/height
                try:
                    await bot.edit_message_text(text=f"{dataChat['BarText']}\n*Прогресс: {round(progress,2)}%*\n\nМаксимальное время ожидания: {TIMEOUT*3}секунд", 
                                        chat_id=dataChat["idChat"], 
                                        message_id=dataChat["BarId"],
                                        reply_markup=markups.ExitFromImageMatrix(),
                                        parse_mode="Markdown")
                except: ()

            if np.sum(matrix)/255/PointsWeight*100 > 30 and dataChat != {}:
                for x in await Cutter(matrix, direction,setAlpha,checkSum, step=1):
                    CutterizeINFO.append(x)

            if dataChat != {}:
                await bot.edit_message_text(text=f"_Осталось секундочка._ \n*Прогресс: 100%*", 
                                        chat_id=dataChat["idChat"], 
                                        message_id=dataChat["BarId"],
                                        reply_markup=markups.ExitFromImageMatrix(),
                                        parse_mode="Markdown")
                await asyncio.sleep(2)
                await bot.delete_message(chat_id=dataChat["idChat"], 
                                    message_id=dataChat["BarId"])     
            return CutterizeINFO
        
        except asyncio.exceptions.CancelledError as TimeErr:
            await bot.send_message(data["idChat"], text=f"*Истекло время работы поиска изображения.\nВозможно упущены некоторые кадры.*\nПерезапустить с дефолтными параметрами?",parse_mode="Markdown",reply_markup=markups.Accept2()) 
            return CutterizeINFO
        except Exception as Err:
            await bot.send_message(data["idChat"], text=f"*Возникла непредвиденная ошибка.*\nПерезапустить с дефолтными параметрами?",parse_mode="Markdown",reply_markup=markups.Accept2())
            ErrorsHandler.ExceptionHandler(Err, message.from_user.id, ScriptName="imageDivider")
            return CutterizeINFO
        
    data = await state.get_data()
    image = data["image"]
    dir = "Left"
    Alpha = 0
    chkSum = 0
    step = 5
    t = None
    matrix = imageMatrix.ExpandMatrix(imageMatrix.image_to_matrix(image))
    try:
        t = await Cutter(matrix, direction = dir, setAlpha=Alpha, checkSum=chkSum, step = step, dataChat=data, state=state)
        #return Pillow object
        imageCrops = imageMatrix.GetCrops(image,t)
        image_buffer = io.BytesIO()
        imageCrops.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        await state.update_data(Cutterize = t)
        await bot.send_photo(data["idChat"], photo=BufferedInputFile(image_buffer.getvalue(), filename='photo.png'), caption="*Подтверждаете разрезку?*", reply_markup=markups.Accept(), parse_mode="Markdown")
    except imageMatrix.DiagonalException as exc:
        await bot.send_message(data["idChat"], text=f"*😭 Возникла ошибка: {exc}.*\nСкорее всего ваше изображение не может быть разрезанным.\nИзвините, что алгоритм не идеален.", parse_mode="Markdown")
    except Exception as e:
        try:
            await bot.send_message(data["idChat"], text=f"*😭 Возникла непредвиденная ошибка.*\nНапишите нам в саппорт, если такое будет повторяться: @DeFaustus", parse_mode="Markdown")
            ErrorsHandler.ExceptionHandler(e, message.from_user.id, ScriptName="imageDivider")
        except exceptions.TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 10)
            await bot.send_message(data["idChat"], text=f"*😭 Возникла ошибка:  Telegram server says - Flood control.*\nВам был выдан таймаут на {e.retry_after} секунд от самого телеграмм\n*В данный момент он недействителен.*\n\n||*Убедительная просьба делать менее частое кол-во запросов, дабы не словить таймаут на большее время||", parse_mode="Markdown")
            await state.clear()

@dp.callback_query(F.data.contains('AgreeWindow_Yes'))
async def EndStep(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if len(data) == 0:
        await callback.answer(text="Данные стерты")
    else:
        List = imageMatrix.GetListImages(data["Cutterize"], data["imageExport"])
        archive_Buffer = io.BytesIO()
            
        with zipfile.ZipFile(archive_Buffer, 'w') as zipF:
                for i, image in enumerate(List):
                    imageBuff = io.BytesIO()
                    image.save(imageBuff, format="PNG")
                    imageBuff.seek(0)
                    
                    zipF.writestr(f'image_{i}.png', imageBuff.getvalue())
            
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await bot.send_document(callback.message.chat.id, document=BufferedInputFile(archive_Buffer.getvalue(), filename=data["nameFile"]))
        dataBase.updateCount(callback.message.chat.id,callback.from_user.full_name)
        await state.set_state(ImageDivider.sendImage)
    
@dp.callback_query(F.data.contains('AgreeWindow_No'))
async def NewStep(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await bot.send_message(callback.message.chat.id, text = "Ожидаю нового изображения", reply_markup=markups.ExitFromImageMatrix())
    await state.set_state(ImageDivider.sendImage)

@dp.callback_query(F.data.contains('AgreeWindow_Exit'))
async def ExitStep(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await state.clear()
    await AllScripts(callback.message)

@dp.callback_query(F.data.contains('AgreeWindow_Rejoin'))
async def RejoinStep(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    a = await callback.message.answer(text="Обработка изображения перезапущена с новыми параметрами")
    await state.update_data(BarId = a.message_id, BarText = a.text)
    await Step2(state, callback.message, percent = 80)
#----------- SEARCH ----------#
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    asyncio.run(main())
