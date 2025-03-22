import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


os.getenv("TELEGRAM_BOT_TOKEN")
MODERATION_CHAT_ID = -1002303863795  # ID чата модерации
PUBLIC_CHANNEL_ID = -1002605169969   # ID канала Lawyers.Club
TELEGRAPH_LINK = "https://telegra.ph/Politika-v-otnoshenii-obrabotki-personalnyh-dannyh-03-14-4"

bot = Bot(token=getenv)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Словарь для хранения данных пользователей
user_data = {}

# Кнопка "Оставить заявку"
start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📝 Оставить заявку", callback_data="leave_request")]
    ]
)

# Приветствие при старте
@dp.message(lambda message: message.text == "/start")
async def start(message: types.Message):
    welcome_text = (
        "Привет✌️ Добро пожаловать в **Lawyers.Club** 🤓\n\n"
        "Этот бот поможет Вам составить заявку на поиск юриста и разместит её на канале **Lawyers.Club**.\n\n"
        "После чего Вашу заявку увидят все подписчики канала 🧑‍💻\n\n"
        "**Для заполнения заявки нажмите на кнопку👇**"
    )
    await message.answer(welcome_text, reply_markup=start_keyboard, parse_mode="Markdown")

# Обработка нажатия "Оставить заявку"
@dp.callback_query(lambda call: call.data == "leave_request")
async def handle_request(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    accept_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я прочитал(а) и принимаю условия", callback_data="accept_terms")]
        ]
    )

    text = (
        "📌 **Ваша заявка на поиск юриста будет размещена в канале Lawyers.Club** с указанием имени пользователя в Telegram.\n\n"
        "Соответственно, для размещения заявки требуется **Ваше согласие** на обработку **Имени пользователя** и **описания профиля** в Telegram, "
        "поскольку эти сведения могут относиться к персональным данным.\n\n"
        "Оставляя заявку, **Вы автоматически подтверждаете наличие такого согласия** и принимаете "
        f"[Политику в отношении обработки персональных данных]({TELEGRAPH_LINK})."
    )
    await call.message.answer(text, reply_markup=accept_keyboard, parse_mode="Markdown")

# После нажатия "✅ Я прочитал(а) и принимаю условия"
@dp.callback_query(lambda call: call.data == "accept_terms")
async def ask_city(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    text = (
        "💻 **В каком городе требуется юрист?**\n\n"
        "🏘 Укажите город, в котором требуется выполнить задачу. Например: **Ташкент** (не использовать сокращения).\n\n"
        "🌍 Если задача может быть выполнена дистанционно, укажите: **Онлайн**."
    )
    await call.message.answer(text, parse_mode="Markdown")
    user_data[call.from_user.id] = {"stage": "waiting_for_city"}

# Обработка ввода города
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("stage") == "waiting_for_city")
async def confirm_city(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["city"] = message.text
    user_data[user_id]["stage"] = "confirming_city"

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_city_input"),
                InlineKeyboardButton(text="✅ Далее", callback_data="confirm_city")
            ]
        ]
    )

    text = (
        "📍 **Проверьте правильность ввода данных (Локация).**\n\n"
        f"**Локация:** {message.text}\n\n"
        "Если всё верно, то нажмите кнопку **'Далее'**."
    )
    await message.answer(text, reply_markup=confirm_keyboard, parse_mode="Markdown")


# Обработка кнопки "Назад" к вводу города
@dp.callback_query(lambda call: call.data == "back_to_city_input")
async def back_to_city_input(call: types.CallbackQuery):
    await ask_city(call)


# Далее -> Ввод отрасли права
@dp.callback_query(lambda call: call.data == "confirm_city")
async def ask_law_field(call: types.CallbackQuery):
    user_data[call.from_user.id]["stage"] = "waiting_for_law_field"

    text = (
        "💼 **В какой отрасли права требуется юрист?**\n\n"
        "Например: **Уголовное право, Семейное право, Жилищное право** и т.д."
    )
    await call.message.edit_text(text, parse_mode="Markdown")

    

# Обработка ввода отрасли права
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("stage") == "waiting_for_law_field")
async def confirm_law_field(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["law_field"] = message.text
    user_data[user_id]["stage"] = "confirming_law_field"

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_law_field_input"),
                InlineKeyboardButton(text="✅ Далее", callback_data="confirm_law_field")
            ]
        ]
    )

    text = (
        "**Проверьте правильность ввода данных (Отрасль права).**\n\n"
        f"**Отрасль права:** {message.text}\n\n"
        "Если всё верно, то нажмите кнопку **'Далее'**."
    )
    await message.answer(text, reply_markup=confirm_keyboard, parse_mode="Markdown")


# Обработка кнопки "Назад" к вводу отрасли права
@dp.callback_query(lambda call: call.data == "back_to_law_field_input")
async def back_to_law_field_input(call: types.CallbackQuery):
    await ask_law_field(call)


# Обработка кнопки "Далее" (описание задачи)
@dp.callback_query(lambda call: call.data == "confirm_law_field")
async def ask_task_description(call: types.CallbackQuery):
    user_id = call.from_user.id
    law_field = user_data.get(user_id, {}).get("law_field", "Неизвестно")
    user_data[user_id]["stage"] = "waiting_for_task_description"

    text = (
        "🏢 **Опишите вкратце задачу**\n\n"
        "Например: **Представление интересов в суде первой инстанции по иску о разделе совместно нажитого имущества.**"
    )
    await call.message.edit_text(text, parse_mode="Markdown")

# Обработка ввода описания задачи
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("stage") == "waiting_for_task_description")
async def confirm_task_description(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["task"] = message.text
    user_data[user_id]["stage"] = "confirming_task_description"

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_task_description_input"),
                InlineKeyboardButton(text="✅ Далее", callback_data="confirm_task_description")
            ]
        ]
    )

    text = (
        "**Проверьте правильность ввода данных (Описание задачи).**\n\n"
        f"**Задача:** {message.text}\n\n"
        "Если всё верно, нажмите **'Далее'**."
    )
    await message.answer(text, reply_markup=confirm_keyboard, parse_mode="Markdown")


# Обработка кнопки "Назад" к вводу описания задачи
@dp.callback_query(lambda call: call.data == "back_to_task_description_input")
async def back_to_task_description_input(call: types.CallbackQuery):
    await ask_task_description(call)


# Обработка кнопки "Далее" после подтверждения описания задачи
@dp.callback_query(lambda call: call.data == "confirm_task_description")
async def ask_price(call: types.CallbackQuery):
    user_data[call.from_user.id]["stage"] = "waiting_for_price"

    text = (
        "🏢 **Укажите стоимость услуг, которую готов заплатить клиент**\n\n"
        "Можно использовать один из следующих вариантов:\n\n"
        "1️⃣ Указать **точную стоимость**. Например: **100 000 рублей**.\n"
        "2️⃣ Указать **диапазон цен**. Например: **От 50 000 до 100 000 рублей**.\n"
        "3️⃣ Указать, что стоимость предлагается исполнителем. В этом случае напишите: **Предлагается юристом**.\n\n"
        "**Лучший вариант** – точная стоимость, так как юристы сразу будут понимать ваш бюджет."
    )
    await call.message.edit_text(text, parse_mode="Markdown")


# Обработка ввода стоимости
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get("stage") == "waiting_for_price")
async def confirm_price(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["price"] = message.text
    user_data[user_id]["stage"] = "confirming_price"

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_price_input"),
                InlineKeyboardButton(text="✅ Далее", callback_data="confirm_price")
            ]
        ]
    )

    text = (
        "**Проверьте правильность ввода данных (Стоимость услуг).**\n\n"
        f"**Стоимость:** {message.text}\n\n"
        "Если всё верно, то нажмите кнопку **'Далее'**."
    )
    await message.answer(text, reply_markup=confirm_keyboard, parse_mode="Markdown")

# Обработка кнопки "Назад" к вводу стоимости услуг
@dp.callback_query(lambda call: call.data == "back_to_price_input")
async def back_to_price_input(call: types.CallbackQuery):
    await ask_price(call)


# Обработка кнопки "Далее" после стоимости услуг
@dp.callback_query(lambda call: call.data == "confirm_price")
async def ask_response_time(call: types.CallbackQuery):
    user_data[call.from_user.id]["stage"] = "waiting_for_response_time"

    response_time_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 час", callback_data="response_1h")],
            [InlineKeyboardButton(text="3 часа", callback_data="response_3h")],
            [InlineKeyboardButton(text="12 часов", callback_data="response_12h")],
            [InlineKeyboardButton(text="24 часа", callback_data="response_24h")],
            [InlineKeyboardButton(text="48 часов", callback_data="response_48h")],
            [InlineKeyboardButton(text="72 часа", callback_data="response_72h")]
        ]
    )

    text = (
        "⌚ **Укажите время, в течение которого юристу необходимо отреагировать на заявку**\n\n"
        "Выберите один из вариантов ниже 👇\n\n"
        "🔹 По истечении этого срока заявка будет автоматически удалена из канала.\n\n"
        "🔹 Если Вы не нашли исполнителя за это время, можете разместить заявку повторно."
    )
    await call.message.edit_text(text, reply_markup=response_time_keyboard, parse_mode="Markdown")

# Обработка выбора времени отклика
@dp.callback_query(lambda call: call.data.startswith("response_"))
async def confirm_response_time(call: types.CallbackQuery):
    user_id = call.from_user.id
    response_time = call.data.replace("response_", "").replace("h", " часов")
    user_data[user_id]["response_time"] = response_time
    user_data[user_id]["stage"] = "confirming_response_time"

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_response_time"),
                InlineKeyboardButton(text="✅ Далее", callback_data="confirm_final")
            ]
        ]
    )

    text = (
        "**Проверьте правильность ввода данных (Время отклика).**\n\n"
        f"**Время отклика:** {response_time}\n\n"
        "Если всё верно, то нажмите кнопку **'Далее'**."
    )
    await call.message.edit_text(text, reply_markup=confirm_keyboard, parse_mode="Markdown")

# Обработка кнопки "Назад" к выбору времени
@dp.callback_query(lambda call: call.data == "back_to_response_time")
async def back_to_response_time(call: types.CallbackQuery):
    await ask_response_time(call)

# Обработка кнопки "Далее" после подтверждения времени отклика
@dp.callback_query(lambda call: call.data == "confirm_final")
async def show_final_request(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data[user_id]["stage"] = "final_confirmation"

    location = user_data[user_id].get("city", "Не указано")
    law_field = user_data[user_id].get("law_field", "Не указано")
    task_description = user_data[user_id].get("task", "Не указано")
    price = user_data[user_id].get("price", "Не указано")
    response_time = user_data[user_id].get("response_time", "Не указано")

    text = (
        "📋 **❗️ Новая заявка ❗️**\n"
        f"\n📍 **Локация:** {location}"
        f"\n⚖ **Отрасль:** {law_field}"
        f"\n📝 **Задача:** {task_description}"
        f"\n💰 **Стоимость:** {price}"
        f"\n⏳ **Предельный срок отклика на заявку:** {response_time}"
    )

    final_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Сбросить", callback_data="reset_form"),
                InlineKeyboardButton(text="📨 Отправить", callback_data="submit_request")
            ]
        ]
    )

    await call.message.edit_text(text, reply_markup=final_keyboard, parse_mode="Markdown")


# Обработка кнопки "Сбросить"
@dp.callback_query(lambda call: call.data == "reset_form")
async def reset_form(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data[user_id] = {}  # Полностью очищаем данные пользователя

    # Удаляем финальное сообщение
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    # Отправляем стартовое сообщение
    await start(call.message)


@dp.callback_query(lambda call: call.data == "submit_request")
async def submit_request(call: types.CallbackQuery):
    user_id = call.from_user.id
    location = user_data[user_id].get("city", "Не указано")
    law_field = user_data[user_id].get("law_field", "Не указано")
    task_description = user_data[user_id].get("task", "Не указано")
    price = user_data[user_id].get("price", "Не указано")
    response_time = user_data[user_id].get("response_time", "Не указано")
    username = f"@{call.from_user.username}" if call.from_user.username else f"[Написать автору заявки](tg://user?id={user_id})"

    request_text = (
        "📋 **❗️ Новая заявка ❗️**\n"
        f"\n📍 **Локация:** {location}"
        f"\n⚖ **Отрасль:** {law_field}"
        f"\n📝 **Задача:** {task_description}"
        f"\n💰 **Стоимость:** {price}"
        f"\n⏳ **Предельный срок отклика на заявку:** {response_time}\n"
        f"\n📲 [Написать автору заявки](tg://user?id={user_id})"
    )

    moderation_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отказать", callback_data=f"reject_{user_id}"),
             InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{user_id}")]
        ]
    )

    message = await bot.send_message(MODERATION_CHAT_ID, request_text, reply_markup=moderation_keyboard, parse_mode="Markdown")
    user_data[user_id]["moderation_message_id"] = message.message_id

    apply_again_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Подать заявку", callback_data="leave_request")]
        ]
    )

    await call.message.edit_text("✅ Заявка отправлена на модерацию!", reply_markup=apply_again_keyboard)



@dp.callback_query(lambda call: call.data.startswith("approve_"))
async def approve_request(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])  # Получаем user_id заявки
    user_info = user_data.get(user_id, {})  # Получаем сохраненные данные

    if not user_info:
        await call.answer("Ошибка: заявка не найдена.", show_alert=True)
        return

    location = user_info.get("city", "Не указано")
    law_field = user_info.get("law_field", "Не указано")
    task_description = user_info.get("task", "Не указано")
    price = user_info.get("price", "Не указано")
    response_time = user_info.get("response_time", "Не указано")
    
    contact_link = f"[Написать автору заявки](tg://user?id={user_id})"  # Используем сохраненный user_id
    
    request_text = (
        "📋 **❗️ Новая заявка ❗️**\n"
        f"\n📍 **Локация:** {location}"
        f"\n⚖ **Отрасль:** {law_field}"
        f"\n📝 **Задача:** {task_description}"
        f"\n💰 **Стоимость:** {price}"
        f"\n⏳ **Предельный срок отклика:** {response_time}\n"
        f"\n📲 {contact_link}"
    )

    await bot.send_message(PUBLIC_CHANNEL_ID, request_text, parse_mode="Markdown")

    await call.answer("✅ Заявка одобрена и опубликована!")

    await bot.delete_message(chat_id=MODERATION_CHAT_ID, message_id=call.message.message_id)

    


@dp.callback_query(lambda call: call.data.startswith("reject_"))
async def reject_request(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])

    retry_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Повторить отправку", callback_data="leave_request")]
        ]
    )

    # Уведомляем пользователя об отказе
    await bot.send_message(
        user_id, 
        "❌ Ваша заявка не прошла модерацию.\n\nВнимательно изучите детали и попробуйте оставить заявку еще раз.", 
        reply_markup=retry_keyboard, 
        parse_mode="Markdown"
    )

    # Уведомляем модератора
    await call.answer("❌ Заявка отклонена и удалена.", show_alert=False)

    # Удаляем заявку из чата модерации
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
