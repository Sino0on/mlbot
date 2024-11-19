import asyncio
from pprint import pprint
from sys import prefix

from aiogram import Bot, Dispatcher, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio
import logging
import sys

from aiogram.types import Message
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart, Command
from decouple import config
from django.contrib.admin import StackedInline

from states import PaymentState
from utils import get_all_packs, get_user_id, create_payment, create_link

from db import db


TOKEN = '5346235377:AAGg1mWc4FPRxGn1GFcnOBcj75MMLlrAJlA'

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())


# Определяем CallbackData для стран и городов
class CountryCallback(CallbackData, prefix="country"):
    name: str


class CityCallback(CallbackData, prefix="city"):
    name: str
    country: str

class InputCallback(CallbackData, prefix="input"):
    user_id: str
    price: str
    status: bool


# Хэндлер для команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Создаем клавиатуру с кнопками стран
    countries = [("🇰🇬 Кыргызстан", "Кыргызстан"), ("🇺🇿 Узбекистан", "Узбекистан"), ("🇰🇿 Казахстан", "Казахстан")]
    buttons = [
        [types.InlineKeyboardButton(text=text, callback_data=CountryCallback(name=name).pack())]
        for text, name in countries
    ]
    data_from_db = db.get_single()
    print(data_from_db)
    buttons.append(
        [types.InlineKeyboardButton(text="✍️ Поддержка", url=data_from_db['podderjka']),
        types.InlineKeyboardButton(text="✅ Канал", url=data_from_db['canal']),]
    )
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Привет! Выбери страну:", reply_markup=keyboard)


# Хэндлер для выбора страны
@dp.callback_query(CountryCallback.filter())
async def process_country_callback(callback: types.CallbackQuery, callback_data: CountryCallback):

    country_name = callback_data.name
    await callback.message.delete()

    # Создаем новую клавиатуру с тарифами
    packs = get_all_packs()
    cities = [(f"💎 {good['title']}", f'{good['title']}') for good in packs]
    buttons = [
        [
            types.InlineKeyboardButton(text=text, callback_data=CityCallback(name=name, country=country_name).pack())
            for text, name in cities[i:i + 2]
        ]
        for i in range(0, len(cities), 2)
    ]
    buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="start")
    ])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(f"Ты выбрал {country_name.capitalize()}. Теперь выбери тариф:", reply_markup=keyboard)


# Хэндлер для кнопки "Назад" (команда /start)
@dp.callback_query(lambda callback: callback.data == "start")
async def process_back_to_start(callback: types.CallbackQuery):
    await callback.message.delete()
    await start_command(callback.message)

@dp.callback_query(lambda callback: callback.data == "payment")
async def process_payment_to_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(PaymentState.user_id)
    await callback.message.answer('Напишите свой ID аккаунта')


@dp.callback_query(InputCallback.filter())
async def process_payment_to_end(callback: types.CallbackQuery, callback_data: InputCallback, state: FSMContext):
    user_id = callback_data.user_id
    status = callback_data.status
    data = await state.get_data()
    if status:
        buttons = [
            [types.InlineKeyboardButton(text="✅✅ Принято и оплачено ✅✅", callback_data='payment_accepted')]
        ]
    else:
        buttons = [
            [types.InlineKeyboardButton(text="🚫🚫 Отказано 🚫🚫", callback_data='payment_accepted')]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_reply_markup(reply_markup=keyboard, text=callback.message.text)
    if callback.message:
        await bot.send_message(chat_id=user_id, text='good' if status else 'bad')


# Хэндлер для выбора тарифа
@dp.callback_query(CityCallback.filter())
async def process_city_callback(callback: types.CallbackQuery, callback_data: CityCallback, state: FSMContext):
    city_name = callback_data.name
    country_name = callback_data.country
    await state.update_data(region=callback_data.country)
    await callback.message.delete()
    buttons = [[
        types.InlineKeyboardButton(text="💳 Купить", callback_data="payment"),
        types.InlineKeyboardButton(text="✍️ Поддержка", url="https://t.me/kbchmk"),
        ],
        [
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="start")
    ]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    # await callback.message.answer(f"Ты выбрал город {city_name.capitalize()} в стране {country_name.capitalize()}.", reply_markup=keyboard)
    packs = get_all_packs()
    good = [i for i in packs if i['title'] == city_name][0]
    photo_url = good['icon']

    price = good['pay_channel_sub'][0]['price_local_sell_precision']
    await state.update_data(price=price)

    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=photo_url,
        caption=f"Ты выбрал тариф {city_name.capitalize()} в стране {country_name.capitalize()}.\nСтоимость - {price} рублей",
        reply_markup=keyboard
    )

@dp.message(PaymentState.user_id)
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    user = get_user_id(message.text)
    if user:
        await state.update_data(username=user)
        await state.update_data(user_id=message.text)

        await state.set_state(PaymentState.check)
        data = await state.get_data()
        buttons = [[
            types.InlineKeyboardButton(text="🔙 Назад", callback_data="start"),
            types.InlineKeyboardButton(text="✍️ Поддержка", url="https://t.me/kbchmk"),
            ]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        countres = {
            "Кыргызстан": "kg",
            "Казахстан": "kz",
            "Узбекистан": "uz",
        }
        recvisits = db.get_recvisits(region=countres[data['region']])

        await message.reply(
            f"""Пользователь найден - {user}\nПожалуйста отправьте чек оплаты\n{"\n".join([f"{a.title} - {a.number}" for a in recvisits])}\nСумма перевода - {data['price']}""",
            reply_markup=keyboard,
        )
    else:
        await message.answer("ID аккаунта не найден. Пожалуйста, попробуйте снова.")
        return  # Прерываем выполнение функции, если user отсутствует


@dp.message(PaymentState.check, F.photo)
async def process_image_upload(message: Message, state: FSMContext) -> None:
    # Проверяем, что пользователь отправил изображение
    if not message.photo:
        await message.answer("Пожалуйста, отправьте изображение.")
        return  # Прерываем выполнение, если изображение отсутствует

    # Получаем файл изображения
    photo = message.photo[-1]  # Берем изображение с наивысшим разрешением
    file_id = photo.file_id

    # Сохраняем file_id в состоянии
    await state.update_data(photo_file_id=file_id)
    data_from_db = db.get_single()
    # Переход к следующему состоянию или выполнение дальнейших действий
    await state.set_state(PaymentState)  # Укажите нужное состояние
    buttons = [
        [types.InlineKeyboardButton(text="✍️ Поддержка", url=data_from_db['podderjka']),
         types.InlineKeyboardButton(text="✅ Канал", url=data_from_db['canal']), ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply(
        "✅Спасибо.\n✅Пожалуйста дождитесь модерации оплаты",
        reply_markup=keyboard
    )
    data = await state.get_data()
    pprint(data)
    data_from_db = db.get_single()
    response = create_payment(data['user_id'], str(data['price']), data_from_db['mail'])
    pprint(response)
    response = create_link(response['data']['order_id'])
    url = response['data']['payment_url']
    await state.update_data(url=url)
    buttons = [
        [types.InlineKeyboardButton(text="✅ Принять", callback_data=InputCallback(user_id=f'{message.from_user.id}', price=f"{data['price']}", status=True).pack()),
         types.InlineKeyboardButton(text="🚫 Отказ", callback_data=InputCallback(user_id=f'{message.from_user.id}', price=f"{data['price']}", status=False).pack()), ]
    ]
    buttons.append([types.InlineKeyboardButton(text="🕐 Оплатить", url=url)])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_photo(chat_id='-1002290257071', photo=file_id, caption=f'Новый Чек ⬆️⬆️\nОплата на аккаунт {data['user_id']} - {data['username']}\nСумма - {data['price']}\nРегион - {data['region']}', reply_markup=keyboard)

@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls


    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())