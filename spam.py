from telethon import TelegramClient, events
import asyncio
import time

api_id = 2040
api_hash = 'b18441a1ff607e10a989891a5462e627'
phone_number = '+ваш номер'

client = TelegramClient(phone_number, api_id, api_hash)
client.session.set_dc(2, '149.154.167.40', 443)

async def main():
    await client.start(phone=phone_number)
    print("Успешно вошли в аккаунт!")

    me = await client.get_me()
    my_id = me.id

    @client.on(events.NewMessage(pattern='спам'))
    async def spam_handler(event):
        if event.sender_id != my_id:
            return

        parts = event.message.message.split(' ', 2)
        if len(parts) != 3:
            await event.reply("Неверный формат. Используйте: спам (число сообщений) (сообщение)")
            return

        try:
            num_messages = int(parts[1])
            message = parts[2]
        except ValueError:
            await event.reply("Неверный формат числа сообщений.")
            return

        if event.chat:
            chat_identifier = event.chat.username if hasattr(event.chat, 'username') and event.chat.username else str(event.chat_id)
        else:
            chat_identifier = event.sender.username if event.sender and hasattr(event.sender, 'username') and event.sender.username else str(event.chat_id)

        start_time = time.time()

        await event.reply(f"Спам в чат {chat_identifier} начат")

        tasks = [client.send_message(event.chat_id, message) for _ in range(num_messages)]
        await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed_time = end_time - start_time

        await event.reply(f"Спам в чат {chat_identifier} окончен.\nВремя: {elapsed_time:.2f} секунд")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
