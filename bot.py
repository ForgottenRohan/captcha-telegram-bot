import logging
import sys
import random
import string
from threading import Timer
from pyperclip import copy

import asyncio

from aiogram import Bot, Dispatcher, types, Router
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.filters.command import Command, CommandStart
from aiogram.types.input_file import BufferedInputFile
from captcha.image import ImageCaptcha


#logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
#consts
Token = 'Token'
Admin = 'admin'
bot = Bot(Token)
dp = Dispatcher()
router = Router()
links = []
captcha = {}
info_message = 'INFO'

#funcs
def generate_captcha():
    image = ImageCaptcha()
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    captcha_image = image.generate(captcha_text)
    captcha_image = captcha_image.read()
    return captcha_text, captcha_image


@dp.message(CommandStart())
async def start(message: types.Message):
    captcha_text, captcha_image = generate_captcha()
    captcha_file = BufferedInputFile(captcha_image, filename='captcha.png')
    await message.answer_photo(photo=captcha_file, caption='Пожалуйста введите текст с избражения!\nТолько заглавные буквы')
    captcha[message.from_user.id] = captcha_text
    print(captcha_text)
    copy(captcha_text)

@dp.message(lambda message: captcha[message.from_user.id])
async def check_captcha(message: types.Message):
    user_captcha = message.text
    if user_captcha != captcha[message.from_user.id]:
        await message.answer(text='Неверная капча')
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Получить ссылку', callback_data='get_link')],
            [InlineKeyboardButton(text='Инфо', callback_data='get_info')]
        ])
        await message.answer(text='Выберите действие', reply_markup=keyboard)
    # if user_captcha == :
    #     keyboard = InlineKeyboardMarkup(inline_keyboard=[
    #         [InlineKeyboardButton(text='Получить ссылку', callback_data='get_link')],
    #         [InlineKeyboardButton(text='Инфо', callback_data='get_info')]
    #     ])
    #     await message.answer(text='Выберите действие', reply_markup=keyboard)
    #     dp.storage.set_data(message.from_user.id, [''])
    # else:
    #     await message.answer(text='Неверная капча')


@dp.callback_query()
async def button(callback_query: types.CallbackQuery):
    if callback_query.data == "get_link":
        link = f'https://t.me/joinchat/{generate_unique_link()}'
        timer = Timer(900, delete_link, [callback_query.from_user.id, link])
        timer.start()
        await callback_query.message.edit_text(f"Ваша одноразовая ссылка: {link}")
    elif callback_query.data == "get_info":
        await callback_query.message.edit_text(info_message)



def generate_unique_link():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


def delete_link(link: str):
    if link in links:
        del links[link]


@dp.message(Command('broadcast'))
async def broadcast(message: types.Message):
    if message.from_user.id == Admin:
        broadcast_message = message.text.replace('/broadcast ', '')
        for user_id in dp.storage.get_data():
            await bot.send_message(user_id, broadcast_message)


@dp.message(Command('editinfo'))
async def editinfo(message: types.Message):
    if message.from_user.id == Admin:
        global info_message
        info_message = message.text.replace('/editinfo ', '')
        await message.answer('Инфо обновлено!')

# @router.message()
# async def add_user(message: types.Message):
#     dp.storage.set_data(message.from_user.id, [''])

     
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())