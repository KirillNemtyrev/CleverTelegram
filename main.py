from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import random
from random import choice

import requests
import os
import asyncio
import time
from bs4 import BeautifulSoup
from config import TOKEN,DEVELOPER

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

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
    file = "chats/" + str(chat_id) + "/" + "info.txt"
    try:
        opened = open(file)
        opened.close()
        return True
    except FileNotFoundError:
        return False
    return False

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
    except Exception as e:
        print(repr(e)) 

# Remove dirs
def remove_dirs_chat(chat_id):
    try:
        path = os.path.join(os.getcwd() + "/chats", str(chat_id))
        cash = os.path.exists(path) 
        if os.path.exists(path):
            dirs = os.listdir("/chats/" + str(chat_id))
            if dirs:
                for temp in dirs:
                    name = "chats/" + str(chat_id) + "/" + temp
                    if ".txt" in temp:
                        os.remove(name)
                    else:
                        os.rmdir(name)
            os.rmdir("chats/" + str(chat_id))

    except Exception as e:
        print(repr(e)) 

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
            await message.answer("🍍 Приветствую Вас, господа!\nМеня зовут - *Ананасыч*\nЯ многофункциональный бот\n\nС моей помощью можно:\n💾 Играть в различные игры\n👮 Следить за порядком\n🔔 Администрировать чат\n\n_для полного функционала рекомендую выдать мне права администратора_", parse_mode="Markdown", reply_markup=keyboard)
        
            verification_dirs_chat(message.chat.id)
        else:
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
    except Exception as e:
        print(repr(e))

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
        print(repr(e))

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
        print(repr(e)) 

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

        await message.answer("🍍 [%s](tg://user?id=%d) *не сможет писать в чат 30 минут*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,until_date=int(time.time()) + 60*30,can_send_messages=False)
    except Exception as e:
        print(repr(e))  

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
        print(repr(e)) 

# Games
# Command: Fanta
@dp.message_handler(commands=['fanta'])
async def fanta_command(message: types.Message):
    try:

        buttons  = [types.InlineKeyboardButton(text='Дальше', callback_data="Дальше")] 
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        data = open("info/fanta_message.txt", encoding="utf8")
        mission = data.read().replace("\\n", "\n").split("|")
        data.close()
        select_mission = random.randint(0,len(mission)) - 1

        await bot.send_message(message.chat.id, "🍍 %s" % mission[select_mission], parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        print(repr(e)) 

# Command: crosses
@dp.message_handler(commands=['crosses'])
async def crosses_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await bot.send_message(message.from_user.id, "🍍 Эту игру можно запустить только в группе)")

        if is_game_in_chat(message.chat.id):
            if await is_admin_group(message.chat.id, message.bot.id) == False:
                return message.answer("🍍 *В чате уже идёт игра!*")
            await bot.delete_message(message.chat.id, message.message_id)

        buttons  = [types.InlineKeyboardButton(text='Присоединиться', callback_data="Крестики-нолики")] 
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        verification_dirs_chat(message.chat.id)

        info = await message.reply("🍍 [%s](tg://user?id=%d) хочет поиграть в крестики-нолики" % (message.from_user.first_name,message.from_user.id), parse_mode="Markdown", reply_markup=keyboard)
        if message.chat.id != message.from_user.id and await is_admin_group(message.chat.id, bot.id) == False:
            await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

        await asyncio.sleep(20)
        file = "/chats/" + str(message.chat.id) + "/" + str(info.message_id)
        try:
            opened = open(file)
            opened.close()
        except FileNotFoundError:
            return await bot.edit_message_text(chat_id=message.chat.id, message_id=info.message_id, text="🍍 *Никто не хочет играть:(*", parse_mode="Markdown",reply_markup=None)
        
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
        DESTROY_MATCH = True
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

# Command: associations
@dp.message_handler(commands=['associations'])
async def associations_command(message: types.Message):
    try:
        if is_game_in_chat(message.chat.id):
            if await is_admin_group(message.chat.id, message.bot.id) == False:
                return message.answer("🍍 *В чате уже идёт игра!*")
            return await bot.delete_message(message.chat.id, message.message_id)

        file = open("info/words_for_associations.txt", encoding="utf8")
        words = file.read().split(",")
        POS_WORD = random.randint(0, len(words) - 1)

        verification_dirs_chat(message.chat.id)

        step_first_message = await bot.send_message(message.chat.id, "🍍 Ассоциации\n\n[%s](tg://user?id=%d) запустил игру!\n\n✏ Пишите ассоциации к слову в течении 120 секунд\n⚡ Зарабатывайте очки и выигрывайте\n\nСлово для ассоциаций: *%s*" % (message.from_user.first_name,message.from_user.id,words[POS_WORD]), parse_mode="Markdown")
        if message.chat.id != message.from_user.id and await is_admin_group(message.chat.id, bot.id) == False:
            await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

        parse_words(message.chat.id, words[POS_WORD])

        file = "chats/" + str(message.chat.id) + "/info.txt"
        parse = "chats/" + str(message.chat.id) + "/parse.txt"

        game = open(file, "+w")
        game.write("ASSOCIATIONS")
        game.close()

        await asyncio.sleep(60)
        step_second_message = await bot.send_message(message.chat.id, "🍍 *Ассоциации*\n\nНапоминаю слово: *%s*\n⌛Осталось: 60 секунд..." % words[POS_WORD], parse_mode="Markdown")

        await asyncio.sleep(30)
        step_third_message = await bot.send_message(message.chat.id, "🍍 *Ассоциации*\n\nНапоминаю слово: *%s*\n⌛Осталось: 30 секунд..." % words[POS_WORD], parse_mode="Markdown")

        await asyncio.sleep(30)
        dirs = os.listdir(os.getcwd() + "/chats/" + str(message.chat.id) + "/associations")

        os.remove(file)
        os.remove(parse)

        if not dirs:
            if await is_admin_group(message.chat.id, bot.id):
                # Remove messages
                await bot.delete_message(message.chat.id, message.message_id)
                await bot.delete_message(message.chat.id, step_first_message.message_id)
                await bot.delete_message(message.chat.id, step_second_message.message_id)
                return await bot.delete_message(message.chat.id, step_third_message.message_id)

            return await bot.send_message(message.chat.id, "🍍 *Ассоциации*\nИгра завершена!", parse_mode="Markdown")

        game_message = "🍍 *Ассоциации*\nИгра завершена!\n\nУчастники:\n"
        count = 1

        for item in dirs:
            file = "chats/" + str(message.chat.id) + "/associations/" + item
            player = open(file)
            score = int(player.read())
            player.close()

            os.remove(file)

            index = int(item.replace(".txt", ""))
            info = await bot.get_chat_member(message.chat.id, index)

            game_message += "%d. [%s](tg://user?id=%d) - ⚡ %d очков.\n" % (count, info.user.first_name, index, score)
            count += 1

        return await bot.send_message(message.chat.id, game_message, parse_mode="Markdown")   

    except Exception as e:
        print(repr(e)) 

def parse_words(chat_id, word):
    try:
        desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']

        url = 'http://sinonim.org/as/%s' % word
        response = requests.get(url, headers={'User-Agent': choice(desktop_agents),'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'})
        soup = BeautifulSoup(response.text, 'lxml')
        sections = soup.find_all('ul', class_="assocPodryad")
        cases = soup.find_all('li')

        file = "chats/" + str(chat_id) + "/parse.txt"
        parse = open(file, "+w")

        for item in cases:
            text = item.get_text()
            if "." not in text:
                parse.write(text + ",")

        parse.close()
    except Exception as e:
        print(repr(e))

# Types: text
@dp.message_handler(content_types=["text"])
async def check_all_messages(message):
    try:
        file = open('info/bad_words.txt', encoding="utf8")
        text = file.read().split(" ")
        file.close()

        for temp in text:
            if message.text.lower() == temp:
                if await is_admin_group(message.chat.id, message.bot.id):
                    return await bot.delete_message(message.chat.id, message.message_id)
                return await message.reply("🤬 Попрошу не выражаться!")
                break

        if is_game_in_chat(message.chat.id) == False:
            return True

        file = "chats/" + str(message.chat.id) + "/info.txt"
        game = open(file)
        if "ASSOCIATIONS" in game.read():
            file = "chats/" + str(message.chat.id) + "/parse.txt"
            parse = open(file)
            text = parse.read()
            parse.close()

            text_split = text.split(",")
            FIND = False

            for item in text_split:
                if message.text.lower() == item:
                    FIND = True
                    break

            if FIND is True:

                parse = open(file, "+w")
                parse.write(text.replace(message.text.lower() + ",", ""))
                parse.close()

                await message.reply("🍍 *Ассоциации*\n\nСлово *%s* засчитано\n⚡ *+%d очков*" % (message.text, len(message.text) / 2), parse_mode="Markdown")  

                file = "chats/" + str(message.chat.id) + "/associations/" + str(message.from_user.id) + ".txt" 
                try:
                    player = open(file)
                    score = int(player.read())
                    player.close()

                    player = open(file, "+w")
                    player.write(str(score + int(len(message.text) / 2)))
                    player.close()
                except FileNotFoundError:
                    player = open(file, "+w")
                    player.write(str(int(len(message.text) / 2)))
                    player.close()
                
    except Exception as e:
        print(repr(e)) 

# Types: callback keyboard
@dp.callback_query_handler(lambda callback_query: True)
async def some_callback_handler(callback_query: types.CallbackQuery):
    try:
        code = callback_query.data
        if code == "Игры":

            message = "🍍 *Игры*\n\n/crosses - Игра крестики-нолики\n📌 Играть можно только в чатах\n\n/associations - Игра в ассоциации\n📌 Бот пишет слово, а ты придумываешь к нему слово-ассоциацию, чем длиннее слово, тем больше очков\n\n/fanta - Игра для 'культурной' посиделки 🔞"
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=None)
        
        elif code == "Помощь":

            message = "🍍 *Помощь*\n\nВ случае возникновения технической проблемы\nОбратитесь в техническую поддержку\n\n📌 Используйте: */bag [Текст]*"
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=None)
       
        elif code == "Крестики-нолики":

            if callback_query.from_user.id == callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Вы являетесь участником этой игры...", show_alert=True)

            buttons = [types.InlineKeyboardButton(text="⏺", callback_data="1"),types.InlineKeyboardButton(text="⏺", callback_data="2"),types.InlineKeyboardButton(text="⏺", callback_data="3"),
            types.InlineKeyboardButton(text="⏺", callback_data="4"),types.InlineKeyboardButton(text="⏺", callback_data="5"),types.InlineKeyboardButton(text="⏺", callback_data="6"),
            types.InlineKeyboardButton(text="⏺", callback_data="7"),types.InlineKeyboardButton(text="⏺", callback_data="8"),types.InlineKeyboardButton(text="⏺", callback_data="9")]
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            keyboard.add(*buttons)

            message = "🍍 Игра началась!\n⌛ На ход: *60 секунд*\n\n❌ [%s](tg://user?id=%d) ходит крестиками\n⭕ [%s](tg://user?id=%d) ходит ноликами\n\nПервым ходит: [%s](tg://user?id=%d) ❌" % (callback_query.message.reply_to_message.from_user.first_name, callback_query.message.reply_to_message.from_user.id, callback_query.from_user.first_name, callback_query.from_user.id, callback_query.message.reply_to_message.from_user.first_name, callback_query.message.reply_to_message.from_user.id)
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=keyboard)
    
            file = "/chats/" + str(callback_query.message.chat.id) + "/" + str(callback_query.message.message_id) + ".txt"
            game = open(file, "w+")
            game.write("%d|%s|%d|%s|CROSS|1|0|0|0|0|0|0|0|0|0" % (callback_query.message.reply_to_message.from_user.id, callback_query.message.reply_to_message.from_user.first_name, callback_query.from_user.id, callback_query.from_user.first_name))
            game.close()

            try:
                await asyncio.sleep(60)
                game = open(file)
                game_split = game.read().split("|")
                if int(game_split[5]) == 1:
                    message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%d) - Не сделал(-а) ход\n⭕ [%s](tg://user?id=%d)" % (TEXT_KEYBOARD[0],TEXT_KEYBOARD[1],TEXT_KEYBOARD[2],TEXT_KEYBOARD[3],TEXT_KEYBOARD[4],TEXT_KEYBOARD[5],TEXT_KEYBOARD[6],TEXT_KEYBOARD[7],TEXT_KEYBOARD[8],callback_query.message.reply_to_message.from_user.first_name, callback_query.message.reply_to_message.from_user.id, callback_query.from_user.first_name, callback_query.from_user.id)
                    return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=None)
            except FileNotFoundError:
                    return False

        elif code == "1" or code == "2" or code == "3" or code == "4" or code == "5" or code == "6" or code == "7" or code == "8" or code == "9":
            try:
                file = "/chats/" + str(callback_query.message.chat.id) + "/" + str(callback_query.message.message_id) + ".txt"
                game = open(file)
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
                        game_message = "🍍 Игра началась!\n⌛ На ход: *60 секунд*\n\n❌ [%s](tg://user?id=%s) ходит крестиками\n⭕ [%s](tg://user?id=%s) ходит ноликами\n\nСейчас ходит: [%s](tg://user?id=%s) ⭕" % (game_info[1], game_info[0], game_info[3], game_info[2], game_info[3], game_info[2])
                        crosses_position[position] = 2
                        write_to_txt = "%s|%s|%s|%s|ZERO|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d" % (game_info[0], game_info[1], game_info[2], game_info[3], int(game_info[5]) + 1, crosses_position[0],crosses_position[1],crosses_position[2],crosses_position[3],crosses_position[4],crosses_position[5],crosses_position[6],crosses_position[7],crosses_position[8])
                    else:
                        game_message = "🍍 Игра началась!\n⌛ На ход: *60 секунд*\n\n❌ [%s](tg://user?id=%s) ходит крестиками\n⭕ [%s](tg://user?id=%s) ходит ноликами\n\nСейчас ходит: [%s](tg://user?id=%s) ❌" % (game_info[1], game_info[0], game_info[3], game_info[2], game_info[1], game_info[0])
                        crosses_position[position] = 3
                        write_to_txt = "%s|%s|%s|%s|CROSS|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d" % (game_info[0], game_info[1], game_info[2], game_info[3], int(game_info[5]) + 1, crosses_position[0],crosses_position[1],crosses_position[2],crosses_position[3],crosses_position[4],crosses_position[5],crosses_position[6],crosses_position[7],crosses_position[8])
                    
                    game = open(file, "w+")
                    game.write(write_to_txt)
                    game.close()

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
                        os.remove(file)

                    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=game_message, parse_mode="Markdown",reply_markup=keyboard)
                    if keyboard is not None:
                        try:
                            await asyncio.sleep(60)
                            game = open(file)
                            game_info_next = game.read().split("|")
                            if int(game_info_next[5]) == int(game_info[5]) + 1:
                                if game_info_next[4] == "CROSS":
                                    game_message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s) - Не сделал(-а) ход\n⭕ [%s](tg://user?id=%s)" % (keyboard_text[0],keyboard_text[1],keyboard_text[2],keyboard_text[3],keyboard_text[4],keyboard_text[5],keyboard_text[6],keyboard_text[7],keyboard_text[8],game_info[1], game_info[0], game_info[3], game_info[2])
                                else:
                                    game_message = "🍍 *Игра закончилась!*\n\n%s | %s | %s\n%s | %s | %s\n%s | %s | %s\n\nУчастники:\n❌ [%s](tg://user?id=%s)\n⭕ [%s](tg://user?id=%s) - Не сделал(-а) ход" % (keyboard_text[0],keyboard_text[1],keyboard_text[2],keyboard_text[3],keyboard_text[4],keyboard_text[5],keyboard_text[6],keyboard_text[7],keyboard_text[8],game_info[1], game_info[0], game_info[3], game_info[2])
                                keyboard = None
                                await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=message, parse_mode="Markdown",reply_markup=keyboard)
                        except FileNotFoundError:
                            return False

                return await bot.answer_callback_query(callback_query_id=callback_query.id, text="🍍 Вы не можете ходить!", show_alert=True)
            except FileNotFoundError:
                return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="🍍 *Игра удалена...*", parse_mode="Markdown",reply_markup=keyboard)
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
    except Exception as e:
        print(repr(e)) 

if __name__ == '__main__':
    try:
        if not os.path.isdir("chats"):
            os.mkdir("chats")

        executor.start_polling(dp, skip_updates=False)
    except Exception as e:
        print(repr(e))
