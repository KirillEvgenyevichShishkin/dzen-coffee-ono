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
from typing import Any, Optional

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
        [InlineKeyboardButton(text="КАТАЛОГ", callback_data="catalog")],
        [InlineKeyboardButton(text="ДОСТАВКА И ОПЛАТА", callback_data="shipping")],
        [InlineKeyboardButton(text="ЗАДАТЬ ВОПРОС", callback_data="question")],
        [InlineKeyboardButton(text="ПОЧЕМУ ДЗЕН", callback_data="about")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def catalog_menu():
    kb = [
        [InlineKeyboardButton(text="КОФЕ 250Г ЗЕРНО", callback_data="coffee_250")],
        [InlineKeyboardButton(text="КОФЕ 1000Г ЗЕРНО", callback_data="coffee_1000")],
        [InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_to(prev_callback):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=prev_callback)],
            [InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]
        ]
    )

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]])

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

# --- Универсальная функция автоудаления сообщений бота ---
async def clean_last_message(
    message: Optional[types.Message] = None,
    callback: Optional[types.CallbackQuery] = None,
    state: Optional[FSMContext] = None
):
    if state is None:
        return
    data = await state.get_data() or {}
    last_bot_msg = data.get("last_bot_msg_id")
    try:
        if last_bot_msg is not None:
            if message is not None:
                await bot.delete_message(message.chat.id, last_bot_msg)
            elif callback is not None:
                await bot.delete_message(callback.from_user.id, last_bot_msg)
    except Exception:
        pass

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await clean_last_message(message=message, state=state)
    msg = await bot.send_photo(
        message.chat.id,
        "https://i.postimg.cc/Jn584dW1/image.png",
        caption="Добро пожаловать в магазин Дзен Кофе!\nМы обжариваем зерна специально для Вас и доставляем их в день обжарки или на следующий.\n- Так Вы получаете по-настоящему свежий кофе!\n\nЧтобы попробовать наш продукт, выберите нужный раздел 👇",
        reply_markup=main_menu()
    )
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "main_menu")
async def show_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await clean_last_message(callback=callback, state=state)
    msg = await bot.send_photo(
        callback.from_user.id,
        "https://i.postimg.cc/Jn584dW1/image.png",
        caption="Мы обжариваем зерна специально для Вас и доставляем их в день обжарки или на следующий.  - Так Вы получаете по-настоящему свежий кофе!\n\nЧтобы попробовать наш продукт, выберите нужный раздел 👇",
        reply_markup=main_menu()
    )
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery, state: FSMContext):
    await clean_last_message(callback=callback, state=state)
    msg = await bot.send_photo(
        callback.from_user.id,
        "https://i.postimg.cc/pXBGTb7h/image.jpg",
        caption="Наш небольшой каталог кофе:",
        reply_markup=catalog_menu()
    )
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "coffee_250")
async def coffee_250(callback: types.CallbackQuery, state: FSMContext):
    # Не удаляем сообщения — после этих кнопок история сохраняется!
    photos = [
        "https://i.postimg.cc/x825ft33/image.png",
        "https://i.postimg.cc/CLJ70CBb/250.jpg",
        "https://i.postimg.cc/CxPcGCww/250.jpg"
    ]
    media: Sequence = [InputMediaPhoto(media=url) for url in photos]
    await callback.answer()
    await bot.send_media_group(callback.from_user.id, media)
    await bot.send_message(
        callback.from_user.id,
        "☕️ <b>Дзен Кофе — Суль де Минас 250 г</b>\n749 ₽\nСредняя обжарка, в день заказа.\nЕстественный вкус: шоколад, орехи, лёгкая кислинка. (без ароматизаторов)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="КУПИТЬ", callback_data="buy_250")],
            [InlineKeyboardButton(text="КАТАЛОГ", callback_data="catalog")],
            [InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "coffee_1000")
async def coffee_1000(callback: types.CallbackQuery, state: FSMContext):
    # Не удаляем сообщения — после этих кнопок история сохраняется!
    photos = [
        "https://i.postimg.cc/vTtzcfPF/1000.jpg",
        "https://i.postimg.cc/4xS17J1d/1000.jpg",
        "https://i.postimg.cc/Hx531fXL/1000.jpg"
    ]
    media: Sequence = [InputMediaPhoto(media=url) for url in photos]
    await callback.answer()
    await bot.send_media_group(callback.from_user.id, media)
    await bot.send_message(
        callback.from_user.id,
        "☕️ <b>Дзен Кофе — Суль де Минас 1000 г</b>\n2399 ₽\nСредняя обжарка, в день заказа.\nЕстественный вкус: шоколад, орехи, лёгкая кислинка. (без ароматизаторов)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="КУПИТЬ", callback_data="buy_1000")],
            [InlineKeyboardButton(text="КАТАЛОГ", callback_data="catalog")],
            [InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "buy_250")
async def buy_250(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await bot.send_message(callback.from_user.id, "Пожалуйста, заполните форму заказа.\nСсылка для оплаты появится после заполнения.\n\nВаше <b>ФИО</b>:", parse_mode="HTML", reply_markup=back_to("catalog"))
    await state.set_state(OrderForm.fio)
    await state.update_data(weight="250 г", paylink="https://yookassa.ru/my/i/aF6PZhaxXQmX/l")

@dp.callback_query(F.data == "buy_1000")
async def buy_1000(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await bot.send_message(callback.from_user.id, "Пожалуйста, заполните форму заказа.\nСсылка для оплаты появится после заполнения.\n\nВаше <b>ФИО</b>:", parse_mode="HTML", reply_markup=back_to("catalog"))
    await state.set_state(OrderForm.fio)
    await state.update_data(weight="1000 г", paylink="https://yookassa.ru/my/i/aF6QF8z6dd86/l")

@dp.callback_query(F.data == "back_to_fio")
async def go_to_fio(callback: types.CallbackQuery, state: FSMContext):
    msg = await bot.send_message(callback.from_user.id, "Ваше <b>ФИО</b>:", parse_mode="HTML", reply_markup=back_to("catalog"))
    await state.set_state(OrderForm.fio)
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "back_to_phone")
async def go_to_phone(callback: types.CallbackQuery, state: FSMContext):
    msg = await bot.send_message(callback.from_user.id, "Ваш <b>Телефон</b>:", parse_mode="HTML", reply_markup=back_to("back_to_fio"))
    await state.set_state(OrderForm.phone)
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "back_to_address")
async def go_to_address(callback: types.CallbackQuery, state: FSMContext):
    msg = await bot.send_message(callback.from_user.id, "Ваш <b>Адрес доставки</b>:", parse_mode="HTML", reply_markup=back_to("back_to_phone"))
    await state.set_state(OrderForm.address)
    await state.update_data(last_bot_msg_id=msg.message_id)

#@dp.callback_query(F.data == "back_to_grind")
#async def go_to_grind(callback: types.CallbackQuery, state: FSMContext):
#    msg = await bot.send_message(callback.from_user.id, "Нужен ли помол? Если да — под какой способ?", reply_markup=back_to("back_to_address"))
#    await state.set_state(OrderForm.grind)
#    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.message(OrderForm.fio)
async def order_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    msg = await bot.send_message(
        message.chat.id,
        "Ваш <b>Телефон</b>:",
        parse_mode="HTML",
        reply_markup=back_to("back_to_fio")
    )
    await state.set_state(OrderForm.phone)
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.message(OrderForm.phone)
async def order_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    msg = await bot.send_message(
        message.chat.id,
        "Ваш <b>Адрес доставки</b>:",
        parse_mode="HTML",
        reply_markup=back_to("back_to_phone")
    )
    await state.set_state(OrderForm.address)
    await state.update_data(last_bot_msg_id=msg.message_id)

#@dp.message(OrderForm.address)
#async def order_address(message: types.Message, state: FSMContext):
#    await state.update_data(address=message.text)
#    msg = await bot.send_message(
#        message.chat.id,
#        "Нужен ли помол? Если да — под какой способ?",
#        reply_markup=back_to("back_to_address")
#    )
#    await state.set_state(OrderForm.grind)
#    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.message(OrderForm.address)
async def order_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data() or {}
    addr = data.get('address', '').lower()
    city_bonus = ""
    if "екатеринбург" in addr:
        city_bonus = "\n\n🎉 Поздравляем! Заказ для Екатеринбурга — бесплатная доставка курьером за наш счёт!"
    paylink = data.get('paylink', '')
    weight = data.get('weight', '')
    pay_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=paylink)],
        [InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]
    ])
    await bot.send_message(
        message.chat.id,
        f"Отлично! Остался последний шаг — <b>оплата</b>.\n\n"
        f"Вы выбрали: {weight}\n"
        f"После оплаты прикрепите скриншот что все получилось!{city_bonus}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=pay_kb
    )
    await bot.send_message(message.chat.id, "Прикрепите скрин оплаты (отправьте фото):")
    await state.set_state(OrderForm.payment_screenshot)

#@dp.message(OrderForm.grind)
#async def order_grind(message: types.Message, state: FSMContext):
#    await state.update_data(grind=message.text)
#    data: dict[str, Any] = await state.get_data() or {}
#    addr = data.get('address', '').lower()
#    city_bonus = ""
#    if "екатеринбург" in addr:
#        city_bonus = "\n\n🎉 Поздравляем! Заказ для Екатеринбурга — бесплатная доставка курьером за наш счёт!"
#    paylink = data.get('paylink', '')
#    weight = data.get('weight', '')
#    pay_kb = InlineKeyboardMarkup(inline_keyboard=[
#        [InlineKeyboardButton(text="💳 Оплатить", url=paylink)],
#        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_grind")],
#        [InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]
#    ])
#    await bot.send_message(
#        message.chat.id,
 #       f"Отлично! Остался последний шаг — <b>оплата</b>.\n\n"
 #       f"Вы выбрали: {weight}\n"
 #       f"После оплаты прикрепите скриншот что все получилось!{city_bonus}",
#        parse_mode="HTML",
#        disable_web_page_preview=True,
 #       reply_markup=pay_kb
#    )
#    await bot.send_message(message.chat.id, "Прикрепите скрин оплаты (отправьте фото):")
#    await state.set_state(OrderForm.payment_screenshot)

@dp.message(OrderForm.payment_screenshot, F.photo)
async def order_payment_screenshot(message: types.Message, state: FSMContext):
    data: dict[str, Any] = await state.get_data() or {}
    if not message.photo or len(message.photo) == 0:
        await bot.send_message(message.chat.id, "Пожалуйста, отправьте фото (скрин оплаты)!")
        return
    photo_id = message.photo[-1].file_id

    # Гарантированная защита от None
    from_user = message.from_user
    if from_user is not None:
        username = from_user.username if from_user.username else "нет"
        user_id = from_user.id
    else:
        username = "нет"
        user_id = "нет"

    order_text = (
        "Новый заказ Дзен Кофе!\n"
        f"ФИО: {data.get('fio', '')}\n"
        f"Телефон: {data.get('phone', '')}\n"
        f"Адрес: {data.get('address', '')}\n"
        f"Помол: {data.get('grind', '')}\n"
        f"Вес: {data.get('weight', '')}\n"
        f"Telegram: @{username} (ID: {user_id})"
    )
    user_link = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Связаться в Telegram",
            url=f"tg://user?id={user_id}"
        )]
    ])
    for admin in ADMINS:
        try:
            await bot.send_message(admin, order_text, reply_markup=user_link)
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

# Остальной функционал меню/доставки и др.
@dp.callback_query(F.data == "shipping")
async def shipping(callback: types.CallbackQuery, state: FSMContext):
    await clean_last_message(callback=callback, state=state)
    msg = await bot.send_photo(
        callback.from_user.id,
        "https://i.postimg.cc/VNJDDSNn/250.jpg",
        caption="Выберите раздел:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="О ДОСТАВКЕ", callback_data="shipping_info")],
            [InlineKeyboardButton(text="ОБ ОПЛАТЕ", callback_data="payment_info")],
            [InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]
        ])
    )
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "shipping_info")
async def shipping_info(callback: types.CallbackQuery, state: FSMContext):
    await clean_last_message(callback=callback, state=state)
    msg = await bot.send_message(
        callback.from_user.id,
        "🚚 <b>О Доставке</b>\n\n"
        "Мы работаем с несколькими службами доставки:\n"
        "• 5Post — пункты выдачи в большинстве городов РФ\n"
        "• СДЭК — пункты и курьерская доставка по всей России\n"
        "• Почта России — отправка в любую точку РФ\n"
        "• Курьерская доставка — доставка курьером только по Екатеринбургу, бесплатно!\n\n"
        "Доставка в день заказа или на следующий день работает только для Екатеринбурга.\n"
        "Сроки: от 1 до 7 дней, зависит от выбранной службы и региона.\n"
        "Стоимость и сроки доставки в другие регионы рассчитываются индивидуально.\n\n"
        "❗️После оформления заказа наш менеджер свяжется для подтверждения адреса и уточнения способа доставки. Обязательно оставляйте контактные данные.",
        parse_mode="HTML",
        reply_markup=back_menu()
    )
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "payment_info")
async def payment_info(callback: types.CallbackQuery, state: FSMContext):
    await clean_last_message(callback=callback, state=state)
    msg = await bot.send_message(
        callback.from_user.id,
        "💳 <b>Об Оплате</b>\n"
        "Оплата производится через сервис ЮКасса, в ней Вы можете выбрать удобный для Вас способ. \n"
        "Способы оплаты:\n"
        "- SberPay\n"
        "- Банковской картой\n"
        "- Кошельком ЮMoney\n"
        "- СБП\n\n"
        "Заказать товар и перейти к оплате можно в разделе <b>Каталог</b>.",
        parse_mode="HTML",
        reply_markup=back_menu()
    )
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "question")
async def question(callback: types.CallbackQuery, state: FSMContext):
    await clean_last_message(callback=callback, state=state)
    kb = [
        [InlineKeyboardButton(text="ЕВГЕНИЙ", url="https://t.me/skybiker01")],
        [InlineKeyboardButton(text="КИРИЛЛ", url="https://t.me/kirillshishkin29")],
        [InlineKeyboardButton(text="НАШ САЙТ", url="https://dzencoffee.ru")],
        [InlineKeyboardButton(text="МЕНЮ", callback_data="main_menu")]
    ]
    msg = await bot.send_photo(
        callback.from_user.id,
        "https://i.postimg.cc/XYGCP9wj/IMG-20250711-173618-122.jpg",
        caption=(
            "Если у Вас появились вопросы, свяжитесь с нами любым удобным способом:\n"
            "Почта: dzencoffee@mail.ru"
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await state.update_data(last_bot_msg_id=msg.message_id)

@dp.callback_query(F.data == "about")
async def about(callback: types.CallbackQuery, state: FSMContext):
    await clean_last_message(callback=callback, state=state)
    msg = await bot.send_photo(
        callback.from_user.id,
        "https://i.postimg.cc/Bn6gn8Hk/250.jpg",
        caption=(
            "В мире, где все спешат и пьют кофе на бегу, мы выбрали другой путь ☕\n"
            "Для нас кофе — не просто способ взбодриться, а особый ритуал: короткая пауза, чтобы замедлиться, почувствовать вкус жизни и найти спокойствие внутри 🧘‍♂️\n\n"
            "Мы создаём кофе для тех, кто умеет остановиться, насладиться моментом и набраться сил — чтобы потом двигаться дальше уже осознанно ✨\n\n"
            "Используем только 100% арабику: лучшие зёрна, которые мы нашли 🌱\n"
            "Без ароматизаторов и компромиссов.\n"
            "Мы не храним кофе на складе — обжариваем его только после вашего заказа, чтобы сохранить свежесть, глубокий и мягкий вкус, без лишней кислинки и горечи 🥄\n\n"
            "Это не просто кофе.\n"
            "Это напоминание: жизнь — не гонка, а моменты, которые стоит проживать с удовольствием 🤍"
        ),
        parse_mode="HTML",
        reply_markup=back_menu()
    )
    await state.update_data(last_bot_msg_id=msg.message_id)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
