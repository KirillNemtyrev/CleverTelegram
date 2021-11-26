from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import random
from random import choice

import requests
import os
import asyncio
import time

from pyowm import OWM
from pyowm.utils.config import get_default_config

from bs4 import BeautifulSoup
from config import TOKEN,API_KEY

import pymorphy2
morph = pymorphy2.MorphAnalyzer()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
owm = OWM(API_KEY)

letters = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "И", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Щ", "Я"]
not_spam_commands = {}

# Check have user admin in group
async def is_admin_group(chat_id, user_id):
    try:
        result = await bot.get_chat_member(chat_id, user_id)
        if "administrator" in result["status"] or "creator" in result["status"]:
            return True
        return False
    except Exception as e:
        print(repr(e))
        
# Check game in chat
def is_game_in_chat(chat_id):
    try:
        if os.path.isfile(os.getcwd() + "/chats/" + str(chat_id) + "/" + "info.txt"):
            return True
        return False
    except Exception as e:
        print(repr(e))

# Check dirs 
def verification_dirs_chat(chat_id):
    try:
        path = os.path.join(os.getcwd() + "/chats", str(chat_id))
        if not os.path.exists(path):
            os.mkdir(path)

        path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "crosses")
        if not os.path.exists(path):
            os.mkdir(path)

        path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "associations")
        if not os.path.exists(path):
            os.mkdir(path)

        path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "hand")
        if not os.path.exists(path):
            os.mkdir(path)

        path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "titles")
        if not os.path.exists(path):
            os.mkdir(path)

        path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "scallop")
        if not os.path.exists(path):
            os.mkdir(path)

    except Exception as e:
        print(repr(e))

# Remove dirs
def remove_dirs_chat(chat_id):
    try:
        path = os.path.join(os.getcwd() + "/chats", str(chat_id))

        if os.path.exists(path):

            path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "crosses")
            if os.path.exists(path):
                files = os.listdir(os.getcwd() + "/chats/" + str(chat_id) + "/crosses")
                if files:
                    for temp in files:
                        os.remove(os.getcwd() + "/chats/" + str(chat_id) + "/crosses/" + temp)
                os.rmdir(os.getcwd() + "/chats/" + str(chat_id) + "/crosses")

            path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "associations")
            if os.path.exists(path):
                files = os.listdir(os.getcwd() + "/chats/" + str(chat_id) + "/associations")
                if files:
                    for temp in files:
                        os.remove(os.getcwd() + "/chats/" + str(chat_id) + "/associations/" + temp)
                os.rmdir(os.getcwd() + "/chats/" + str(chat_id) + "/associations")

            path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "hand")
            if os.path.exists(path):
                files = os.listdir(os.getcwd() + "/chats/" + str(chat_id) + "/hand")
                if files:
                    for temp in files:
                        os.remove(os.getcwd() + "/chats/" + str(chat_id) + "/hand/" + temp)
                os.rmdir(os.getcwd() + "/chats/" + str(chat_id) + "/hand")

            path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "titles")
            if os.path.exists(path):
                files = os.listdir(os.getcwd() + "/chats/" + str(chat_id) + "/titles")
                if files:
                    for temp in files:
                        os.remove(os.getcwd() + "/chats/" + str(chat_id) + "/titles/" + temp)
                os.rmdir(os.getcwd() + "/chats/" + str(chat_id) + "/titles")

            path = os.path.join(os.getcwd() + "/chats/" + str(chat_id), "scallop")
            if os.path.exists(path):
                files = os.listdir(os.getcwd() + "/chats/" + str(chat_id) + "/scallop")
                if files:
                    for temp in files:
                        os.remove(os.getcwd() + "/chats/" + str(chat_id) + "/scallop/" + temp)
                os.rmdir(os.getcwd() + "/chats/" + str(chat_id) + "/scallop")

            files = os.listdir(os.getcwd() + "/chats/" + str(chat_id))
            if files:
                for temp in files:
                    os.remove(os.getcwd() + "/chats/" + str(chat_id) + "/" + temp)

            return os.rmdir(os.getcwd() + "/chats/" + str(chat_id))

    except Exception as e:
        print(repr(e))

# Type: new member
@dp.message_handler(content_types=["new_chat_members"])
async def new_chat_members_delete(message):
    try:
        if await is_admin_group(message.chat.id, message.bot.id):
            await bot.delete_message(message.chat.id, message.message_id)
            
        if message.new_chat_members[0].id == bot.id:
            verification_dirs_chat(message.chat.id)

            buttons  = [types.InlineKeyboardButton(text='Игры 📌', callback_data="Игры"),types.InlineKeyboardButton(text='Помощь ◀', callback_data="Помощь")] 
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            return await message.answer("🍍 Приветствую Вас, господа!\nМеня зовут - *Ананасыч*\nЯ многофункциональный бот\n\nС моей помощью можно:\n💾 Играть в различные игры\n👮 Следить за порядком\n🔔 Администрировать чат\n\n_для полного функционала рекомендую выдать мне права администратора_", parse_mode="Markdown", reply_markup=keyboard)
        
        return await message.answer("🍍[%s](tg://user?id=%d), *добро пожаловать в %s*" % (message.new_chat_members[0].first_name, message.new_chat_members[0].id,message.chat.full_name), parse_mode="Markdown")
    except Exception as e:
        print(repr(e))

# Type: left member
@dp.message_handler(content_types=["left_chat_member"])
async def new_chat_members_delete(message):
    try:
        if message.left_chat_member.id == bot.id:
            return remove_dirs_chat(message.chat.id)

        if await is_admin_group(message.chat.id, message.bot.id):
            await bot.delete_message(message.chat.id, message.message_id)

        await message.answer("🍍 [%s](tg://user?id=%d) покинул(-а) *%s*" % (message.left_chat_member.first_name, message.left_chat_member.id,message.chat.full_name), parse_mode="Markdown")
        
        if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt"):
            with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt") as game:
                record = game.read()
            
            if "ASSOCIATIONS" in record:
                if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt"):
                    os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations/" + str(message.from_user.id) + ".txt")

    except Exception as e:
        print(repr(e))

# Command: start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    try:
        if is_game_in_chat(message.chat.id):
            if await is_admin_group(message.chat.id, bot.id):
                return await bot.delete_message(message.chat.id, message.message_id)
            return message.answer("🍍 *В чате уже идёт игра!*", parse_mode="Markdown")

        if message.chat.id not in not_spam_commands:
            not_spam_commands[message.chat.id] = time.time()
        else:
            if (time.time() - not_spam_commands[message.chat.id]) * 1000 < 2000:
                if await is_admin_group(message.chat.id, bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🍍 *Попрошу не спамить...*", parse_mode="Markdown")
            not_spam_commands[message.chat.id] = time.time()

        buttons  = [types.InlineKeyboardButton(text='Игры 📌', callback_data="Игры"),types.InlineKeyboardButton(text='Помощь ◀', callback_data="Помощь")] 
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)

        return await message.answer("Приветствую - я Ананасыч 🍍\nМногоспособный бот для веселья!", reply_markup=keyboard)
    except Exception as e:
        print(repr(e))

# Admins commands
# Command: mute
@dp.message_handler(commands=['mute'])
async def mute_command(message: types.Message):
    try:
        if message.chat.id not in not_spam_commands:
            not_spam_commands[message.chat.id] = time.time()
        else:
            if (time.time() - not_spam_commands[message.chat.id]) * 1000 < 2000:
                if await is_admin_group(message.chat.id, bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🍍 *Попрошу не спамить...*", parse_mode="Markdown")
            not_spam_commands[message.chat.id] = time.time()

        if message.chat.id == message.from_user.id:
            return await message.answer("🍍 Нужно использовать только в чатах!")

        if not message.reply_to_message:
            return await message.reply("🍍 Команда должна быть использована на ответное сообщение!")

        if not await is_admin_group(message.chat.id, message.bot.id):
            return await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

        if message.reply_to_message.from_user.id == message.bot.id:
            return await message.reply("🍍 Невозможно использовать команду...")

        if not await is_admin_group(message.chat.id, message.from_user.id):
            return await bot.delete_message(message.chat.id, message.message_id)

        if await is_admin_group(message.chat.id, message.reply_to_message.from_user.id):
            return await message.reply("🍍 [%s](tg://user?id=%d) является *Администратором*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")

        await message.answer("🍍 [%s](tg://user?id=%d) *не сможет писать в чат 30 минут*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id,until_date=int(time.time()) + 60*30, permissions={'can_send_messages': False})
    except Exception as e:
        print(repr(e))

# Command: Kick
@dp.message_handler(commands=['kick'])
async def kick_command(message: types.Message):
    try:
        if message.chat.id not in not_spam_commands:
            not_spam_commands[message.chat.id] = time.time()
        else:
            if (time.time() - not_spam_commands[message.chat.id]) * 1000 < 2000:
                if await is_admin_group(message.chat.id, bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🍍 *Попрошу не спамить...*", parse_mode="Markdown")
            not_spam_commands[message.chat.id] = time.time()

        if message.chat.id == message.from_user.id:
            return await message.answer("🍍 Нужно использовать только в чатах!")

        if not message.reply_to_message:
            return await message.reply("🍍 Команда должна быть использована на ответное сообщение!")

        if not await is_admin_group(message.chat.id, message.bot.id):
            return await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

        if message.reply_to_message.from_user.id == message.bot.id:
            return await message.reply("🍍 Невозможно использовать команду...")

        if not await is_admin_group(message.chat.id, message.from_user.id):
            return await bot.delete_message(message.chat.id, message.message_id)

        if await is_admin_group(message.chat.id, message.reply_to_message.from_user.id):
            return await message.reply("🍍 [%s](tg://user?id=%d) является *Администратором*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")

        await bot.delete_message(message.chat.id, message.message_id)
        await message.answer("🍍 [%s](tg://user?id=%d) *кикнул(-а)* [%s](tg://user?id=%d)" % (message.from_user.first_name,message.from_user.id,message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")
        await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    except Exception as e:
        print(repr(e))

# Games
# Command: hand
@dp.message_handler(commands=['hand'])
async def hand_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await bot.send_message(message.from_user.id, "🍍 Эту игру можно запустить только в группе)")

        if message.chat.id not in not_spam_commands:
            not_spam_commands[message.chat.id] = time.time()
        else:
            if (time.time() - not_spam_commands[message.chat.id]) * 1000 < 2000:
                if await is_admin_group(message.chat.id, bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🍍 *Попрошу не спамить...*", parse_mode="Markdown")
            not_spam_commands[message.chat.id] = time.time()

        if is_game_in_chat(message.chat.id):
            if await is_admin_group(message.chat.id, bot.id):
                return await bot.delete_message(message.chat.id, message.message_id)
            return message.answer("🍍 *В чате уже идёт игра!*", parse_mode="Markdown")

        verification_dirs_chat(message.chat.id)

        buttons  = [types.InlineKeyboardButton(text='Принять 👍', callback_data="Рука")] 
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        get_info = await message.reply("🍍 [%s](tg://user?id=%d) кидает вызов в камень-ножницы-бумага" % (message.from_user.first_name,message.from_user.id), parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        print(repr(e)) 

# Command: crosses
@dp.message_handler(commands=['crosses'])
async def crosses_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await bot.send_message(message.from_user.id, "🍍 Эту игру можно запустить только в группе)")

        if message.chat.id not in not_spam_commands:
            not_spam_commands[message.chat.id] = time.time()
        else:
            if (time.time() - not_spam_commands[message.chat.id]) * 1000 < 2000:
                if await is_admin_group(message.chat.id, bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🍍 *Попрошу не спамить...*", parse_mode="Markdown")
            not_spam_commands[message.chat.id] = time.time()

        if is_game_in_chat(message.chat.id):
            if await is_admin_group(message.chat.id, bot.id):
                return await bot.delete_message(message.chat.id, message.message_id)
            return message.answer("🍍 *В чате уже идёт игра!*", parse_mode="Markdown")

        verification_dirs_chat(message.chat.id)

        buttons  = [types.InlineKeyboardButton(text='Присоединиться ⚔', callback_data="Крестики-нолики")] 
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        get_info = await message.reply("🍍 [%s](tg://user?id=%d) хочет поиграть в крестики-нолики" % (message.from_user.first_name,message.from_user.id), parse_mode="Markdown", reply_markup=keyboard)        
    except Exception as e:
        print(repr(e))

# Help function crosses
def progress_to_win_crosses(check_pos):
    if check_pos[0] != 0 and check_pos[0] == check_pos[1] and check_pos[1] == check_pos[2]:
        return check_pos[0]
    elif check_pos[3] != 0 and check_pos[3] == check_pos[4] and check_pos[4] == check_pos[5]:
        return check_pos[3]
    elif check_pos[6] != 0 and check_pos[6] == check_pos[7] and check_pos[7] == check_pos[8]:
        return check_pos[6]
    elif check_pos[0] != 0 and check_pos[0] == check_pos[3] and check_pos[3] == check_pos[6]:
        return check_pos[0]
    elif check_pos[1] != 0 and check_pos[1] == check_pos[4] and check_pos[4] == check_pos[7]:
        return check_pos[1]
    elif check_pos[2] != 0 and check_pos[2] == check_pos[5] and check_pos[5] == check_pos[8]:
        return check_pos[2]
    elif check_pos[0] != 0 and check_pos[0] == check_pos[4] and check_pos[4] == check_pos[8]:
        return check_pos[0]
    elif check_pos[2] != 0 and check_pos[2] == check_pos[4] and check_pos[4] == check_pos[6]:
        return check_pos[2]
    elif check_pos[0] != 0 and check_pos[1] != 0 and check_pos[2] != 0 and check_pos[3] != 0 and check_pos[4] != 0 and check_pos[5] != 0 and check_pos[6] != 0 and check_pos[7] != 0 and check_pos[8] != 0:
        return 4
    return False

# Command: titles
@dp.message_handler(commands=['titles'])
async def crosses_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await bot.send_message(message.from_user.id, "🍍 Эту игру можно запустить только в группе)")

        if message.chat.id not in not_spam_commands:
            not_spam_commands[message.chat.id] = time.time()
        else:
            if (time.time() - not_spam_commands[message.chat.id]) * 1000 < 2000:
                if await is_admin_group(message.chat.id, bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🍍 *Попрошу не спамить...*", parse_mode="Markdown")
            not_spam_commands[message.chat.id] = time.time()

        if is_game_in_chat(message.chat.id):
            if await is_admin_group(message.chat.id, bot.id):
                return await bot.delete_message(message.chat.id, message.message_id)
            return message.answer("🍍 *В чате уже идёт игра!*", parse_mode="Markdown")

        if not await is_admin_group(message.chat.id, bot.id):
            return await message.reply("🍍 Для запуска данной игры мне нужны права Администратора.")

        verification_dirs_chat(message.chat.id)
        first_letter = choice(letters)

        with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt", "+w") as game:
            game.write("TITLES|%s|0|0" % first_letter)
            open(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles.txt", "+w")

        await bot.delete_message(message.chat.id, message.message_id)

        get_info = await message.answer("🍍 *Названия местностей*\n\n📌 Бот пишет букву на которую нужно написать название местности\nСледующий ход будет на последнию букву названия\nНазвания стран,городов,штатов и др.\nСоответственно игрок пропустит следующий ход\n\nИ так начнём, буква: *%s*" % first_letter, parse_mode="Markdown")        
        
        await asyncio.sleep(60)
        if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt"):
            with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt") as game:
                record = game.read().split("|")

            if record[2] == "0":
                os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt")
                os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles.txt")
                return await bot.delete_message(message.chat.id, get_info.message_id)

    except Exception as e:
        print(repr(e))

# Command: associations
@dp.message_handler(commands=['associations'])
async def associations_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await bot.send_message(message.from_user.id, "🍍 Эту игру можно запустить только в группе)")

        if not await is_admin_group(message.chat.id, bot.id):
            return await message.reply("🍍 Для запуска данной игры мне нужны права Администратора.")

        if message.chat.id not in not_spam_commands:
            not_spam_commands[message.chat.id] = time.time()
        else:
            if (time.time() - not_spam_commands[message.chat.id]) * 1000 < 2000:
                if await is_admin_group(message.chat.id, bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🍍 *Попрошу не спамить...*", parse_mode="Markdown")
            not_spam_commands[message.chat.id] = time.time()

        if is_game_in_chat(message.chat.id):
            if await is_admin_group(message.chat.id, bot.id):
                return await bot.delete_message(message.chat.id, message.message_id)
            return message.answer("🍍 *В чате уже идёт игра!*", parse_mode="Markdown")

        verification_dirs_chat(message.chat.id)

        with open(os.getcwd() + "/info/words_for_associations.txt", encoding="utf8") as game:
            words = game.read().split(",")

        POS_WORD = random.randint(0, len(words) - 1)
        step_first_message = await bot.send_message(message.chat.id, "🍍 Ассоциации\n\n[%s](tg://user?id=%d) запустил игру!\n\n✏ Пишите ассоциации к слову в течении 120 секунд\n⚡ Зарабатывайте очки и выигрывайте\n\nСлово для ассоциаций: *%s*" % (message.from_user.first_name,message.from_user.id,words[POS_WORD]), parse_mode="Markdown")

        parse_words(message.chat.id, words[POS_WORD])

        with open("chats/" + str(message.chat.id) + "/info.txt", "+w") as game:
            game.write("ASSOCIATIONS")

        await asyncio.sleep(60)
        step_second_message = await bot.send_message(message.chat.id, "🍍 *Ассоциации*\n\nНапоминаю слово: *%s*\n⌛Осталось: 60 секунд..." % words[POS_WORD], parse_mode="Markdown")

        await asyncio.sleep(30)
        step_third_message = await bot.send_message(message.chat.id, "🍍 *Ассоциации*\n\nНапоминаю слово: *%s*\n⌛Осталось: 30 секунд..." % words[POS_WORD], parse_mode="Markdown")

        await asyncio.sleep(30)
        dirs = os.listdir(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations")

        os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt")
        os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/parse.txt")

        if not dirs:
            if await is_admin_group(message.chat.id, bot.id):
                # Remove messages
                await bot.delete_message(message.chat.id, message.message_id)
                await bot.delete_message(message.chat.id, step_first_message.message_id)
                await bot.delete_message(message.chat.id, step_second_message.message_id)
                return await bot.delete_message(message.chat.id, step_third_message.message_id)

            return await bot.send_message(message.chat.id, "🍍 *Ассоциации*\nИгра завершена!", parse_mode="Markdown")

        game_message = "🍍 *Ассоциации*\nИгра завершена!\n\nУчастники:\n"
        win_message = ""
        count = 1
        max = 0

        for item in dirs:
            if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations/" + item):
                with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations/" + item) as player:
                    score = int(player.read())
                    
                info = await bot.get_chat_member(message.chat.id, int(item.replace(".txt", "")))
                os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations/" + item)
                game_message += "[%s](tg://user?id=%d) - ⚡ %d очков.\n" % (info.user.first_name, int(item.replace(".txt", "")), score)

                if score > max:
                    max = score
                    win_message = "\nПобедитель:\n[%s](tg://user?id=%d) - ⚡ %d очков" % (info.user.first_name, int(item.replace(".txt", "")), score)

        return await bot.send_message(message.chat.id, game_message + win_message, parse_mode="Markdown")   

    except Exception as e:
        print(repr(e))  

def parse_words(chat_id, word):
    try:
        url = 'http://sinonim.org/as/%s' % word
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'})
        soup = BeautifulSoup(response.text, 'lxml')
        sections = soup.find_all('ul', class_="assocPodryad")
        cases = soup.find_all('li')

        with open("chats/" + str(chat_id) + "/parse.txt", "+w") as parse:
            for item in cases:
                if "." not in item.get_text():
                    parse.write(item.get_text() + ",")

    except Exception as e:
        print(repr(e))

# Command: associations
@dp.message_handler(commands=['scallop'])
async def scallop_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await bot.send_message(message.from_user.id, "🍍 Эту игру можно запустить только в группе)")

        if not await is_admin_group(message.chat.id, bot.id):
            return await message.reply("🍍 Для запуска данной игры мне нужны права Администратора.")

        if message.chat.id not in not_spam_commands:
            not_spam_commands[message.chat.id] = time.time()
        else:
            if (time.time() - not_spam_commands[message.chat.id]) * 1000 < 2000:
                if await is_admin_group(message.chat.id, bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🍍 *Попрошу не спамить...*", parse_mode="Markdown")
            not_spam_commands[message.chat.id] = time.time()

        if is_game_in_chat(message.chat.id):
            if await is_admin_group(message.chat.id, bot.id):
                return await bot.delete_message(message.chat.id, message.message_id)
            return message.answer("🍍 *В чате уже идёт игра!*", parse_mode="Markdown")

        verification_dirs_chat(message.chat.id)

        scallop_letters = ["Б", "В", "Г", "Д", "К", "Л", "М", "Н", "П", "Р", "С", "Т"]
        first_lett = choice(scallop_letters)
        scallop_letters.remove(first_lett)

        second_lett = choice(scallop_letters)
        scallop_letters.remove(second_lett)

        third_lett = choice(scallop_letters)
        scallop_letters.remove(third_lett)

        step_first_message = await bot.send_message(message.chat.id, "🍍 *Гребешок*\n\n[%s](tg://user?id=%d) запустил игру!\n\n*Суть игры:*\n✏ Составляйте слова из предложенных букв\n✏ Слова должны быть существительными\n✏ Предоставленные буквы обязательно должны находиться в слове\n\nБуквы: *%s %s %s*" % (message.from_user.first_name,message.from_user.id,first_lett,second_lett,third_lett), parse_mode="Markdown")

        with open("chats/" + str(message.chat.id) + "/info.txt", "+w") as game:
            game.write("SCALLOP|%s|%s|%s" % (first_lett,second_lett,third_lett))

        open("chats/" + str(message.chat.id) + "/words.txt", "+w")

        await asyncio.sleep(60)
        step_second_message = await bot.send_message(message.chat.id, "🍍 *Гребешок*\n\nБуквы для слов: *%s %s %s*\n⌛ Осталось: 60 секунд..." % (first_lett,second_lett,third_lett), parse_mode="Markdown")

        await asyncio.sleep(30)
        step_third_message = await bot.send_message(message.chat.id, "🍍 *Гребешок*\n\nБуквы для слов: *%s %s %s*\n⌛ Осталось: 30 секунд..." % (first_lett,second_lett,third_lett), parse_mode="Markdown")

        await asyncio.sleep(30)
        dirs = os.listdir(os.getcwd() + "/chats/" + str(message.chat.id) + "/scallop")

        os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt")
        os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/words.txt")

        if not dirs:
            if await is_admin_group(message.chat.id, bot.id):
                # Remove messages
                await bot.delete_message(message.chat.id, message.message_id)
                await bot.delete_message(message.chat.id, step_first_message.message_id)
                await bot.delete_message(message.chat.id, step_second_message.message_id)
                return await bot.delete_message(message.chat.id, step_third_message.message_id)

            return await bot.send_message(message.chat.id, "🍍 *Гребешок*\nИгра завершена!", parse_mode="Markdown")

        game_message = "🍍 *Гребешок*\nИгра завершена!\n\nУчастники:\n"
        win_message = ""
        max = 0

        for item in dirs:
            if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/scallop/" + item):
                with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/scallop/" + item) as player:
                    score = int(player.read())
                    
                info = await bot.get_chat_member(message.chat.id, int(item.replace(".txt", "")))
                os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/scallop/" + item)
                game_message += "[%s](tg://user?id=%d) - ⚡ %d очков.\n" % (info.user.first_name, int(item.replace(".txt", "")), score)

                if score > max:
                    max = score
                    win_message = "\nПобедитель:\n[%s](tg://user?id=%d) - ⚡ %d очков" % (info.user.first_name, int(item.replace(".txt", "")), score)

        return await bot.send_message(message.chat.id, game_message + win_message, parse_mode="Markdown")   

    except Exception as e:
        print(repr(e))  

# Types: text
@dp.message_handler(content_types=["text"])
async def check_all_messages(message):
    try:
        if is_game_in_chat(message.chat.id):
            with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt") as game:
                game_text = game.read()

            if "SCALLOP" in game_text:
                try:
                    with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt") as game:
                        records = game.read().split("|")

                    if records[1] in message.text.upper() and records[2] in message.text.upper() and records[3] in message.text.upper():
                        if morph.word_is_known(message.text):
                            word = morph.parse(message.text)[0]
                            if word.tag.POS != "NOUN":
                                return True

                            with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/words.txt") as parse:
                                text = parse.read()

                            text_split = text.split(",")
                            for item in text_split:
                                if message.text.lower() in item.lower():
                                    return await message.reply("🍍 *Гребешок*\n\nСлово уже было!", parse_mode="Markdown")

                            with open("chats/" + str(message.chat.id) + "/words.txt", "+w") as parse:
                                parse.write(message.text + ",")

                            await message.reply("🍍 *Гребешок*\n\nСлово *%s* засчитано\n⚡ *+%d очков*" % (message.text, len(message.text) / 2), parse_mode="Markdown")  
                            if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/scallop/" + str(message.from_user.id) + ".txt"):
                                with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/scallop/" + str(message.from_user.id) + ".txt") as player:
                                    score = int(player.read())

                                with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/scallop/" + str(message.from_user.id) + ".txt" , "+w") as player:
                                    player.write(str(score + int(len(message.text) / 2)))
                            else:
                                with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/scallop/" + str(message.from_user.id) + ".txt" , "+w") as player:
                                    player.write(str(int(len(message.text) / 2)))

                except Exception as e:
                    print(repr(e)) 

            if "TITLES" in game_text:
                try:
                    with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt") as game:
                        records = game.read().split("|")

                    city = message.text.upper() 
                    first_letter = city[:1]
                    last_letter = city.replace(city[:-1], "")

                    if int(records[2]) == message.from_user.id or first_letter != records[1]:
                        return True

                    with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles.txt") as file:
                        cities = file.read()

                    result = cities.split(",")
                    for temp in result:
                        if temp.lower() == message.text.lower():
                            return await message.reply("🍍 *Местность*\n\nЭта местность уже была!", parse_mode="Markdown")

                    mgr = owm.weather_manager()
                    mgr.weather_at_place(message.text)

                    for i in range(len(city)):
                        if last_letter in letters:
                            break

                        else:
                            if len(last_letter) != 1:
                                last_letter = last_letter[:1]
                            else:
                                last_letter = city.replace(city[:len(city) - 2 - i], "").replace(last_letter, "")

                    with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles.txt", "+w") as file:
                        file.write(cities + message.text + ",")

                    with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt", "+w") as game:
                        game.write("TITLES|%s|%d|%d" % (last_letter, message.from_user.id, int(records[3]) + 1))

                    await message.reply("🍍 *Местность - %s*\n\n📌 Буква - *%s*\n⌛ Ход: *60 секунд*" % (message.text, last_letter), parse_mode="Markdown")
                    
                    if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles/" + str(message.from_user.id) + ".txt"):
                        with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles/" + str(message.from_user.id) + ".txt") as player:
                            score = int(player.read())

                        with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles/" + str(message.from_user.id) + ".txt" , "+w") as player:
                            player.write(str(score + 1))
                    else:
                        with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles/" + str(message.from_user.id) + ".txt" , "+w") as player:
                            player.write(str(1))

                    await asyncio.sleep(60)
                    if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt"):

                        with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt") as game:
                            record = game.read().split("|")

                        if int(record[2]) == message.from_user.id and int(record[3]) == int(records[3]) + 1:
                            os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/info.txt")
                            os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles.txt")

                            players = os.listdir(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles")
                            try:
                                max = 0
                                for temp in players:
                                    with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles/" + temp) as player:
                                        score = int(player.read())
                                        
                                    os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles/" + temp)

                                    if score > max:
                                        max = score
                                        index = int(temp.replace(".txt", ""))
                                        info = await bot.get_chat_member(message.chat.id, int(temp.replace(".txt", "")))

                                await message.answer("🍍 *Местность*\nИгра закончена!\n\nПобедитель:\n👑 [%s](tg://user?id=%d) - назвал(-а) больше всех местностей" % (info.user.first_name, index), parse_mode="Markdown")
                            except Exception as e:
                                await message.answer("🍍 *Местность*\nИгра закончена!", parse_mode="Markdown")
                                for temp in players: 
                                    os.remove(os.getcwd() + "/chats/" + str(message.chat.id) + "/titles/" + temp)
                except Exception as e:
                    pass

            if "ASSOCIATIONS" in game_text:

                with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/parse.txt") as parse:
                    text = parse.read()

                text_split = text.split(",")
                for item in text_split:
                    if message.text.lower() == item:
                        with open("chats/" + str(message.chat.id) + "/parse.txt", "+w") as parse:
                            parse.write(text.replace(message.text.lower() + ",", ""))

                        await message.reply("🍍 *Ассоциации*\n\nСлово *%s* засчитано\n⚡ *+%d очков*" % (message.text, len(message.text) / 2), parse_mode="Markdown")  
                        if os.path.isfile(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations/" + str(message.from_user.id) + ".txt"):
                            with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations/" + str(message.from_user.id) + ".txt") as player:
                                score = int(player.read())

                            with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations/" + str(message.from_user.id) + ".txt" , "+w") as player:
                                player.write(str(score + int(len(message.text) / 2)))
                        else:
                            with open(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations/" + str(message.from_user.id) + ".txt" , "+w") as player:
                                player.write(str(int(len(message.text) / 2)))

        morse = [
            {"letter": "а", "morse": "•– "},
            {"letter": "б", "morse": "–••• "},
            {"letter": "в", "morse": "•–– "},
            {"letter": "г", "morse": "––• "},
            {"letter": "д", "morse": "–•• "},
            {"letter": "е", "morse": "• "},
            {"letter": "ж", "morse": "•••– "},
            {"letter": "з", "morse": "––•• "},
            {"letter": "и", "morse": "•• "},
            {"letter": "й", "morse": "•––– "},
            {"letter": "к", "morse": "–•– "},
            {"letter": "л", "morse": "•–•• "},
            {"letter": "м", "morse": "–– "},
            {"letter": "н", "morse": "–• "},
            {"letter": "о", "morse": "––– "},
            {"letter": "п", "morse": "•––• "},
            {"letter": "р", "morse": "•–• "},
            {"letter": "с", "morse": "••• "},
            {"letter": "т", "morse": "– "},
            {"letter": "у", "morse": "••– "},
            {"letter": "ф", "morse": "••–• "},
            {"letter": "х", "morse": "•••• "},
            {"letter": "ц", "morse": "–•–• "},
            {"letter": "ч", "morse": "–––• "},
            {"letter": "ш", "morse": "–––– "},
            {"letter": "щ", "morse": "––•– "},
            {"letter": "ъ", "morse": "•––•–• "},
            {"letter": "ы", "morse": "–•–– "},
            {"letter": "ь", "morse": "–••– "},
            {"letter": "э", "morse": "••–•• "},
            {"letter": "ю", "morse": "••–– "},
            {"letter": "я", "morse": "•–•– "},
        ]
        string = message.text.lower()
        string = string.replace("ё", "е")
        for temp in morse:
            string = string.replace(temp["letter"], temp["morse"])
        if message.from_user.id == message.chat.id:
             await message.answer(string)

    except Exception as e:
        print(repr(e))  

# Types: callback keyboard
@dp.callback_query_handler(lambda callback_query: True)
async def some_callback_handler(callback_query: types.CallbackQuery):
    try:
        code = callback_query.data
        if code == "Игры":

            message = "🍍 *Игры:*\n/associations - Игра в ассоциации\n/crosses - Игра крестики-нолики\n/hand - Камень-Ножницы-Бумага\n/scallop - Игра гребешок\n/titles - Названия местностей"
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=None)
        
        elif code == "Помощь":

            message = "🍍 *Помощь*\n\nАдминистративные команды:\n/mute - Заглушить на 30 мин\n/kick - Кикнуть игрока"
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=None)

        elif code == "Рука":

            if not callback_query.message.reply_to_message:
                return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="🍍 Невозможно начать игру..", parse_mode="Markdown",reply_markup=None)

            if callback_query.from_user.id == callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Это ваш вызов...", show_alert=True)

            with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/hand/" + str(callback_query.message.message_id) + ".txt", "w+") as game:
                game.write("%d|%s|%d|%s|None|None" % (callback_query.from_user.id, callback_query.from_user.first_name, callback_query.message.reply_to_message.from_user.id, callback_query.message.reply_to_message.from_user.first_name))

            buttons = [types.InlineKeyboardButton(text="Камень", callback_data="Камень"),types.InlineKeyboardButton(text="Ножницы", callback_data="Ножницы"),types.InlineKeyboardButton(text="Бумага", callback_data="Бумага")]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            game_message = "🍍 *Вызов принят..*\n\nУчастники:\n1️⃣ [%s](tg://user?id=%d)\n2️⃣ [%s](tg://user?id=%d)\n\n⌛ Ход: *60 секунд*" % (callback_query.from_user.first_name, callback_query.from_user.id, callback_query.message.reply_to_message.from_user.first_name, callback_query.message.reply_to_message.from_user.id)
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=game_message, parse_mode="Markdown",reply_markup=keyboard)
            
            await asyncio.sleep(20)

            if os.path.isfile(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/hand/" + str(callback_query.message.message_id) + ".txt"):

                with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/hand/" + str(callback_query.message.message_id) + ".txt") as game:
                    result = game.read().split("|")

                os.remove(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/hand/" + str(callback_query.message.message_id) + ".txt")

                if result[4] == "None" and result[5] == "None":
                    game_message = "🍍 *Игра окончена!*\n\nУчастники:\n1️⃣ [%s](tg://user?id=%d)\n2️⃣ [%s](tg://user?id=%d)\n\nНикто не сделал ход.." % (result[1], int(result[0]), result[3], int(result[2]))
                elif result[4] == "None":
                    game_message = "🍍 *Игра окончена!*\n\nУчастники:\n1️⃣ [%s](tg://user?id=%d) - Не сделал ход\n2️⃣ [%s](tg://user?id=%d)" % (result[1], int(result[0]), result[3], int(result[2]))
                elif result[5] == "None":
                    game_message = "🍍 *Игра окончена!*\n\nУчастники:\n1️⃣ [%s](tg://user?id=%d)\n2️⃣ [%s](tg://user?id=%d) - Не сделал ход" % (result[1], int(result[0]), result[3], int(result[2]))    
                
                await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=game_message, parse_mode="Markdown",reply_markup=None)

        elif code == "Камень" or code == "Ножницы" or code =="Бумага":

            if not os.path.isfile(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/hand/" + str(callback_query.message.message_id) + ".txt"):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Произошла ошибка!", show_alert=True)

            with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/hand/" + str(callback_query.message.message_id) + ".txt") as game:
                result = game.read().split("|")

            if int(result[0]) != callback_query.from_user.id and int(result[2]) != callback_query.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Вы не можете ходить", show_alert=True)

            buttons = [types.InlineKeyboardButton(text="Камень", callback_data="Камень"),types.InlineKeyboardButton(text="Ножницы", callback_data="Ножницы"),types.InlineKeyboardButton(text="Бумага", callback_data="Бумага")]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            if int(result[0]) == callback_query.from_user.id and result[4] == "None":
                result[4] = code
            elif int(result[2]) == callback_query.from_user.id and result[5] == "None":
                result[5] = code

            with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/hand/" + str(callback_query.message.message_id) + ".txt", "w+") as game:
                game.write("%s|%s|%s|%s|%s|%s" % (result[0], result[1], result[2], result[3], result[4], result[5]))
            
            game_message = "🍍 *Вызов принят..*\n\nУчастники:\n1️⃣ [%s](tg://user?id=%d)\n2️⃣ [%s](tg://user?id=%d)\n\n⌛ Ход: *60 секунд*\n▶ [%s](tg://user?id=%d) - сделал(-а) ход" % (result[1], int(result[0]), result[3], int(result[2]), callback_query.from_user.first_name, callback_query.from_user.id)
            if result[4] != "None" and result[5] != "None":
                os.remove(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/hand/" + str(callback_query.message.message_id) + ".txt")
                keyboard = None
                if result[4] == result[5]:
                    game_message = "🍍 *Ничья*\n\nУчастники:\n1️⃣ [%s](tg://user?id=%d) - %s\n2️⃣ [%s](tg://user?id=%d) - %s" % (result[1], int(result[0]), result[4], result[3], int(result[2]), result[5])
                elif result[4] == "Камень" and result[5] == "Ножницы" or result[4] == "Бумага" and result[5] == "Камень" or result[4] == "Ножницы" and result[5] == "Бумага":
                    game_message = "🍍 *Игра окончена!*\n\nУчастники:\n1️⃣ [%s](tg://user?id=%d) - %s\n2️⃣ [%s](tg://user?id=%d) - %s\n\n*Победитель:*\n[%s](tg://user?id=%d) - 👑" % (result[1], int(result[0]), result[4], result[3], int(result[2]), result[5], result[1], int(result[0]))
                elif result[5] == "Камень" and result[4] == "Ножницы" or result[5] == "Бумага" and result[4] == "Камень" or result[5] == "Ножницы" and result[4] == "Бумага":
                    game_message = "🍍 *Игра окончена!*\n\nУчастники:\n1️⃣ [%s](tg://user?id=%d) - %s\n2️⃣ [%s](tg://user?id=%d) - %s\n\n*Победитель:*\n[%s](tg://user?id=%d) - 👑" % (result[1], int(result[0]), result[4], result[3], int(result[2]), result[5], result[3], int(result[2]))

            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=game_message, parse_mode="Markdown",reply_markup=keyboard)

        elif code == "Крестики-нолики":
            if not callback_query.message.reply_to_message:
                return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="🍍 Невозможно начать игру..", parse_mode="Markdown",reply_markup=None)

            if callback_query.from_user.id == callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Вы являетесь участником этой игры...", show_alert=True)

            buttons = [types.InlineKeyboardButton(text="⏺", callback_data="1"),types.InlineKeyboardButton(text="⏺", callback_data="2"),types.InlineKeyboardButton(text="⏺", callback_data="3"),
            types.InlineKeyboardButton(text="⏺", callback_data="4"),types.InlineKeyboardButton(text="⏺", callback_data="5"),types.InlineKeyboardButton(text="⏺", callback_data="6"),
            types.InlineKeyboardButton(text="⏺", callback_data="7"),types.InlineKeyboardButton(text="⏺", callback_data="8"),types.InlineKeyboardButton(text="⏺", callback_data="9")]
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            keyboard.add(*buttons)

            CHOSEE = random.randint(0, 100)
            crosses_player_index = callback_query.from_user.id
            crosses_player_name = callback_query.from_user.first_name
            zero_player_index = callback_query.message.reply_to_message.from_user.id
            zero_player_name = callback_query.message.reply_to_message.from_user.first_name
            if CHOSEE >= 50:
                crosses_player_index = callback_query.message.reply_to_message.from_user.id
                crosses_player_name = callback_query.message.reply_to_message.from_user.first_name
                zero_player_index = callback_query.from_user.id
                zero_player_name = callback_query.from_user.first_name

            message = "🍍 Игра началась!\n⌛ На ход: *20 секунд*\n\n❌ [%s](tg://user?id=%d) ходит крестиками\n⭕ [%s](tg://user?id=%d) ходит ноликами\n\nПервым ходит: [%s](tg://user?id=%d) ❌" % (crosses_player_name, crosses_player_index, zero_player_name, zero_player_index, crosses_player_name, crosses_player_index)
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=keyboard)
            
            with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt", "w+") as game:
                game.write("%d|%s|%d|%s|CROSS|1|0|0|0|0|0|0|0|0|0" % (crosses_player_index, crosses_player_name, zero_player_index, zero_player_name))

            await asyncio.sleep(20)
            if os.path.isfile(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt"):
                with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt") as game:
                    game_split = game.read().split("|")

                if int(game_split[5]) == 1:
                    message = "🍍 *Игра закончилась!*\n\nУчастники:\n❌ [%s](tg://user?id=%d) - Не сделал(-а) ход\n⭕ [%s](tg://user?id=%d)" % (crosses_player_name, crosses_player_index, zero_player_name, zero_player_index)
                    return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=None)

        elif code == "1" or code == "2" or code == "3" or code == "4" or code == "5" or code == "6" or code == "7" or code == "8" or code == "9":
            if os.path.isfile(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt"):                 
                with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt") as game:
                    game_info = game.read().split("|")

                if (callback_query.from_user.id == int(game_info[0]) and game_info[4] == "CROSS") or (callback_query.from_user.id == int(game_info[2]) and game_info[4] == "ZERO"):
                    # Variables
                    position = int(code) - 1
                    keyboard_text = ["⏺","⏺","⏺","⏺","⏺","⏺","⏺","⏺","⏺"]
                    callback_post = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                    crosses_position = []
                    game_message = ""
                    write_to_txt = ""

                    for i in range(9):
                        crosses_position.append(int(game_info[i+6]))

                    if callback_query.from_user.id == int(game_info[0]) and game_info[4] == "CROSS":
                        game_message = "🍍 Игра началась!\n⌛ На ход: *20 секунд*\n\n❌ [%s](tg://user?id=%s) ходит крестиками\n⭕ [%s](tg://user?id=%s) ходит ноликами\n\nСейчас ходит: [%s](tg://user?id=%s) ⭕" % (game_info[1], game_info[0], game_info[3], game_info[2], game_info[3], game_info[2])
                        crosses_position[position] = 2
                        write_to_txt = "%s|%s|%s|%s|ZERO|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d" % (game_info[0], game_info[1], game_info[2], game_info[3], int(game_info[5]) + 1, crosses_position[0],crosses_position[1],crosses_position[2],crosses_position[3],crosses_position[4],crosses_position[5],crosses_position[6],crosses_position[7],crosses_position[8])
                    else:
                        game_message = "🍍 Игра началась!\n⌛ На ход: *20 секунд*\n\n❌ [%s](tg://user?id=%s) ходит крестиками\n⭕ [%s](tg://user?id=%s) ходит ноликами\n\nСейчас ходит: [%s](tg://user?id=%s) ❌" % (game_info[1], game_info[0], game_info[3], game_info[2], game_info[1], game_info[0])
                        crosses_position[position] = 3
                        write_to_txt = "%s|%s|%s|%s|CROSS|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d" % (game_info[0], game_info[1], game_info[2], game_info[3], int(game_info[5]) + 1, crosses_position[0],crosses_position[1],crosses_position[2],crosses_position[3],crosses_position[4],crosses_position[5],crosses_position[6],crosses_position[7],crosses_position[8])
                    
                    with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt", "w+") as game:
                        game.write(write_to_txt)

                    for i in range(9):
                        if crosses_position[i] == 2:
                            keyboard_text[i] = "❌"
                            callback_post[i] = "Выбрано"
                        elif crosses_position[i] == 3:
                            keyboard_text[i] = "⭕"
                            callback_post[i] = "Выбрано" 

                    buttons = [types.InlineKeyboardButton(text=keyboard_text[0], callback_data=callback_post[0]),types.InlineKeyboardButton(text=keyboard_text[1], callback_data=callback_post[1]),types.InlineKeyboardButton(text=keyboard_text[2], callback_data=callback_post[2]),
                    types.InlineKeyboardButton(text=keyboard_text[3], callback_data=callback_post[3]),types.InlineKeyboardButton(text=keyboard_text[4], callback_data=callback_post[4]),types.InlineKeyboardButton(text=keyboard_text[5], callback_data=callback_post[5]),
                    types.InlineKeyboardButton(text=keyboard_text[6], callback_data=callback_post[6]),types.InlineKeyboardButton(text=keyboard_text[7], callback_data=callback_post[7]),types.InlineKeyboardButton(text=keyboard_text[8], callback_data=callback_post[8])]
                    keyboard = types.InlineKeyboardMarkup(row_width=3)
                    keyboard.add(*buttons)

                    if progress_to_win_crosses(crosses_position) == 2:
                        game_message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (keyboard_text[0],keyboard_text[1],keyboard_text[2],keyboard_text[3],keyboard_text[4],keyboard_text[5],keyboard_text[6],keyboard_text[7],keyboard_text[8],game_info[1], game_info[0], game_info[3], game_info[2])
                        keyboard = None
                    elif progress_to_win_crosses(crosses_position) == 3:
                        game_message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (keyboard_text[0],keyboard_text[1],keyboard_text[2],keyboard_text[3],keyboard_text[4],keyboard_text[5],keyboard_text[6],keyboard_text[7],keyboard_text[8],game_info[1], game_info[0], game_info[3], game_info[2])
                        keyboard = None
                    elif progress_to_win_crosses(crosses_position) == 4:
                        game_message = "🍍 *Ничья!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s)" % (keyboard_text[0],keyboard_text[1],keyboard_text[2],keyboard_text[3],keyboard_text[4],keyboard_text[5],keyboard_text[6],keyboard_text[7],keyboard_text[8],game_info[1], game_info[0], game_info[3], game_info[2])
                        keyboard = None

                    if keyboard is None:
                        os.remove(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt")

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=game_message, parse_mode="Markdown",reply_markup=keyboard)
                    if keyboard is not None:
                        await asyncio.sleep(20)
                        if os.path.isfile(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt"):
                            with open(os.getcwd() + "/chats/" + str(callback_query.message.chat.id) + "/crosses/" + str(callback_query.message.message_id) + ".txt") as game:
                                game_info_next = game.read().split("|")

                            if int(game_info_next[5]) == int(game_info[5]) + 1:
                                if game_info_next[4] == "CROSS":
                                    game_message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - Не сделал(-а) ход\n⭕ [%s](tg://user?id=%s)" % (keyboard_text[0],keyboard_text[1],keyboard_text[2],keyboard_text[3],keyboard_text[4],keyboard_text[5],keyboard_text[6],keyboard_text[7],keyboard_text[8],game_info[1], game_info[0], game_info[3], game_info[2])
                                else:
                                    game_message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - Не сделал(-а) ход" % (keyboard_text[0],keyboard_text[1],keyboard_text[2],keyboard_text[3],keyboard_text[4],keyboard_text[5],keyboard_text[6],keyboard_text[7],keyboard_text[8],game_info[1], game_info[0], game_info[3], game_info[2])
                                keyboard = None
                                await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=game_message, parse_mode="Markdown",reply_markup=keyboard)

            else:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Произошла ошибка!\nПопробуйте позже или создайте новую игру.", show_alert=True)
        elif code == "Выбрано":

            return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Позиция уже занята!", show_alert=True)

    except Exception as e:
        print(repr(e)) 

if __name__ == "__main__":
    if not os.path.isdir("chats"):
            os.mkdir("chats")

    if not os.path.isdir("users"):
        os.mkdir("users")

    chats = os.listdir(os.getcwd() + "/chats")
    for temp in chats:
        try:
            file = os.getcwd() + "/chats/" + temp + "/info.txt"
            with open(os.getcwd() + "/chats/" + temp + "/info.txt") as game:
                result = game.read()

            if "ASSOCIATIONS" in result:
                players = os.listdir(os.getcwd() + "/chats/" + temp + "/associations")
                for item in players:
                    os.remove(os.getcwd() + "/chats/" + temp + "/associations/" + item)

            if "TITLES" in result:
                os.remove(os.getcwd() + "/chats/" + temp + "/titles.txt")

            os.remove(os.getcwd() + "/chats/" + temp + "/info.txt")
        except Exception as e:
            continue

    executor.start_polling(dp, skip_updates=True)

