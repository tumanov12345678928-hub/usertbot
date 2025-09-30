from pyrogram import Client, filters
import asyncio
import logging
from pyrogram.types import Message  # Добавь этот импорт
from pyrogram.enums import ParseMode  # Добавляем импорт ParseMode
from pyrogram.errors import PeerIdInvalid, UsernameInvalid, UsernameNotOccupied, ChannelPrivate, ChatAdminRequired
import sqlite3
import time
import random
import string
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import ChatPermissions

# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client(
    "Osnova",
    api_id=21592124,
    api_hash="c2100f2a2c6beb6af0a98830509f371a",
    test_mode=True,
    plugins=dict(root="plugins")
)





GIFT_IDS = {
    "happy": 5415904913592942593,
    "monkey": 5454418585415843841,
    "love": 5453972608896729089,
    "clown": 5454079300179329025
}

# Глобальная переменная для остановки
is_sending_active = False
is_private = True


async def send_gifts(client, message, gift_type, target, count, ):
    global is_sending_active
    is_sending_active = True
    is_private = True

    try:
        gift_id = GIFT_IDS[gift_type]

        for _ in range(count):
            if not is_sending_active:
                break
            await client.send_gift(chat_id=target.id, gift_id=gift_id)

        await message.reply(f"✅ Готово!") if is_sending_active else None

    except Exception as e:
        await message.reply(f"❌ Ошибка: {str(e)}")
    finally:
        is_sending_active = False




@app.on_message(filters.command("nongift", prefixes=".") & filters.me)
async def stop_sending(client, message):
    global is_sending_active
    is_sending_active = False
    await message.reply("⏹️ Рассылка остановлена")


@app.on_message(filters.command("happy", prefixes=".") & filters.me)
async def happy_gift(client, message):
    await handle_gift_command(client, message, "happy")


@app.on_message(filters.command("monkey", prefixes=".") & filters.me)
async def monkey_gift(client, message):
    await handle_gift_command(client, message, "monkey")


@app.on_message(filters.command("love", prefixes=".") & filters.me)
async def love_gift(client, message):
    await handle_gift_command(client, message, "love")


@app.on_message(filters.command("clown", prefixes=".") & filters.me)
async def clown_gift(client, message):
    await handle_gift_command(client, message, "clown")


async def handle_gift_command(client, message, gift_type):
    global is_sending_active

    if is_sending_active:
        return await message.reply("⚠️ Дождитесь завершения текущей рассылки")

    args = message.text.split()
    if len(args) < 3:
        return await message.reply(f"❌ Формат: .{gift_type} @username количество")

    try:
        target = await client.get_chat(args[1].strip("@"))
        count = min(int(args[2]), 100000)
        await send_gifts(client, message, gift_type, target, count)
    except Exception as e:
        await message.reply(f"❌ Ошибка: {str(e)}")


@app.on_message(filters.command("inf", prefixes=".") & (filters.group | filters.channel))  # В группах/каналах
async def get_group_info(client: Client, message: Message):
    chat = message.chat
    await message.reply_text(
        f"**📌 Информация о чате:**\n"
        f"**ID:** `{chat.id}`\n"
        f"**Тип:** `{'Группа' if chat.type == 'group' else 'Супергруппа' if chat.type == 'supergroup' else 'Канал'}`\n"
        f"**Название:** `{chat.title}`\n"
        f"**Username:** @{chat.username if chat.username else 'нет'}\n"
        f"**Всего участников:** `{chat.members_count if hasattr(chat, 'members_count') else 'N/A'}`"
    )

@app.on_message(filters.command("transfer", ".") & filters.me)
async def transfer_gifts(client, message):
    try:
        if len(message.command) < 3:
            await message.edit("❌ Неверный формат!\nИспользуйте: <code>.transfer юзернейм количество</code>")
            return

        username = message.command[1].lstrip("@")
        try:
            amount = int(message.command[2])
            if amount <= 0:
                await message.edit("❌ Количество должно быть положительным числом!")
                return
        except ValueError:
            await message.edit("❌ Укажите корректное количество подарков!")
            return

        await message.edit(f"🔄 Начинаю передачу {amount} подарков пользователю @{username}...")

        transferred = 0
        errors = 0
        async for gift in client.get_chat_gifts("me"):
            if transferred >= amount:
                break

            try:
                result = await gift.transfer(username)
                transferred += 1
            except Exception as e:
                errors += 1
                print(f"Ошибка при передаче подарка: {e}")
                continue

        report = (
            f"📊 Отчет о передаче подарков:\n\n"
            f"• Запрошено: {amount}\n"
            f"• Передано: {transferred}\n"
            f"• Ошибок: {errors}\n"
            f"• Получатель: @{username}"
        )

        await message.edit(report)

    except Exception as ex:
        await message.edit(f"⚠️ Произошла ошибка: {ex}")
        print(f"Ошибка в команде transfer: {ex}")


@app.on_message(filters.command("ban", prefixes=".") & filters.me)
async def ban_cmd(client, message):
    if not message.reply_to_message:
        await message.edit("<b>❌ Ответьте на сообщение пользователя</b>")
        return

    try:
        await client.ban_chat_member(
            chat_id=message.chat.id,
            user_id=message.reply_to_message.from_user.id
        )
        await message.edit("<b>✅ Пользователь забанен</b>")
    except Exception as e:
        await message.edit(f"<b>❌ Ошибка: {e}</b>")






@app.on_message(filters.command("info", prefixes=".") & filters.me)
async def info_cmd(client, message):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        target = message.from_user

    text = f"""
<b>👤 Информация:</b>
ID: <code>{target.id}</code>
Имя: {target.first_name}
Фамилия: {target.last_name or '❌'}
Юзернейм: @{target.username or '❌'}
Бот: {'✅' if target.is_bot else '❌'}
"""
    await message.edit(text, parse_mode=ParseMode.HTML)





@app.on_message(filters.command("broadcast", prefixes=".") & filters.me)
async def broadcast_cmd(client, message):
    if len(message.command) < 2:
        await message.edit("<b>❌ Укажите текст</b>")
        return

    text = " ".join(message.command[1:])
    count = 0
    async for dialog in client.get_dialogs():
        try:
            await client.send_message(dialog.chat.id, text)
            count += 1
            await asyncio.sleep(0.1)  # Антифлуд
        except:
            continue

    await message.edit(f"<b>✅ Разослано в {count} чатов</b>")


@app.on_message(filters.command("ban", prefixes=".") & filters.me)
async def ban_cmd(client, message):
    if not message.reply_to_message:
        await message.edit("<b>❌ Ответьте на сообщение пользователя</b>")
        return

    try:
        await client.ban_chat_member(
            chat_id=message.chat.id,
            user_id=message.reply_to_message.from_user.id
        )
        await message.edit("<b>✅ Пользователь забанен</b>")
    except Exception as e:
        await message.edit(f"<b>❌ Ошибка: {e}</b>")


@app.on_message(filters.command("join", prefixes=".") & filters.me)
async def join_cmd(client, message):
    if len(message.command) < 2:
        await message.edit("<b>❌ Укажите username чата</b>", parse_mode=ParseMode.HTML)
        return

    username = message.command[1]
    try:
        chat = await client.join_chat(username)
        await message.edit(f"<b>✅ Успешно вступил в {chat.title}</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.edit(f"<b>❌ Ошибка: {e}</b>", parse_mode=ParseMode.HTML)

# Обработчик команды .spam
@app.on_message(filters.command("spam", prefixes=".") & filters.me)
async def spam_command(client: Client, message: Message):
    try:
        logger.info(f"Получена команда: {message.text}")

        # Удаляем команду
        try:
            await message.delete()
        except Exception as del_err:
            logger.error(f"Не удалось удалить сообщение: {del_err}")

        # Разбиваем аргументы
        args = message.text.split(maxsplit=3)  # .spam 5 1.0 Текст...

        if len(args) < 4:
            logger.error("Не хватает аргументов! Нужно: .spam [кол-во] [задержка] [текст]")
            await client.send_message(message.chat.id, "❌ **Формат:** `.spam [кол-во] [задержка] [текст]`")
            return

        # Парсим аргументы
        try:
            count = int(args[1])
            delay = float(args[2])
            text = args[3]
        except (ValueError, IndexError) as e:
            logger.error(f"Ошибка в аргументах: {e}")
            await client.send_message(message.chat.id,
                                      f"⚠️ **Ошибка:** Неправильные аргументы\nПример: `.spam 5 1.0 Привет`")
            return

        if count <= 0 or delay < 0:
            logger.error(f"Некорректные значения: count={count}, delay={delay}")
            await client.send_message(message.chat.id, "⚠️ **Ошибка:** Кол-во > 0, задержка ≥ 0")
            return

        # Проверяем, является ли чат комментарием (reply в группе/канале)
        if message.reply_to_message:
            target_chat_id = message.chat.id
            reply_to_msg_id = message.reply_to_message.id  # Ответ на конкретное сообщение
            logger.info(f"Отправка в комментарии (reply_to_msg_id={reply_to_msg_id})")
        else:
            target_chat_id = message.chat.id
            reply_to_msg_id = None  # Обычное сообщение
            logger.info("Отправка в обычный чат")

        # Отправка сообщений
        logger.info(f"Старт спама: {count} сообщений с задержкой {delay} сек")
        for i in range(count):
            try:
                await client.send_message(
                    chat_id=target_chat_id,
                    text=text,
                    reply_to_message_id=reply_to_msg_id  # Если есть reply, прикрепляем к нему
                )
                logger.info(f"Отправлено сообщение {i + 1}/{count} (chat_id={target_chat_id})")
                if i < count - 1:
                    await asyncio.sleep(delay)
            except Exception as send_err:
                logger.error(f"Ошибка при отправке: {send_err}")
                break

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        await client.send_message(message.chat.id, f"⚠️ **Ошибка:** `{e}`")








@app.on_message(filters.command("stopspam", prefixes=".") & filters.me)
async def stop_spam(client, message):
    global spam_active
    spam_active = False
    await message.edit("<b>🛑 Спам остановлен</b>", parse_mode=ParseMode.HTML)
    
    
@app.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_cmd(client, message):
    start = time.time()
    msg = await message.reply("🏓")
    end = time.time()
    await msg.edit(f"🏓 Pong! Время отклика: <b>{round(end - start, 3)} сек</b>", parse_mode=ParseMode.HTML)
   
    
      
    
@app.on_message(filters.command("clean", prefixes=".") & filters.me)
async def clean_messages(client, message):
    try:
        count = int(message.command[1])
        messages = [msg.id async for msg in client.get_chat_history(message.chat.id, limit=count + 1)]
        await client.delete_messages(message.chat.id, messages)
    except:
        await message.edit("❌ Укажи количество сообщений для удаления")
    
    
    
    
    
@app.on_message(filters.command("raid", prefixes=".") & filters.me)
async def raid_mode(client, message):
    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.edit("❌ Формат: `.raid [кол-во] [задержка] [текст]`")
        return

    try:
        count = int(args[1])
        delay = float(args[2])
        text = args[3]
    except:
        await message.edit("⚠️ Ошибка в аргументах")
        return

    await message.delete()
    previous_msg = await client.send_message(message.chat.id, text)
    for i in range(1, count):
        await asyncio.sleep(delay)
        previous_msg = await client.send_message(
            message.chat.id,
            text,
            reply_to_message_id=previous_msg.id
        )


@app.on_message(filters.command("hack", prefixes=".") & filters.me)
async def hack_cmd(client, message):
    if len(message.command) < 2:
        await message.edit("❌ Укажи кого взламывать\nПример: `.hack @clown`")
        return

    target = message.command[1]
    steps = [
        f"🔍 Поиск уязвимостей {target}...",
        "🧬 Взлом облака Google Drive...",
        "💉 Инъекция вируса Trojan.RAT...",
        "📡 Установка backdoor...",
        "🛢️ Слив логов Telegram Web...",
        "📂 Доступ к перепискам получен...",
        "💾 Скачивание nudes.zip...",
        "📤 Отправка файлов на сервер ФСБ...",
        "☠️ Взлом завершён. Жертва уничтожена.",
        f"✅ {target} теперь под контролем Вас и FemBoySpam."
    ]

    sent = await message.edit(f"🧠 Начинаю взлом {target}...")
    for step in steps:
        await asyncio.sleep(random.uniform(0.7, 1.5))
        try:
            await sent.edit(step)
        except:
            break
        

        
    
@app.on_message(filters.command("whois", prefixes=".") & filters.me)
async def whois_cmd(client, message):
    if not message.reply_to_message:
        await message.edit("❌ Ответь на сообщение пользователя")
        return

    user = message.reply_to_message.from_user
    text = f"""
<b>🕵️ Кто это:</b>
Имя: {user.first_name}
Фамилия: {user.last_name or '❌'}
Юзернейм: @{user.username or '❌'}
ID: <code>{user.id}</code>
Бот: {'✅' if user.is_bot else '❌'}
"""
    await message.edit(text, parse_mode=ParseMode.HTML)
    
    
    
    
    
@app.on_message(filters.command("multiraid", prefixes=".") & filters.me)
async def multiraid_cmd(client, message):
    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.edit("❌ Формат: `.multiraid [кол-во] [задержка] [фраза1;фраза2;...]`")
        return

    try:
        count = int(args[1])
        delay = float(args[2])
        phrases = args[3].split(";")
    except:
        await message.edit("⚠️ Ошибка в аргументах")
        return

    await message.delete()
    previous = await client.send_message(message.chat.id, random.choice(phrases))
    for i in range(1, count):
        await asyncio.sleep(delay)
        text = random.choice(phrases)
        try:
            previous = await client.send_message(
                message.chat.id,
                text,
                reply_to_message_id=previous.id
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"❌ Ошибка: {e}")
            break
            
            
@app.on_message(filters.command("glitch", prefixes=".") & filters.me)
async def glitch_text(client, message):
    if len(message.command) < 2:
        await message.edit("❌ Введи текст")
        return

    text = " ".join(message.command[1:])
    glitchy = ''.join(c + random.choice(['̷','͟','͢','͜','̸','͞']) for c in text)
    await message.edit(f"👾 {glitchy}")
    
    
    
    
@app.on_message(filters.command("roll", prefixes=".") & filters.me)
async def roll_cmd(client, message):
    number = random.randint(1, 6)
    await message.edit(f"🎲 Выпало: <b>{number}</b>", parse_mode=ParseMode.HTML)
    
   
    
      
@app.on_message(filters.command("nudescan", prefixes=".") & filters.me)
async def nude_scan(client, message):
    if len(message.command) < 2:
        await message.edit("❌ Формат: `.nudescan @юзернейм`")
        return

    user = message.command[1]
    await message.edit(f"🔍 Сканирую память устройства {user} на наличие nudes...")
    await asyncio.sleep(2)
    await message.edit("💾 Файлы обнаружены: `nude1.png`, `cam2.mp4`, `leak.zip`\n📤 Отправка в чат запрещена политикой Telegram.")
    
   
    
      
@app.on_message(filters.command("ip", prefixes=".") & filters.me)
async def fake_ip_scan(client, message):
    if len(message.command) < 2:
        await message.edit("❌ Формат: `.ip @юзернейм`")
        return

    username = message.command[1]
    fake_ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
    await message.edit(f"🔍 Сканирую IP {username}...")
    await asyncio.sleep(1.5)
    await message.edit(f"📡 IP-адрес {username}: `{fake_ip}`\n🌐 Местоположение: Россия, Москва (приблизительно)")




@app.on_message(filters.command("lastseen", prefixes=".") & filters.me)
async def last_seen(client, message):
    if len(message.command) < 2:
        return await message.edit("❌ Укажи @юзернейм")
    try:
        user = await client.get_users(message.command[1])
        if user.status and hasattr(user.status, 'was_online'):
            seen = user.status.was_online.strftime('%Y-%m-%d %H:%M:%S')
            await message.edit(f"👀 Последний раз в сети: <code>{seen}</code>", parse_mode=ParseMode.HTML)
        else:
            await message.edit("⛔ Скрыто или оффлайн")
    except Exception as e:
        await message.edit(f"❌ Ошибка: {e}")
        
        
        
        
@app.on_message(filters.command("tagall", prefixes=".") & filters.me & filters.group)
async def tagall(client, message):
    text = ""
    async for member in client.get_chat_members(message.chat.id, limit=30):
        if member.user.is_bot:
            continue
        mention = f"@{member.user.username}" if member.user.username else f"<a href='tg://user?id={member.user.id}'>user</a>"
        text += mention + " "
    await message.reply(text, parse_mode=ParseMode.HTML)
    
    
    
    
@app.on_message(filters.command("menu", prefixes=".") & filters.me)
async def menu(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Создатель", url="kotenochek.t.me")],
        [InlineKeyboardButton("🔥 Канал", url="newxatafan4iik.t.me")],
        [InlineKeyboardButton("😂 Мем", url="nope")]
    ])
    await message.reply("📋 Меню:", reply_markup=keyboard)


HELP_TEXT = """
<b>📜 Список команд FemBoySpam:</b>
                    ОБЫЧНЫЕ КОМАНДЫ
<code>.help</code> - Показать Команды
<code>.join @username</code> - Вступить в чат
<code>.spam [кол-во] [задержка] [текст]</code> - Отправить сообщения N раз с задержкой
<code>.stopspam</code> - Остановить спам
<code>.broadcast</code> - Рассылка всем диалогам
<code>.info</code> - Информация о чате/пользователе
<code>.transfer [юзернейм] [кол-во]</code> - Передача кому-то какое-то количество нфт тортов


                    НОВЫЕ КОМАНДЫ
<code>.ping</code> - Узнать свой пинг
<code>.whois</code> -  Информация о человеке
<code>.clean</code> - Очистка чата
<code>.glitch</code> - Ебанный текст
<code>.roll</code> - Число от 1 до 6
<code>.menu</code> - Меню
<code>.tagall</code> - Тегнуть всех xD
<code>.lastseen</code> - Последний заход челов


                    ПОЛНЫЙ ПИЗ... 
<code>.raid</code> - Спам рейд 😈
<code>.hack</code> - Взлом лошков😈
<code>.multiraid</code> - Спам Рейд разными словами (пример: .multiraid 10 0.4 клоун;иди спать;пук;лол)😈
<code>.ip</code> - Поиск айпи адреса😈
<code>.nudescan</code> - Поиск нюдсов 😈


                СПАМ ПОДАРКАМИ
<code>.happy [юзернейм] [кол-во]</code> - 🎉
<code>.monkey [юзернейм] [кол-во]</code>- 🦧
<code>.love [юзернейм] [кол-во]</code>- ❤️
<code>.clown [юзернейм] [кол-во]</code>- 🤡
<code>.nongift</code> - Остановка спама

"""




@app.on_message(filters.command("help", prefixes=".") & filters.me)
async def help_cmd(client, message):
    await message.edit(HELP_TEXT, parse_mode=ParseMode.HTML)


app.run()