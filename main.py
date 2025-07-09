import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from collections.abc import Sequence
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import aiosmtplib
from email.message import EmailMessage
from typing import Any

ADMINS = [552379435, 2077000128]
SMTP_EMAIL = "lackytek@gmail.com"
SMTP_PASSWORD = "btplwoezaftagsxh"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if TOKEN is None:
    raise ValueError("Переменная окружения BOT_TOKEN не задана!")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderForm(StatesGroup):
    fio = State()
    phone = State()
    address = State()
    grind = State()
    payment_screenshot = State()

def main_menu():
    kb = [
        [InlineKeyboardButton(text="☕️ Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🚚 Доставка и оплата", callback_data="shipping")],
        [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="question")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def catalog_menu():
    kb = [
        [InlineKeyboardButton(text="Кофе 250г зерно (попробовать)", callback_data="coffee_250")],
        [InlineKeyboardButton(text="Кофе 1000г зерно (распробовать)", callback_data="coffee_1000")],
        [InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="main_menu")]])

async def send_order_email(subject, body, to_email):
    try:
        message = EmailMessage()
        message["From"] = SMTP_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_EMAIL,
            password=SMTP_PASSWORD
        )
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "Добро пожаловать в магазин Дзен Кофе!\n\nВыберите нужный раздел 👇",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "main_menu")
async def show_main_menu(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(callback.from_user.id, "Выберите нужный раздел 👇", reply_markup=main_menu())

@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(callback.from_user.id, "Наш каталог кофе:", reply_markup=catalog_menu())

@dp.callback_query(F.data == "coffee_250")
async def coffee_250(callback: types.CallbackQuery):
    photos = [
        "https://i.postimg.cc/B62Cc79J/IMG-20250519-134553-449.jpg",
        "https://i.postimg.cc/tCk2Mc1T/IMG-20250519-134852-540.jpg",
        "https://i.postimg.cc/ht3MS71R/IMG-20250519-135251-240.jpg",
        "https://i.postimg.cc/CLScJ0xX/IMG-20250519-140407-682.jpg",
        "https://i.postimg.cc/W4BnZLy9/IMG-20250519-141312-478.jpg",
        "https://i.postimg.cc/s2Qm1DTQ/IMG-20250618-201659-663.jpg"
    ]
    media: Sequence = [InputMediaPhoto(media=url) for url in photos]
    await callback.answer()
    await bot.send_media_group(callback.from_user.id, media)
    await bot.send_message(
        callback.from_user.id,
        "☕️ <b>Дзен Кофе — Суль де Минас 250 г</b>\n749 ₽\nСредняя обжарка, в день заказа.\nВкус: шоколад, орехи, лёгкая кислинка.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить", callback_data="buy_250")],
            [InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="catalog")]
        ]),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "coffee_1000")
async def coffee_1000(callback: types.CallbackQuery):
    photos = [
        "https://i.postimg.cc/hPsdnWbk/1-1.png",
        "https://i.postimg.cc/zX8g4XWw/2.png",
        "https://i.postimg.cc/26WWN12G/3.png",
        "https://i.postimg.cc/y6FRfSJY/4.png",
        "https://i.postimg.cc/ZnFy01ky/5.png",
        "https://i.postimg.cc/jSqyndSq/6.png"
    ]
    media: Sequence = [InputMediaPhoto(media=url) for url in photos]
    await callback.answer()
    await bot.send_media_group(callback.from_user.id, media)
    await bot.send_message(
        callback.from_user.id,
        "☕️ <b>Дзен Кофе — Суль де Минас 1000 г</b>\n2399 ₽\nСредняя обжарка, в день заказа.\nВкус: шоколад, орехи, лёгкая кислинка.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить", callback_data="buy_1000")],
            [InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="catalog")]
        ]),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "buy_250")
async def buy_250(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await bot.send_message(callback.from_user.id, "Пожалуйста, заполните форму заказа.\n\nВаше <b>ФИО</b>:", parse_mode="HTML", reply_markup=back_menu())
    await state.set_state(OrderForm.fio)
    await state.update_data(weight="250 г", paylink="https://yookassa.ru/my/i/aF6PZhaxXQmX/l")

@dp.callback_query(F.data == "buy_1000")
async def buy_1000(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await bot.send_message(callback.from_user.id, "Пожалуйста, заполните форму заказа.\n\nВаше <b>ФИО</b>:", parse_mode="HTML", reply_markup=back_menu())
    await state.set_state(OrderForm.fio)
    await state.update_data(weight="1000 г", paylink="https://yookassa.ru/my/i/aF6QF8z6dd86/l")

@dp.message(OrderForm.fio)
async def order_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await bot.send_message(message.chat.id, "Ваш <b>Телефон</b>:", parse_mode="HTML", reply_markup=back_menu())
    await state.set_state(OrderForm.phone)

@dp.message(OrderForm.phone)
async def order_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await bot.send_message(message.chat.id, "Ваш <b>Адрес доставки</b>:", parse_mode="HTML", reply_markup=back_menu())
    await state.set_state(OrderForm.address)

@dp.message(OrderForm.address)
async def order_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await bot.send_message(message.chat.id, "Нужен ли помол? Если да — под какой способ?", reply_markup=back_menu())
    await state.set_state(OrderForm.grind)

@dp.message(OrderForm.grind)
async def order_grind(message: types.Message, state: FSMContext):
    data: dict[str, Any] = await state.get_data() or {}
    await state.update_data(grind=message.text)
    addr = data.get('address', '').lower()
    city_bonus = ""
    if "екатеринбург" in addr:
        city_bonus = "\n\n🎉 Поздравляем! Заказ для Екатеринбурга — бесплатная доставка курьером за наш счёт!"
    await bot.send_message(
        message.chat.id,
        f"Отлично! Остался последний шаг — <b>оплата</b>.\n\n"
        f"Вы выбрали: {data.get('weight', '')}\n"
        f"<a href='{data.get('paylink', '')}'>💳 Оплатить</a>\n\n"
        f"После оплаты прикрепите скрин и напишите адрес для отправки.{city_bonus}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=back_menu()
    )
    await bot.send_message(message.chat.id, "Прикрепите скрин оплаты (отправьте фото):")
    await state.set_state(OrderForm.payment_screenshot)

@dp.message(OrderForm.payment_screenshot, F.photo)
async def order_payment_screenshot(message: types.Message, state: FSMContext):
    if not message.photo or len(message.photo) == 0:
        await bot.send_message(message.chat.id,                  "Пожалуйста, отправьте фото (скрин оплаты)!")
        return  # ← обязательно!
    photo_id = message.photo[-1].file_id
    data: dict[str, Any] = await state.get_data() or {}
    order_text = (
        "Новый заказ Дзен Кофе!\n"
        f"ФИО: {data.get('fio', '')}\n"
        f"Телефон: {data.get('phone', '')}\n"
        f"Адрес: {data.get('address', '')}\n"
        f"Помол: {data.get('grind', '')}\n"
        f"Вес: {data.get('weight', '')}\n"
    )
    for admin in ADMINS:
        try:
            await bot.send_message(admin, order_text)
            await bot.send_photo(admin, photo_id)
        except Exception as e:
            print(f"Ошибка при отправке админу {admin}: {e}")
    await send_order_email(
        "Новый заказ Дзен Кофе",
        order_text,
        SMTP_EMAIL
    )
    await bot.send_message(message.chat.id, "Спасибо за заказ! Мы свяжемся с вами в ближайшее время.", reply_markup=main_menu())
    await state.clear()

@dp.callback_query(F.data == "shipping")
async def shipping(callback: types.CallbackQuery):
    await callback.answer()
    kb = [
        [InlineKeyboardButton(text="Доставка", callback_data="shipping_info")],
        [InlineKeyboardButton(text="Оплата", callback_data="payment_info")],
        [InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="main_menu")]
    ]
    await bot.send_message(callback.from_user.id, "Выберите раздел:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data == "shipping_info")
async def shipping_info(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        "🚚 <b>Доставка</b>\n\n"
        "• 5Post — пункты выдачи в большинстве городов РФ\n"
        "• СДЭК — пункты и курьерская доставка по всей России\n"
        "• Почта России — отправка в любую точку РФ\n"
        "• Курьерская доставка — доставка курьером только по Екатеринбургу, бесплатно!\n\n"
        "Сроки: от 1 до 7 дней, зависит от выбранной службы и региона.\n"
        "Стоимость и сроки доставки в другие регионы рассчитываются индивидуально.\n\n"
        "❗️После оформления заказа наш менеджер свяжется для подтверждения адреса и уточнения способа доставки. Обязательно оставляйте контактные данные.",
        parse_mode="HTML",
        reply_markup=back_menu()
    )

@dp.callback_query(F.data == "payment_info")
async def payment_info(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        "💳 <b>Оплата</b>\n"
        "Оплата производится через сервис ЮКасса, в ней Вы можете выбрать удобный для Вас способ. \n"
        "Например:\n"
        "- SberPay\n"
        "- Банковской картой\n"
        "- Кошельком ЮMoney\n"
        "- СБП",
        parse_mode="HTML",
        reply_markup=back_menu()
    )

@dp.callback_query(F.data == "question")
async def question(callback: types.CallbackQuery):
    await callback.answer()
    kb = [
        [InlineKeyboardButton(text="Telegram: @skybiker01", url="https://t.me/skybiker01")],
        [InlineKeyboardButton(text="Telegram: @kirillshishkin29", url="https://t.me/kirillshishkin29")],
        [InlineKeyboardButton(text="Сайт", url="https://dzencoffee.ru")],
        [InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="main_menu")]
    ]
    await bot.send_message(
        callback.from_user.id,
        "Свяжитесь с нами любым удобным способом:\n"
        "Почта: dzencoffee@mail.ru",  # ← почта просто в тексте!
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@dp.callback_query(F.data == "about")
async def about(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        "В мире, где все спешат и пьют кофе на бегу, мы выбрали другой путь ☕\n"
        "Для нас кофе — не просто способ взбодриться, а особый ритуал: короткая пауза, чтобы замедлиться, почувствовать вкус жизни и найти спокойствие внутри 🧘‍♂️\n\n"
        "Мы создаём кофе для тех, кто умеет остановиться, насладиться моментом и набраться сил — чтобы потом двигаться дальше уже осознанно ✨\n\n"
        "Используем только 100% арабику: лучшие зёрна, которые мы нашли 🌱\n"
        "Без ароматизаторов и компромиссов.\n"
        "Мы не храним кофе на складе — обжариваем его только после вашего заказа, чтобы сохранить свежесть, глубокий и мягкий вкус, без лишней кислинки и горечи 🥄\n\n"
        "Это не просто кофе.\n"
        "Это напоминание: жизнь — не гонка, а моменты, которые стоит проживать с удовольствием 🤍",
        parse_mode="HTML",
        reply_markup=back_menu()
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
