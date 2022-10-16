from config import dp
from aiogram.utils import executor
from handlers import admin, client


client.client_register(dp)
admin.admin_register(dp)


executor.start_polling(dp, skip_updates=True)
