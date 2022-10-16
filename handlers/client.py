from aiogram.types import Message, ShippingQuery, LabeledPrice, PreCheckoutQuery, InlineKeyboardButton,\
    InlineKeyboardMarkup, CallbackQuery
from aiogram.types.message import ContentType
from aiogram import Dispatcher
from config import bot, bot_name, payment_token, currency, cities_of_UA, client_keyboard, \
    self_delivery, delivery_glovo, delivery_rocket, check
import sqlite3





async def start(message: Message) -> None:

    """ Sends a message about the bot, what it can do, what commands it has.
    Set the built-in keyboard client commands """

    async def func():
        await message.answer('О, привіт!\nМи там якась піцерія.\n\n\
Щоб замовити піцу тицяй кнопку меню, обирай улюблену піцу і \
замовляй її прямо в Телеграмі!\n\n\n', reply_markup=client_keyboard)

        await message.answer('Щоб побачити увесь список команд бота для користувача введи команду /commands_client\n\n\
А команда /commands_admin покаже тобі список команд адміністратора')

    await check(func)


async def commands_client(message: Message) -> None:
    async def func():
        await message.answer('/start - повертає це повідомлення\n\n\
    /help - повертає повідомлення з найчастішими запитаннями та відповідями на них\n\n\
    /menu - виводить список усіх товарів магазину\n\n\
    /locate - повертає список адрес відділень магазину\n\n\
    /worktime - повертає робочі часи магазину\n\n\n')
    
    await check(func)


async def commands_admin(message: Message) -> None:
    async def func():
        await message.answer('/add - використовуйте цю команду, щоб додати новий товар до меню\n\n\
/isAdmin - встановлює клавіатуру адміністратора, якщо ви адміністратор; дозволяє дізнатися чи є ви адміном \n\n\
/delete - виводить меню магазину, під кожним товаром буде кнопка Видалити, при натисканні на неї цей товар буде видалено з бази даних \n\n\
/changeWorkTime - використовуйте цю команду, щоб  змінити повідомлення, що буде виводитися при виклику команди /worktime\n\n\
/changePlaces - використовуйте цю команду, щоб  змінити повідомлення, що буде виводитися при виклику команди /locate\n\n\
/cancel - використовуйте цю команду, щоб відмінити початі зміни.\n\n\
*Не працює якщо адміністратор вже зберіг зміни*'.format(bot_name), reply_markup=client_keyboard)
    await check(func)


async def help(message: Message) -> None:

    """ Sends a message with the most frequent questions and answers """

    await check(await message.answer("""Як мені купити товар?\n\n\
Використайте команду /menu\n\
Оберіть товар\n\
Натисніть на кнопку "Купити" під ним\n\
У відповідь бот надішле інвойс (рахунок для оплати), натисніть на кнопку "Pay" під інвойсом\n\
У вікні, що з'явиться заповните необхідні дані (ім'я покупця, емейл, адресу доставки, спосіб доставки, спосіб оплати)\n\
Після натисніть кнопку "Сплатити"\n\
При успішній операції з'явиться системне повідомлення, а бот подякує вам за покупку\n\n\n\
Як скасувати моє замовлення?\n\n\
Якщо ви ще не сплатили за товар в інвойсі, не переймайтеся. Гроші з вашої картки не списані.\n\n\
Якщо ви вже замовили товар, але вирішили скасувати, напишіть адміністратору магазину. Він перевіріть \
вашу особистіть (чи та ви людина, що замовила товар), скасує замовлення і поверне вам гроші. \
Тому вказуйте ваші реальні ім'я та адресу електронної пошти."""))


async def bot_info(message: Message) -> None:

    """ Sends a message with information about the bot """

    await check(await message.answer('Коротко про бота:\n\
{0} сконструйований як міні магазин зі своєю базою даних.\n\
Клієнти можуть переглянути меню магазину, зробити замовлення і оплатити товар прямо всередині Телеграма.\n\
Кожне оплачене замовлення зберігається в таблицю замовлень бази даних.\n\
Адміністратори можуть додавати і видаляти товари з бази даних, змінювати графік роботи і список адрес магазину.'.format(bot_name)))


async def locate(message: Message) -> None:

    """ Sends a message with a list of store addresses """

    async def func():
        with open('Database/places_file.txt', 'r', encoding='utf-8') as file:
            await message.answer(file.read())
    
    await check(func)


async def work_time(message: Message) -> None:

    """ Send a message with the store's opening hours """

    async def func():
        with open('Database/work_time_file.txt', 'r', encoding='utf-8') as file:
            await message.answer(file.read())
    
    await check(func)





async def menu(message: Message) -> None:

    """ Displays the store menu
    
    Selects all product records from a table in the database.
    Each entry is formatted and sends a message with an inline button to buy.
    The button sends a callback request """
    
    async def func():
        base = sqlite3.connect('Database/my_database.db')
        cur = base.cursor()
        data = cur.execute('SELECT * FROM goods')
        if data:
            for item in data:
                await message.answer_photo(
                    photo= item[2],
                    caption= '<b>{0}</b>\nID товару: {1}\n\n{2}\n\nЦіна: {3} {4}'.format(item[1], str(item[0]), item[3], str(item[4] / 100), currency),
                    reply_markup= InlineKeyboardMarkup(1)\
                        .add(InlineKeyboardButton('Купити', callback_data='buy_{0}'.format(str(item[0]))))
                )
        else:
            await message.answer('Наразі у меню немає товарів :(')

        base.close()
    
    await check(func)


async def order(callback: CallbackQuery) -> None:

    """ Making a purchase
    
    Step 1:
    Catches the callback request and sends an invoice (purchase message) of the selected item in response """

    async def func():
        base = sqlite3.connect('Database/my_database.db')
        cur = base.cursor()
        good = list(cur.execute('SELECT * FROM goods WHERE goods_id == ?', (callback.data[4:],)))
        await bot.send_invoice(callback.message.chat.id,
            title= good[0][1],
            description= good[0][3],
            provider_token= payment_token,
            currency= currency,
            photo_url= good[0][2],
            photo_height= 512,
            photo_size= 512,
            photo_width= 512,
            need_name= True,
            need_email= True,
            need_shipping_address= True,
            is_flexible= True,
            prices= [LabeledPrice('Товар', int(good[0][4]))],
            payload= good[0][0])
        base.close()

    await check(func)


async def ship(shipping: ShippingQuery) -> None:

    """ Making a purchase

    Step 2:

    Checks the shipping address on the invoice.
    Sends possible ways of delivery for this address.
    
    *** If the delivery address is not in Ukraine, an error message appears.
    At delivery to Ukraine, the usual delivery is added.
    When delivering to big cities of Ukraine (cities_of_UA) - fast delivery is added.
    If the delivery address is in Zaporozhya, Ukraine, is added Pickup.***
    
    """

    async def func():
        if shipping.shipping_address.country_code != 'UA':
            return await bot.answer_shipping_query(shipping.id, ok=False, error_message='Доставка тільки по Україні')
        
        shippingoption = [delivery_rocket]

        if shipping.shipping_address.city in cities_of_UA:
            shippingoption.append(delivery_glovo)
            if shipping.shipping_address.city == 'Запоріжжя':
                shippingoption.append(self_delivery)

        await bot.answer_shipping_query(shipping.id, ok=True, shipping_options=shippingoption)
    
    await check(func)


async def pre_checkout(prechekout: PreCheckoutQuery) -> None:

    """ Payment verification """

    await check(await bot.answer_pre_checkout_query(prechekout.id, ok=True))


async def sucsses(message: Message) -> None:

    """ Catches messages of type SUCCESSFUL_PAYMENT
    Adds the order to the database.
    Sends the message "Thank you for your purchase!" """

    async def func():
        base = sqlite3.connect('Database/my_database.db')
        cur = base.cursor()
        cur.execute('INSERT INTO orders (name, \
                                        email, \
                                        product_id, \
                                        country_code, \
                                        state, \
                                        city, \
                                        street_line1, \
                                        street_line2, \
                                        post_code, \
                                        delivery, \
                                        date, \
                                        price, \
                                        currency) \
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        message['successful_payment']['order_info']['name'],
                        message['successful_payment']['order_info']['email'],
                        message['successful_payment']['invoice_payload'],
                        message['successful_payment']['order_info']['shipping_address']['country_code'],
                        message['successful_payment']['order_info']['shipping_address']['state'],
                        message['successful_payment']['order_info']['shipping_address']['city'],
                        message['successful_payment']['order_info']['shipping_address']['street_line1'],
                        message['successful_payment']['order_info']['shipping_address']['street_line2'],
                        message['successful_payment']['order_info']['shipping_address']['post_code'],
                        message['successful_payment']['shipping_option_id'],
                        message['date'],
                        message['successful_payment']['total_amount'] / 100,
                        message['successful_payment']['currency'],
                    ))
        base.commit()
        base.close()
        await message.answer('Дякуємо за покупку!')
    
    await check(func)





def client_register(dp: Dispatcher) -> None:
    dp.register_message_handler(start, commands=['start'])

    dp.register_message_handler(commands_client, commands=['commands_client'])

    dp.register_message_handler(commands_admin, commands=['commands_admin'])

    dp.register_message_handler(help, commands=['help'])

    dp.register_message_handler(locate, commands=['locate'])

    dp.register_message_handler(work_time, commands=['worktime'])

    dp.register_message_handler(menu, commands=['menu'])

    dp.register_callback_query_handler(order, lambda x: x['data'][:4] == 'buy_')
    dp.register_shipping_query_handler(ship)
    dp.register_pre_checkout_query_handler(pre_checkout)
    dp.register_message_handler(sucsses, content_types=ContentType.SUCCESSFUL_PAYMENT)
