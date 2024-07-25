from aiogram import Bot, Dispatcher, types
import logging
import asyncio
from aiogram.filters.command import Command
from Tkn import Token
import json


#------ PARAMETRS BLOCK ------#
btn = types.KeyboardButton
logging.basicConfig(level = logging.INFO)

bot = Bot(token = Token)
dp = Dispatcher()

@dp.message(Command('hah'))
async def hah(message: types.Message):
    chatid = 1239679779
    fromchat = -1001815019206
    dict = {}
    with open("channel_data.json", 'w+') as file_data:
        for x in range(0,20):
            try: 
                receive = await bot.forward_message(
                chat_id= chatid, 
                from_chat_id = fromchat, 
                message_id=x, 
                protect_content=True)

                caption = f"{receive.caption}"
                if receive.caption is not None:
                    dict[caption] = x
                    print(x)
                    print("reply")
            except: 
                print()
        print(dict)
        file_data.write(str(dict).replace("'", "\""))

def GetDict():
    with open("channel_data.json", 'r') as file:
        data = json.load(file)
        return data
    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

