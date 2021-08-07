from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import random
import requests
import os
import asyncio
import time
import logging

from bs4 import BeautifulSoup
from config import TOKEN,DEVELOPER

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Check have user admin in group
async def is_admin_group(chat_id, user_id):
    try:
        result = await bot.get_chat_member(chat_id, user_id)
        if "administrator" in result["status"] or "creator" in result["status"]:
            return True
        return False
    except Exception as e:
        print("CHECK ADMIN: %s" % repr(e))
        
# Check game in chat
def is_game_in_chat(chat_id):
    name_file_chat = "chats/%d.txt" % chat_id
    try:
        file = open(name_file_chat)
        text = file.read()
        file.close()
        if "ASSOCIATIONS" in text or "CROSSES" in text:
            return True
    except Exception as e:
        print("Check game: %s" % repr(e))
    return False

# Create chat 
def create_chat(chat_id):
    try:
        name_file_chat = "chats/%d.txt" % chat_id
        chat = open(name_file_chat, "+w")
        chat.close()
    except Exception as e:
        print("Create chat: %s" % repr(e))

# Take info game
def get_params_game(chat_id):
    try:
        name_file_chat = "chats/%d.txt" % chat_id
        data = open(name_file_chat)
        info = data.read()
        data.close()
        return info
    except Exception as e:
        print("Get params: %s" % repr(e))
    
# Check have user
def is_have_user(user_id):
    try:
        name_file_chat = "users/%d.txt" % user_id
        file = open(name_file_chat)
        text = file.read()
        file.close()
        if len(text) == 0:
            return True
    except Exception as e:
        return True
    return False

def set_user_game(user_id, game):
    try:
        name_file_user = "users/%d.txt" % user_id
        file = open(name_file_user, "+w")
        file.write(str(game))
        file.close()
    except Exception as e:
        print("Set game user: %s" % repr(e))   

# Type: new member
@dp.message_handler(content_types=["new_chat_members"])
async def new_chat_members_delete(message):
    try:
        if await is_admin_group(message.chat.id, message.bot.id):
            await bot.delete_message(message.chat.id, message.message_id)
        if message.new_chat_members[0].id == bot.id:
            # KeyBoard
            buttons  = [ 
            types.InlineKeyboardButton(text='Игры 📌', callback_data="Игры"),
            types.InlineKeyboardButton(text='Помощь ◀', callback_data="Помощь")
            ] 
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            create_chat(message.chat.id)
            return await message.answer("🍍 Приветствую Вас, господа!\nМеня зовут - *Ананасыч*\nЯ многофункциональный бот\n\nС моей помощью можно:\n💾 Играть в различные игры\n👮 Следить за порядком\n🔔 Администрировать чат\n\n***для полного функционала рекомендую выдать мне права администратора***", parse_mode="Markdown", reply_markup=keyboard)
        else:
            return await message.answer("🍍[%s](tg://user?id=%d), *добро пожаловать в %s*" % (message.new_chat_members[0].first_name, message.new_chat_members[0].id,message.chat.full_name), parse_mode="Markdown")
    except Exception as e:
        print("NEW CHAT MEMBERS: %s" % repr(e))

# Type: left member
@dp.message_handler(content_types=["left_chat_member"])
async def new_chat_members_delete(message):
    try:
        if await is_admin_group(message.chat.id, message.bot.id):
            await bot.delete_message(message.chat.id, message.message_id)
        await message.answer("🍍 [%s](tg://user?id=%d) покинул(-а) *%s*" % (message.left_chat_member.first_name, message.left_chat_member.id,message.chat.full_name), parse_mode="Markdown")
    except Exception as e:
        print("LEFT CHAT MEMBERS: %s" % repr(e))

# Command: start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    try:
        buttons  = [ 
        types.InlineKeyboardButton(text='Игры 📌', callback_data="Игры"),
        types.InlineKeyboardButton(text='Помощь ◀', callback_data="Помощь")
        ] 
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        Check_bot = await message.answer("Приветствую - я Ананасыч 🍍\nМногоспособный бот для веселья!", reply_markup=keyboard)
        if message.chat.id != message.from_user.id and await is_admin_group(message.chat.id, Check_bot.bot.id) == False:
            await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")
    except Exception as e:
        print("START COMMAND: %s" % repr(e))

# Bag command
@dp.message_handler(commands=['bag'])
async def mute_command(message: types.Message):
    try:
        text = message.text.split(" ")
        if len(text) < 2:
            return await message.reply("🍍 *Нет текста сообщения*\n\nИспользуйте: /bag [Текст]")
            
        await message.reply("🍍 Сообщение было отправлено!")

        text = message.text.replace(text[0], "")
        message = "⚠ *Сообщение о баге*\n\nОтправитель: [%s](tg://user?id=%d)\nЧат ID: %d\nUser ID: %d\n\nСообщение:\n%s" % (message.from_user.first_name,message.from_user.id,message.chat.id,message.from_user.id,text)
        await bot.send_message(DEVELOPER, message, parse_mode="Markdown")
    except Exception as e:
        print("BAG COMMAND: %s" % repr(e)) 

# Admins commands
# Command: mute
@dp.message_handler(commands=['mute'])
async def mute_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await message.answer("🍍 Нужно использовать только в чатах!")

        if not message.reply_to_message:
            return await message.reply("🍍 Команда должна быть использована на ответное сообщение!")

        if await is_admin_group(message.chat.id, message.bot.id) == False:
            return await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

        if message.reply_to_message.from_user.id == message.bot.id:
            return await message.reply("🍍 Невозможно использовать команду...")

        if await is_admin_group(message.chat.id, message.from_user.id) == False:
            return await bot.delete_message(message.chat.id, message.message_id)

        if await is_admin_group(message.chat.id, message.reply_to_message.from_user.id):
            return await message.reply("🍍 [%s](tg://user?id=%d) является *Администратором*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")

        await message.answer("🍍 [%s](tg://user?id=%d) *не сможет писать в чат 5 минут*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,until_date=int(time.time()) + 60*5,can_send_messages=False)
    except Exception as e:
        print("MUTE COMMAND: %s" % repr(e))  

# Command: Kick
@dp.message_handler(commands=['kick'])
async def kick_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await message.answer("🍍 Нужно использовать только в чатах!")

        if not message.reply_to_message:
            return await message.reply("🍍 Команда должна быть использована на ответное сообщение!")

        if await is_admin_group(message.chat.id, message.bot.id) == False:
            return await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

        if message.reply_to_message.from_user.id == message.bot.id:
            return await message.reply("🍍 Невозможно использовать команду...")

        if await is_admin_group(message.chat.id, message.from_user.id) == False:
            return await bot.delete_message(message.chat.id, message.message_id)

        if await is_admin_group(message.chat.id, message.reply_to_message.from_user.id):
            return await message.reply("🍍 [%s](tg://user?id=%d) является *Администратором*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")

        await bot.delete_message(message.chat.id, message.message_id)
        await message.answer("🍍 [%s](tg://user?id=%d) *кикнул(-а)* [%s](tg://user?id=%d)" % (message.from_user.first_name,message.from_user.id,message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")
        await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    except Exception as e:
        print("KICK COMMAND: %s" % repr(e))  

# Games
# Command: Fanta
@dp.message_handler(commands=['fanta'])
async def fanta_command(message: types.Message):
    try:

        buttons  = [types.InlineKeyboardButton(text='Дальше', callback_data="Дальше")] 
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        data = open("fanta_message.txt", encoding="utf8")
        mission = data.read().replace("\\n", "\n").split("|")
        data.close()
        select_mission = random.randint(0,len(mission)) - 1

        await bot.send_message(message.chat.id, "🍍 %s" % mission[select_mission], parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        print("FANTA COMMAND: %s" % repr(e))

# Command: Mafia
@dp.message_handler(commands=['mafia'])
async def start_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await bot.send_message(message.from_user.id, "🍍 Эту игру можно запустить только в группе)")

        if is_have_user(message.from_user.id) == False:
            return await bot.delete_message(message.chat.id, message.message_id)

        if is_game_in_chat(message.chat.id) == False:
            buttons = [types.InlineKeyboardButton(text='Присоединиться', url="https://telegram.me/PineAppleAPP_bot?start=%d" % message.chat.id)] 
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            Check_bot = await message.answer("🍍 [%s](tg://user?id=%d) запустил игру *мафия*\n\nУчастники:\n[%s](tg://user?id=%d)" % (message.from_user.first_name,message.from_user.id,message.from_user.first_name,message.from_user.id), parse_mode="Markdown", reply_markup=keyboard)
            if message.chat.id != message.from_user.id and await is_admin_group(message.chat.id, Check_bot.bot.id) == False:
                await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")
    except Exception as e:
        print("START COMMAND: %s" % repr(e))

# Command: crosses
@dp.message_handler(commands=['crosses'])
async def crosses_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await bot.send_message(message.from_user.id, "🍍 Эту игру можно запустить только в группе)")

        if is_have_user(message.from_user.id) == False:
            return await bot.delete_message(message.chat.id, message.message_id)

        if is_game_in_chat(message.chat.id) == False:
 
            buttons  = [types.InlineKeyboardButton(text='Присоединится', callback_data="Крестики-нолики")] 
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            name_file = "chats/%d.txt" % message.chat.id

            get_info = await bot.send_message(message.chat.id, "🍍 [%s](tg://user?id=%d) хочет поиграть в крестики-нолики" % (message.from_user.first_name,message.from_user.id), parse_mode="Markdown", reply_markup=keyboard)
            if message.chat.id != message.from_user.id and await is_admin_group(message.chat.id, bot.id) == False:
                await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

            data = open(name_file, "w+")
            data.write("CROSSES|%d|%s|0|None|CROSS|%d" % (message.from_user.id,message.from_user.first_name,get_info.message_id))
            data.close()

            set_user_game(message.from_user.id, message.chat.id)

            await asyncio.sleep(60)
            result = get_params_game(message.chat.id).split("|")
            if int(result[3]) == 0:
                data = open(name_file, "w+")
                data.write("")
                data.close()
                set_user_game(message.from_user.id, "")
                await bot.edit_message_text(chat_id=message.chat.id, message_id=get_info.message_id, text="🍍 *Никто не хочет играть в крестики-нолики:(*", parse_mode="Markdown",reply_markup=None)
        else:
            if await is_admin_group(message.chat.id, message.bot.id):
                await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print("CROSSES COMMAND: %s" % repr(e))

# Command: associations
@dp.message_handler(commands=['associations'])
async def associations_command(message: types.Message):
    try:
        if is_game_in_chat(message.chat.id) == False:
            file = open("words_for_associations.txt")
            words = file.read().split(",")

            POS_WORD = random.randint(0, len(words))

            get_info = await bot.send_message(message.chat.id, "🍍 Ассоциации\n\n[%s](tg://user?id=%d) запустил игру!\n\n✏ Пишите ассоциации к слову в течении 120 секунд\n⚡ Зарабатывайте очки и выигрывайте\n\nСлово для ассоциаций: *%s*" % (message.from_user.first_name,message.from_user.id,words[POS_WORD]), parse_mode="Markdown")
            if message.chat.id != message.from_user.id and await is_admin_group(message.chat.id, get_info.bot.id) == False:
                await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

            url = 'http://www.slovesa.ru/assearch?q=%s' % words[POS_WORD]
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            sections = soup.find_all('div', class_='tagcloud')

            name_file = "chats/associations/%d.txt" % message.chat.id
            words_file = open(name_file, "w+")
            for item in sections:
                words_file.write(item.get_text().replace('  ', ',').replace(" ", "").replace(",А,Б,В,Г,Д,Е,Ж,З,И,К,Л,М,Н,О,П,Р,С,Т,У,Ф,Х,Ц,Ч,Ш,Щ,Э,Ю,Я,", ""))

            words_file.close()

            name_file = "chats/%d.txt" % message.chat.id
            data = open(name_file, "w+")
            data.write("ASSOCIATIONS")
            data.close()

            await asyncio.sleep(60)
            await bot.send_message(message.chat.id, "🍍 *Ассоциации*\n\n⌛Осталось: 60 секунд...", parse_mode="Markdown")

            await asyncio.sleep(30)
            await bot.send_message(message.chat.id, "🍍 *Ассоциации*\n\n⌛Осталось: 30 секунд...", parse_mode="Markdown")

            await asyncio.sleep(30)
            data = open(name_file)
            records = data.read().replace("ASSOCIATIONS|", "").split("|")
            data.close()

            count = 0
            people = 1
            score = []

            text_message = "🍍 *Ассоциации*\n\nИгра закончена!\n\nУчастники:\n"

            for i in range(len(records)):
                try:
                    text_message += "%d. [%s](tg://user?id=%s) - ⚡ %s\n" %  (people, records[count + 1], records[count], records[count + 2])
                    score.append(records[count + 2])
                    count += 3
                    people += 1
                    if count >= len(records):
                        break
                except Exception as e:
                    print("ASSOCIATIONS COMMAND(FOR): %s" % repr(e))

            name_file = "chats/%d.txt" % message.chat.id
            data = open(name_file, "w+")
            data.write("")
            data.close()

            return await bot.send_message(message.chat.id, text_message, parse_mode="Markdown")
        else:
            if await is_admin_group(message.chat.id, message.bot.id):
                await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print("ASSOCIATIONS COMMAND: %s" % repr(e))

# Types: text
@dp.message_handler(content_types=["text"])
async def check_all_messages(message):
    try:
        for_bad_word = open('bad_words.txt', encoding="utf8")
        bad_words = for_bad_word.read().split(",")
        for word in bad_words:
            if word.lower() in message.text.lower():
                if await is_admin_group(message.chat.id, message.bot.id):
                    await bot.delete_message(message.chat.id, message.message_id)
                await message.answer("🤬 Попрошу не выражаться!")
                break

        if is_game_in_chat(message.chat.id) and message.chat.id != message.from_user.id:
            result = get_params_game(message.chat.id)
            if "ASSOCIATIONS" in str(result):
                data = open('chats/associations/%d.txt' % message.chat.id)
                read_text = data.read()
                data.close()
                text = read_text.split(',')
                for item in text:
                    if message.text.lower() == item.lower():
                        data = open('chats/associations/%d.txt' % message.chat.id, "w")
                        data.write(read_text.replace("%s," % item, ""))
                        data.close()

                        accept = ["Великолепно!", "Прекрасно!", "Умно!", "Замечательно!", "Восхитительно!", "Молодец!", "Гений!", "Блестяще!"]
                        RANDOM_POS = random.randint(0, len(accept))
                        await message.reply("🍍 %s\n*%s* засчитано\n\n⚡ +%d Очков" % (accept[RANDOM_POS], message.text, len(message.text) / 2), parse_mode="Markdown")

                        main_file = open("chats/%d.txt" % message.chat.id)
                        text = main_file.read()
                        main_file.close()
                        if str(message.from_user.id) in text:
                            result = text.replace("ASSOCIATIONS|", "").split("|")
                            for_result = 0
                            for item in result:
                                if item == str(message.from_user.id):
                                    summa = (len(message.text) / 2) + int(result[for_result + 2])
                                    need_replace = "%s|%s|%s" % (result[for_result],result[for_result + 1],result[for_result + 2])
                                    replace_text = "%s|%s|%s" % (result[for_result],result[for_result + 1],int(summa))
                                    data = text.replace(need_replace, replace_text)
                                    text = data
                                    break
                                for_result+=1
                        else:
                            text += "|%d|%s|%d" % (message.from_user.id,message.from_user.first_name,len(message.text) / 2)
                        main_file = open("chats/%d.txt" % message.chat.id, "w")
                        main_file.write(text)
                        main_file.close()
                        break
    except Exception as e:
        print("READ TEXT: %s" % repr(e))

@dp.chosen_inline_handler(lambda selected_inline_result: True)
def test_chosen(selected_inline_result):
    print(selected_inline_result)

# Types: callback keyboard
@dp.callback_query_handler(lambda callback_query: True)
async def some_callback_handler(callback_query: types.CallbackQuery):
    print(callback_query.data)
    try:
        code = callback_query.data
        if code == "Игры":
            message = "🍍 *Игры*\n\n/crosses - Игра крестики-нолики\n📌 Играть можно только в чатах\n\n/associations - Игра в ассоциации\n📌 Бот пишет слово, а ты придумываешь к нему слово-ассоциацию, чем длиннее слово, тем больше очков\n\n/fanta - Игра для 'культурной' посиделки 🔞"
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=None)
        elif code == "Помощь":
            message = "🍍 *Помощь*\n\nВ случае возникновения технической проблемы\nОбратитесь в техническую поддержку\n\n📌 Используйте: */bag [Текст]*"
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=None)
        elif code == "Крестики-нолики":

            if is_have_user(callback_query.message.from_user.id) == False:
                return bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Вы уже участвуете в другой игре!", show_alert=True)

            if is_game_in_chat(callback_query.message.chat.id):
                name_file = "chats/%d.txt" % callback_query.message.chat.id
                result = get_params_game(callback_query.message.chat.id).replace("CROSSES|", "").split("|")
                if int(result[0]) != callback_query.from_user.id and int(result[2]) == 0:
                    data = open(name_file, "w+")
                    data.write("CROSSES|%s|%s|%s|%s|CROSS|%d|1|0|0|0|0|0|0|0|0|0" % (result[0], result[1], callback_query.from_user.id, callback_query.from_user.first_name, callback_query.message.message_id))
                    data.close()

                    set_user_game(callback_query.from_user.id, callback_query.message.chat.id)

                    TEXT_KEYBOARD = ["⏺","⏺","⏺","⏺","⏺","⏺","⏺","⏺","⏺"]
                    TEXT_CALLBACK = [1, 2, 3, 4, 5, 6, 7, 8, 9]

                    buttons = [types.InlineKeyboardButton(text=TEXT_KEYBOARD[0], callback_data=TEXT_CALLBACK[0]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[1], callback_data=TEXT_CALLBACK[1]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[2], callback_data=TEXT_CALLBACK[2]),
                    types.InlineKeyboardButton(text=TEXT_KEYBOARD[3], callback_data=TEXT_CALLBACK[3]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[4], callback_data=TEXT_CALLBACK[4]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[5], callback_data=TEXT_CALLBACK[5]),
                    types.InlineKeyboardButton(text=TEXT_KEYBOARD[6], callback_data=TEXT_CALLBACK[6]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[7], callback_data=TEXT_CALLBACK[7]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[8], callback_data=TEXT_CALLBACK[8])]
                    keyboard = types.InlineKeyboardMarkup(row_width=3)
                    keyboard.add(*buttons)

                    message = "🍍 Игра началась!\n⌛ На ход: *60 секунд*\n\n❌ [%s](tg://user?id=%s) ходит крестиками\n⭕ [%s](tg://user?id=%s) ходит ноликами\n\nПервым ходит: [%s](tg://user?id=%s) ❌" % (result[1], result[0], callback_query.from_user.first_name, callback_query.from_user.id, result[1], result[0])
                    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=keyboard)

                    await asyncio.sleep(60)
                    flag = get_params_game(callback_query.message.chat.id).replace("CROSSES|", "").split("|")
                    if int(flag[6]) == 1:
                        message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - Не сделал(-а) ход\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],flag[1], flag[0], flag[3], flag[2])
                        data = open(name_file, "w+")
                        data.write("")
                        data.close()
                        keyboard = None
                        return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=keyboard)
                
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Вы уже участвуете в другой игре!", show_alert=True)

            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="🍍 *Произошла ошибка!*", parse_mode="Markdown",reply_markup=None)
        elif code == "Выбрано":
            return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Позиция уже занята!", show_alert=True)
        elif code == "Дальше":
            buttons  = [types.InlineKeyboardButton(text='Дальше', callback_data="Дальше")] 
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            data = open("fanta_message.txt", encoding="utf8")
            mission = data.read().replace("\\n", "\n").split("|")
            data.close()

            select_mission = random.randint(0,len(mission)) - 1
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="🍍 %s" % mission[select_mission], parse_mode="Markdown",reply_markup=keyboard)
        elif code == "1" or code == "2" or code == "3" or code == "4" or code == "5" or code == "6" or code == "7" or code == "8" or code == "9":
            if is_game_in_chat(callback_query.message.chat.id):
                result = get_params_game(callback_query.message.chat.id).replace("CROSSES|", "").split("|")
                if (int(result[0]) == callback_query.from_user.id and result[4] == "CROSS") or (int(result[2]) == callback_query.from_user.id and result[4] == "ZERO"):
                    name_file = "chats/%d.txt" % callback_query.message.chat.id
                    TEXT_KEYBOARD = ["⏺","⏺","⏺","⏺","⏺","⏺","⏺","⏺","⏺"]
                    TEXT_CALLBACK = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

                    code = int(code)
                    message = "Для текста сообщения"
                    check_pos = []
                    write_message = "EOS"
                    for a in range(9):
                        check_pos.append(int(result[a+7]))

                    if int(result[0]) == callback_query.from_user.id and result[4] == "CROSS":
                        message = "🍍 Игра началась!\n⌛ На ход: *60 секунд*\n\n❌ [%s](tg://user?id=%s) ходит крестиками\n⭕ [%s](tg://user?id=%s) ходит ноликами\n\nСейчас ходит: [%s](tg://user?id=%s) ⭕" % (result[1], result[0], result[3], result[1], result[3], result[1])
                        check_pos[code - 1] = 2
                        write_message = "CROSSES|%s|%s|%s|%s|ZERO|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d" % (result[0], result[1], result[2], result[3], callback_query.message.message_id, int(result[6]) + 1, check_pos[0],check_pos[1],check_pos[2],check_pos[3],check_pos[4],check_pos[5],check_pos[6],check_pos[7],check_pos[8])
                    else:
                        message = "🍍 Игра началась!\n⌛ На ход: *60 секунд*\n\n❌ [%s](tg://user?id=%s) ходит крестиками\n⭕ [%s](tg://user?id=%s) ходит ноликами\n\nСейчас ходит: [%s](tg://user?id=%s) ❌" % (result[1], result[0], result[3], result[1], result[1], result[0])
                        check_pos[code - 1] = 3
                        write_message = "CROSSES|%s|%s|%s|%s|CROSS|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d" % (result[0], result[1], result[2], result[3], callback_query.message.message_id, int(result[6]) + 1, check_pos[0],check_pos[1],check_pos[2],check_pos[3],check_pos[4],check_pos[5],check_pos[6],check_pos[7],check_pos[8])
                    
                    data = open(name_file, "w+")
                    data.write(write_message)
                    data.close()
                    for i in range(9):
                        if check_pos[i] == 2:
                            TEXT_KEYBOARD[i] = "❌"
                            TEXT_CALLBACK[i] = "Выбрано"
                        elif check_pos[i] == 3:
                            TEXT_KEYBOARD[i] = "⭕"
                            TEXT_CALLBACK[i] = "Выбрано"

                    DESTROY_MATCH = False
                    WHO_WIN = 0

                    if check_pos[0] != 0 and check_pos[0] == check_pos[1] and check_pos[1] == check_pos[2]:
                        if check_pos[0] == 2:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[1]
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[2]
                        DESTROY_MATCH = True
                    elif check_pos[3] != 0 and check_pos[3] == check_pos[4] and check_pos[4] == check_pos[5]:
                        if check_pos[3] == 2:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                        DESTROY_MATCH = True
                    elif check_pos[6] != 0 and check_pos[6] == check_pos[7] and check_pos[7] == check_pos[8]:
                        if check_pos[6] == 2:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[1]
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[2]
                        DESTROY_MATCH = True
                    elif check_pos[0] != 0 and check_pos[0] == check_pos[3] and check_pos[3] == check_pos[6]:
                        if check_pos[0] == 2:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[1]
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[2]
                        DESTROY_MATCH = True
                    elif check_pos[1] != 0 and check_pos[1] == check_pos[4] and check_pos[4] == check_pos[7]:
                        if check_pos[1] == 2:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[1]
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[2]
                        DESTROY_MATCH = True
                    elif check_pos[2] != 0 and check_pos[2] == check_pos[5] and check_pos[5] == check_pos[8]:
                        if check_pos[2] == 2:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[1]
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[2]
                        DESTROY_MATCH = True
                    elif check_pos[0] != 0 and check_pos[0] == check_pos[4] and check_pos[4] == check_pos[8]:
                        if check_pos[0] == 2:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[1]
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[2]
                        DESTROY_MATCH = True
                    elif check_pos[2] != 0 and check_pos[2] == check_pos[4] and check_pos[4] == check_pos[6]:
                        if check_pos[2] == 2:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - 👑\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[1]
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - 👑" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                            WHO_WIN = result[2]
                        DESTROY_MATCH = True
                    elif check_pos[0] != 0 and check_pos[1] != 0 and check_pos[2] != 0 and check_pos[3] != 0 and check_pos[4] != 0 and check_pos[5] != 0 and check_pos[6] != 0 and check_pos[7] != 0 and check_pos[8] != 0:
                        message = "🍍 *Ничья!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                        DESTROY_MATCH = True

                    buttons = [types.InlineKeyboardButton(text=TEXT_KEYBOARD[0], callback_data=TEXT_CALLBACK[0]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[1], callback_data=TEXT_CALLBACK[1]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[2], callback_data=TEXT_CALLBACK[2]),
                    types.InlineKeyboardButton(text=TEXT_KEYBOARD[3], callback_data=TEXT_CALLBACK[3]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[4], callback_data=TEXT_CALLBACK[4]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[5], callback_data=TEXT_CALLBACK[5]),
                    types.InlineKeyboardButton(text=TEXT_KEYBOARD[6], callback_data=TEXT_CALLBACK[6]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[7], callback_data=TEXT_CALLBACK[7]),types.InlineKeyboardButton(text=TEXT_KEYBOARD[8], callback_data=TEXT_CALLBACK[8])]
                    keyboard = types.InlineKeyboardMarkup(row_width=3)
                    keyboard.add(*buttons)

                    if DESTROY_MATCH:
                        data = open(name_file, "w+")
                        data.write("")
                        data.close()
                        keyboard = None

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=keyboard)
                    await asyncio.sleep(60)
                    flag = get_params_game(callback_query.message.chat.id).replace("CROSSES|", "").split("|")
                    if int(flag[6]) == int(result[6]) + 1:
                        if flag[4] == "CROSS":
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - Не сделал(-а) ход\n⭕ [%s](tg://user?id=%s)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                        else:
                            message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - Не сделал(-а) ход" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],result[1], result[0], result[3], result[2])
                        data = open(name_file, "w+")
                        data.write("")
                        data.close()
                        keyboard = None

                        set_user_game(int(result[0]), "")
                        set_user_game(int(result[2]), "")

                        return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=keyboard)
                    
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Вы не можете ходить!", show_alert=True)
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="🍍 *Произошла ошибка!*", parse_mode="Markdown",reply_markup=None)
    except Exception as e:
        print("CALLBACK=%s: %s" % (code,repr(e)))

if __name__ == '__main__':
    try:
        # Start bot
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print(repr(e))
