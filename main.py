import logging, asyncio, _config
from FIREBASE import FireBase
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

firebase = FireBase()

# Инициализация бота
API_TOKEN = _config.BOT_TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Логирование
logging.basicConfig(level=logging.INFO)

# Обработчики команд
@dp.message(Command('start'))
async def welcome(message: types.Message):
    """Регистрируем пользователя в FireBase."""
    user_id = str(message.from_user.id)
    user_name = message.from_user.full_name

    response = firebase.init(user_id, user_name)

    if response["status"] == "success":
        await message.answer(f"Привет {user_name}! {response['message']}")
    else:
        await message.answer(f"Ошибка: {response['message']}")


@dp.message(Command('help'))
async def welcome(message: types.Message):
    """Отправляет список доступных команд пользователю."""
    help_text = (
        "🤖 <b>Доступные команды:</b>\n\n"
        "🔹 <b>/start</b> – Начать работу с ботом (зарегистрироваться)\n"
        "🔹 <b>/add_bank</b> – Добавить банковский счет\n"
        "🔹 <b>/show_bank_accounts</b> – Показать все счета и общий баланс\n"
        "🔹 <b>/delete_bank</b> – Удалить банковский счет\n"
        "🔹 <b>/add_debt</b> – Добавить долг\n"
        "🔹 <b>/show_debts</b> – Показать все долги и общую сумму долгов\n"
        "🔹 <b>/delete_debt</b> – Удалить долг\n"
        "🔹 <b>/help</b> – Показать этот список команд\n"
    )

    await message.answer(help_text, parse_mode="HTML")


@dp.message(Command('add_debt'))
async def add_debt(message: types.Message):
    """Добавляет долг пользователю."""
    user_id = str(message.from_user.id)

    await message.answer(
        "📝 *Добавление долга*\n\n"
        "Введите данные в следующем формате:\n"
        "`Название_долга Сумма Дата(DD.MM.YYYY)`\n\n"
        "📌 *Пример:* `Kaspi Кредит 50000 25.04.2025`",
        parse_mode="Markdown"
    )

    @dp.message()
    async def process_debt_input(msg: types.Message):
        try:
            parts = msg.text.rsplit(" ", 2)
            if len(parts) != 3:
                await msg.answer(
                    "❌ *Ошибка:* Неверный формат!\n"
                    "Используйте: `Название_долга Сумма Дата(DD.MM.YYYY)`\n\n"
                    "📌 *Пример:* `Kaspi Кредит 50000 25.04.2025`",
                    parse_mode="Markdown"
                )
                return

            debt_name, amount, due_date = parts[0], parts[1], parts[2]
            response = firebase.add_debt(user_id, debt_name, amount, due_date)

            if response["status"] == "success":
                await msg.answer(
                    f"✅ *Долг успешно добавлен!*\n\n"
                    f"📌 *Название:* `{debt_name}`\n"
                    f"💰 *Сумма:* `{amount} ₸`\n"
                    f"📅 *Дата возврата:* `{due_date}`\n\n"
                    "Просмотреть все долги можно командой /show_debts",
                    parse_mode="Markdown"
                )
            else:
                await msg.answer(f"❌ *Ошибка:* {response['message']}", parse_mode="Markdown")

        except Exception as e:
            await msg.answer(f"❌ *Ошибка обработки:* {str(e)}", parse_mode="Markdown")


@dp.message(Command('show_debts'))
async def show_debts(message: types.Message):
    """Показывает все долги пользователя в красивом формате."""
    user_id = str(message.from_user.id)

    # Получаем ответ от Firebase
    response = firebase.get_debts(user_id)

    # Обрабатываем ответ
    if response["status"] == "success" and response["debts"]:
        debts = response["debts"]
        total_debt = sum(float(debt_info['amount']) for debt_info in debts.values())  # Подсчет общего долга

        # Формируем красивое сообщение с долгами
        debts_message = "📌 *Ваши текущие долги:*\n\n"
        for debt_name, debt_info in debts.items():
            debts_message += (
                f"*{debt_name}*\n"
                f"   💰 *Сумма:* `{debt_info['amount']} ₸`\n"
                f"   📅 *До:* `{debt_info['due_date']}`\n\n"
            )

        debts_message += f"💰 *Общий долг:* `{total_debt} ₸`"

        await message.answer(debts_message, parse_mode="Markdown")
    else:
        await message.answer("✅ У вас нет текущих долгов!", parse_mode="Markdown")


@dp.message(Command('add_bank'))
async def add_bank_account(message: types.Message):
    """Запрашивает данные для добавления банковского счета."""
    user_id = str(message.from_user.id)  # Фиксируем user_id на уровне функции

    await message.answer(
        "🏦 *Добавление банковского счета*\n\n"
        "Введите данные в формате:\n"
        "```\nНазвание_Банка Сумма\n```\n"
        "Пример:\n"
        "```\nKaspi Gold 1000.50\n```",
        parse_mode="Markdown"
    )

    @dp.message(lambda msg: True)
    async def process_bank_input(msg: types.Message):
        nonlocal user_id  # Используем user_id конкретного пользователя
        try:
            parts = msg.text.rsplit(" ", 1)  
            if len(parts) != 2:
                await msg.answer("❌ *Ошибка:* Неверный формат ввода!\n\nПопробуйте так:\n```\nKaspi Gold 1000.50\n```", parse_mode="Markdown")
                return

            name_bank, value = parts[0], parts[1]
            response = firebase.add_bank_account(user_id, name_bank, value)

            if response["status"] == "success":
                await msg.answer(
                    f"✅ *Счет успешно добавлен!*\n\n"
                    f"🏦 *Банк:* `{response['data']['bank']}`\n"
                    f"💰 *Сумма:* `{response['data']['value']} ₸`\n\n"
                    f"📊 Посмотреть все счета: `/show_bank_accounts`",
                    parse_mode="Markdown"
                )
            else:
                await msg.answer(f"❌ *Ошибка:* {response['message']}", parse_mode="Markdown")

        except Exception as e:
            await msg.answer(f"⚠️ *Ошибка обработки:* `{str(e)}`", parse_mode="Markdown")


@dp.message(Command('show_bank_accounts'))
async def show_bank_accounts(message: types.Message):
    """Выводит список банковских счетов пользователя."""
    user_id = str(message.from_user.id)
    response = firebase.get_bank_accounts(user_id)

    if response["status"] == "error":
        await message.answer(f"❌ {response['message']}")
        return

    bank_accounts = response["data"]

    if not bank_accounts:
        await message.answer("ℹ️ У вас пока нет банковских счетов. Добавьте их с помощью /add_bank")
        return

    # Формируем красивый список счетов
    accounts_list = "\n".join([f"🏦 {bank}: {balance}" for bank, balance in bank_accounts.items()])
    response_text = f"📊 **Ваши банковские счета:**\n\n{accounts_list}"
    total_balance = sum(bank_accounts.values()) if bank_accounts else 0
    
    await message.answer(f"{response_text}\n\nОбщий баланс на банковских счетах: {total_balance}", parse_mode="Markdown")


@dp.message(Command("delete_bank"))
async def delete_bank_step_1(message: types.Message):
    """Показывает список банков и предлагает ввести название для удаления."""
    user_id = str(message.from_user.id)
    bank_data = firebase.get_bank_accounts(user_id)  # Метод для получения счетов

    # Проверяем статус ответа и наличие данных
    if bank_data["status"] == "error":
        await message.answer(f"❌ *Ошибка:* {bank_data['message']}", parse_mode="Markdown")
        return

    bank_accounts = bank_data["data"]  # Данные находятся в ключе "data"

    if not bank_accounts:
        await message.answer("❌ *У вас нет добавленных банковских счетов.*", parse_mode="Markdown")
        return

    # Формируем список банков
    bank_list = "\n".join([f"`{bank}`" for bank in bank_accounts.keys()])

    await message.answer(
        "🗑 *Удаление банковского счета*\n\n"
        "Введите *название банка*, который хотите удалить:\n\n"
        f"{bank_list}\n\n"
        "📌 *Совет:* нажмите на нужный банк, чтобы скопировать его название.",
        parse_mode="Markdown"
    )

    @dp.message()
    async def delete_bank_step_2(message: types.Message):
        """Удаляет введенный пользователем банк."""
        user_id = str(message.from_user.id)
        bank_name = message.text.strip()

        response = firebase.delete_bank_account(user_id, bank_name)

        await message.answer(response["message"])


@dp.message(Command("delete_debt"))
async def delete_debt_step_1(message: types.Message):
    """Показывает список долгов и предлагает ввести название для удаления."""
    user_id = str(message.from_user.id)
    debt_data = firebase.get_debts(user_id)

    if debt_data["status"] == "error":
        await message.answer(f"❌ У вас нет добавленных долгов. {debt_data['message']}")
        return

    debts_list = "\n".join([f"`{debt}`" for debt in debt_data["debts"].keys()])

    await message.answer(
        f"Введите название долга, который хотите удалить:\n\n{debts_list}",
        parse_mode="Markdown"
    )

    @dp.message()
    async def delete_debt_step_2(message: types.Message):
        """Удаляет введенный пользователем долг."""
        user_id = str(message.from_user.id)
        debt_name = message.text.strip()

        response = firebase.delete_debt(user_id, debt_name)

        await message.answer(response["message"])


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
