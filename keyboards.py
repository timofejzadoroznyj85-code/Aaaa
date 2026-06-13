from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("🎁 Бонус", callback_data="bonus")],
        [InlineKeyboardButton("👥 Рефералы", callback_data="referrals")],
        [InlineKeyboardButton("💸 Вывод", callback_data="withdraw")]
    ])


def referral_menu(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Ссылка", url=f"https://t.me/{BOT_USERNAME}?start={user_id}")],
        [InlineKeyboardButton("Назад", callback_data="menu")]
    ])


def withdraw_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("15 ⭐", callback_data="withdraw_15")],
        [InlineKeyboardButton("25 ⭐", callback_data="withdraw_25")],
        [InlineKeyboardButton("50 ⭐", callback_data="withdraw_50")],
        [InlineKeyboardButton("100 ⭐", callback_data="withdraw_100")],
        [InlineKeyboardButton("Назад", callback_data="menu")]
    ])


def bonus_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Получить", callback_data="bonus_get")],
        [InlineKeyboardButton("Назад", callback_data="menu")]
    ])

