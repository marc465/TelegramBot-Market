from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from config import client_keyboard, currency, admins_id, admin_keyboard, check
import sqlite3





class update_menu(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()


class change_worktime(StatesGroup):
    new_work_time = State()


class change_places(StatesGroup):
    new_places = State()





async def is_admin(message: Message) -> None:
    async def func():
        if message.from_user.id in admins_id:
            await message.answer('Ви адмін')
            await message.answer('Встановлена клавіатура адміністратора', reply_markup=admin_keyboard)

        else:
            await message.answer('Ви не адмін')

    await check(func)


async def switch_keyboard(message: Message)  -> None:
    async def func():
        if message.from_user.id in admins_id:
            await message.answer('Встановлена клавіатура користувача', reply_markup=client_keyboard)
    await check(func)


async def cancel(message: Message, state: FSMContext)  -> None:
    async def func():
        if await state.get_state() is None:
            return
        await state.finish()
        await message.answer('Скасовано')
    await check(func)





async def add_product_start(message: Message) -> None:

    """ Adding a record to the database

    Step 1:
    Checks if the user is an admin.
    Enters the bot into a machine state.
    Requests a photo. """

    async def func():
        if message.from_user.id in admins_id:
            await update_menu.photo.set()
            await message.answer('Починаю додавати новий продукт у меню\n\nЯкщо ви передумаєте додавати товар, використовуйте команду /cancel для скасування')
            await message.answer('Надішліть URL фото продукту')
    
    await check(func)


async def load_photo(message: Message, state: FSMContext) -> None:

    """ Adding a record to the database

    Step 2:
    Catches a photo of a product, saves its id to the dictionary.
    Queries the name. """

    async def func():
        async with state.proxy() as data:
            data['photo'] = message.text
        await update_menu.next()
        await message.answer('Напишіть назву')
    
    await check(func)


async def load_name(message: Message, state: FSMContext) -> None:

    """ Adding a record to the database

    Step 3:
    Catches the product name, stores it in the dictionary.
    Requests a description. """

    async def func():
        async with state.proxy() as data:
            data['name'] = message.text
        await update_menu.next()
        await message.answer('Напшіть опис')
    
    await check(func)


async def load_description(message: Message, state: FSMContext) -> None:

    """ Adding a record to the database

    Step 4:
    Catches the product description, stores it in the dictionary.
    Queries the price. """

    async def func():
        async with state.proxy() as data:
            data['description'] = message.text
        await update_menu.next()
        await message.answer('Напишіть ціну товару в найменших одиницях валюти\nНаприклад, товар цінною 14,72 потрібно записати як 1472')
    
    await check(func)


async def load_price(message: Message, state: FSMContext) -> None:

    """ Adding a record to the database

    Step 5:
    Catches the price of the product, saves it to the dictionary.
    Adds the result to the database.
    Deletes the dictionary.
    Reports a successful operation. """ 

    try:
        async with state.proxy() as data:
            base = sqlite3.connect('Database/my_database.db')
            cur = base.cursor()
            cur.execute('INSERT INTO goods (name, photo, description, price) VALUES (?, ?, ?, ?)', 
                        (data['name'],
                        data['photo'],
                        data['description'],
                        int(message.text)))
            base.commit()
            base.close()

        await state.finish()
        await message.answer('Товар добавлено')
    except:
        await state.finish()
        await message.answer('Сталася помилка під час додавання товару')





async def delete_product_from_db_step_1(message: Message) -> None:

    """ Deleting a record from the database

    Step 1:
    Checks if the user is an admin.
    Outputs all records from the database goods table (as a menu client function).
    Under each message is an inline Delete button.
    The button sends a callback request to delete the item from the database. """

    async def func():
        if message.from_user.id in admins_id:
            base = sqlite3.connect('Database/my_database.db')
            cur = base.cursor()
            data = list(cur.execute('SELECT * FROM goods'))
            if data:
                for item in data:
                    await message.answer_photo(
                        photo= item[2],
                        caption= '<b>{0}</b>\nID товару: {1}\n\n{2}\n\nЦіна: {3} {4}'.format(item[1], str(item[0]), item[3], str(item[4] / 100), currency),
                        reply_markup= InlineKeyboardMarkup(1).add(InlineKeyboardButton('Видалити', callback_data='del_{0}'.format(str(item[0]))))
                    )
            else:
                await message.answer('База даних пуста')

            base.close()

    await check(func)


async def delete_product_from_db_step_2(callback: CallbackQuery) -> None:

    """ Deleting a record from the database

    Step 2:
    Catches the callback to remove an item from the database.
    Checks if it is in the database.
    Deletes it if there is one.
    Reports success of the operation  """

    async def func():
        base = sqlite3.connect('Database/my_database.db')
        cur = base.cursor()
        if (int(callback.data[4:]),) in list(cur.execute('SELECT goods_id FROM goods')):
            cur.execute('DELETE FROM goods WHERE goods_id == ?', (callback.data[4:],))
            base.commit()
            await callback.answer('Товар видалено')
        else:
            await callback.answer('Товар вже видалено')

        base.close()
    
    await check(func)





async def change_work_time_step_1(message: Message) -> None:
    """ Changing the work schedule

    Step 1:
    Checks if the user is an admin.
    Displays the current work schedule.
    Requests a new work schedule. """

    async def func():
        if message.from_user.id in admins_id:
            with open('Database/work_time_file.txt', 'r', encoding='utf-8') as file:
                await change_worktime.new_work_time.set()
                await message.answer('Поточний графік роботи має такий вигляд:\n\n' + file.read())
                await message.answer('Щоб змінити, надішліть новий\n\nДля скасування використовуйте команду /cancel')
    
    await check(func)


async def change_work_time_step_2(message: Message, state: FSMContext) -> None:
    
    """ Changing the work schedule

    Step 2:
    Catches the new work schedule and writes it to a file.
    Reports a successful change. """ 

    async def func():
        with open('Database/work_time_file.txt', 'w', encoding='utf-8') as file:
            file.write(message.text)
        await state.finish()
        await message.answer('Графік роботи змінено')
    
    await check(func)





async def change_places_step_1(message: Message) -> None:

    """ Changing the address list

    Step 1:
    Checks if the user is an administrator.
    Sends the original address list.
    Requests a new one. """ 

    async def func():
        if message.from_user.id in admins_id:
            with open('Database/places_file.txt', 'r', encoding='utf-8') as file:
                await change_places.new_places.set()
                await message.answer('Поточний список адрес магазинів має такий вигляд:\n\n' + file.read())
                await message.answer('Щоб змінити, надішліть новий\n\nДля скасування використовуйте команду /cancel')
    
    await check(func)


async def change_places_step_2(message: Message, state: FSMContext) -> None:

    """ Changing the address list

    Step 2:
    Catches the new address list and writes it to a file.
    Reports a successful change. """ 

    async def func():
        with open('Database/places_file.txt', 'w', encoding='utf-8') as file:
            file.write(message.text)
        await state.finish()
        await message.answer('Список адрес магазинів змінено')
    await check(func)





def admin_register(dp: Dispatcher) -> None:
    dp.register_message_handler(is_admin, commands=['isAdmin'])

    dp.register_message_handler(switch_keyboard, commands=['clientKeyboard'])

    dp.register_message_handler(cancel, commands=['cancel'], state='*')

    dp.register_message_handler(add_product_start, commands=['add'])
    dp.register_message_handler(load_photo, state=update_menu.photo)
    dp.register_message_handler(load_name, state=update_menu.name)
    dp.register_message_handler(load_description, state=update_menu.description)
    dp.register_message_handler(load_price, state=update_menu.price)

    dp.register_message_handler(delete_product_from_db_step_1, commands=['delete'])
    dp.register_callback_query_handler(delete_product_from_db_step_2, lambda x: x['data'][:4] == 'del_')

    dp.register_message_handler(change_work_time_step_1, commands=['changeWorktime'])
    dp.register_message_handler(change_work_time_step_2, state=change_worktime.new_work_time)

    dp.register_message_handler(change_places_step_1, commands=['changePlaces'])
    dp.register_message_handler(change_places_step_2, state=change_places.new_places)
