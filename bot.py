import asyncio
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from config import BOT_TOKEN, ADMIN_ID, TASK_REWARD, REFERRAL_REWARD, BOT_USERNAME
from database import (
    init_db,
    create_user,
    get_user,
    add_balance,
    get_balance,
    add_referral,
    captcha_passed,
    set_captcha_passed,
    save_completed_task,
    task_completed,
    create_withdrawal
)
from keyboards import main_menu, referral_menu, withdraw_menu, bonus_menu
from piarflow import get_sponsors, check_sponsors


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def generate_captcha():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    return a, b, a + b


def captcha_keyboard(correct, wrong):
    buttons = [
        InlineKeyboardButton(text=str(correct), callback_data=f"captcha_ok:{correct}"),
        InlineKeyboardButton(text=str(wrong), callback_data="captcha_fail")
    ]
    random.shuffle(buttons)
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    args = message.text.split()
    ref_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    await create_user(user_id, username, ref_id)

    if not await captcha_passed(user_id):
        a, b, res = generate_captcha()
        kb = captcha_keyboard(res, res + 3)
        await message.answer(f"Сколько будет {a} + {b} ?", reply_markup=kb)
        return

    await message.answer("Главное меню", reply_markup=main_menu())


@dp.callback_query(F.data.startswith("captcha_ok"))
async def captcha_ok(call: CallbackQuery):
    await set_captcha_passed(call.from_user.id)
    await call.message.answer("Капча пройдена!")
    await call.message.answer("Главное меню", reply_markup=main_menu())
    await call.answer()


@dp.callback_query(F.data == "menu")
async def menu(call: CallbackQuery):
    await call.message.edit_text("Главное меню", reply_markup=main_menu())
    await call.answer()


@dp.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    user_id = call.from_user.id
    user = await get_user(user_id)
    bal = await get_balance(user_id)

    text = f"ID: {user_id}\nБаланс: {bal:.2f} ⭐\nРефералы: {user[3] if user else 0}"

    await call.message.edit_text(text, reply_markup=main_menu())


@dp.callback_query(F.data == "referrals")
async def referrals(call: CallbackQuery):
    await call.message.edit_text(
        f"Ваша ссылка:\nhttps://t.me/{BOT_USERNAME}?start={call.from_user.id}",
        reply_markup=referral_menu(call.from_user.id)
    )


@dp.callback_query(F.data == "bonus")
async def bonus(call: CallbackQuery):
    await call.message.edit_text("Получите задания", reply_markup=bonus_menu())


@dp.callback_query(F.data == "bonus_get")
async def bonus_get(call: CallbackQuery):
    data = await get_sponsors(call.from_user.id, call.message.chat.id)
    sponsors = data.get("sponsors", [])

    if not sponsors:
        await call.answer("Нет заданий", show_alert=True)
        return

    kb = [
        [InlineKeyboardButton("Подписаться", url=s["link"])]
        for s in sponsors
    ]
    kb.append([InlineKeyboardButton("Проверить", callback_data="bonus_check")])

    await call.message.edit_text(
        "Подпишитесь на каналы",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@dp.callback_query(F.data == "bonus_check")
async def bonus_check(call: CallbackQuery):
    data = await get_sponsors(call.from_user.id, call.message.chat.id)
    links = [s["link"] for s in data.get("sponsors", [])]

    result = await check_sponsors(call.from_user.id, links)

    done = 0

    for s in result.get("sponsors", []):
        if s["status"] == "subscribed":
            if not await task_completed(call.from_user.id, s["link"]):
                await add_balance(call.from_user.id, TASK_REWARD)
                await save_completed_task(call.from_user.id, s["link"])
                done += 1

    await call.message.answer(f"+{done * TASK_REWARD} ⭐")


@dp.callback_query(F.data == "withdraw")
async def withdraw(call: CallbackQuery):
    await call.message.edit_text("Вывод", reply_markup=withdraw_menu())


@dp.callback_query(F.data.startswith("withdraw_"))
async def withdraw_req(call: CallbackQuery):
    amount = float(call.data.split("_")[1])
    bal = await get_balance(call.from_user.id)

    if bal < amount:
        await call.answer("Недостаточно средств", show_alert=True)
        return

    await create_withdrawal(call.from_user.id, amount)

    await bot.send_message(
        ADMIN_ID,
        f"Вывод:\nUser: {call.from_user.id}\nAmount: {amount}"
    )

    await call.message.answer("Заявка отправлена")


@dp.message()
async def fallback(message: Message):
    await message.answer("Используй меню", reply_markup=main_menu())


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

