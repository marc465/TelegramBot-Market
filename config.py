from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ShippingOption, LabeledPrice
import logging


logging.basicConfig(filename='logs/log_file.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s')

storage = MemoryStorage()
token = ''    # <-------- Here insert the regular bot token obtained from @BotFather


payment_token = ''  # <-------- Insert payment token obtained from @BotFather here
currency = ''    # <-------- Here write the currency in which you sell


admins_id = ()    # <-------- Insert here the IDs of users who will have access to admin functions (IDs can be obtained from @getmyid_bot)
admin_keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
admin_keyboard.row(KeyboardButton('/delete'), KeyboardButton('/add'))\
    .row(KeyboardButton('/changePlaces'), KeyboardButton('/changeWorktime'))\
    .add(KeyboardButton('/clientKeyboard'))


client_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
client_keyboard.add(KeyboardButton('/locate')).add(KeyboardButton('/menu')).add(KeyboardButton('/worktime'))


# Below is a code block with shipping options, if you want to change the shipping methods or their prices, edit it

delivery_rocket = ShippingOption(
    'rocket',
    'Сервис Rocket').add(LabeledPrice('Звичайна доставка', 2600))


delivery_glovo = ShippingOption(
    'glovo',
    'Сервис Glovo').add(LabeledPrice('Швидка доставка', 5700))


self_delivery = ShippingOption(
    'self_delivery',
    'Самовивіз').add(LabeledPrice('Самовивіз', 000))


cities_of_UA = (
    'Івано-Франківськ','Тернопіль','Львів','Житомир','Вінниця',
    'Київ','Чернігів','Суми','Полтава','Черкаси','Кіровоград',
    'Запоріжжя','Одеса','Миколаїв','Херсон','Харків','Дніпропетровськ'
)

# End of code block with delivery options

bot = Bot(token= token, parse_mode='html')
dp = Dispatcher(bot, storage=storage)
bot_name = '@' + ''   # <-------- Here insert the name of your bot


async def check(func):

    """ Wraps each passed function in try-except blocks.
    The result of the error is written to the logging file """

    try:
        await func()
    except Exception as e:
        logging.error(e)
        logging.exception(e)
