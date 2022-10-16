TelegramBot_Market


This is Telegram bot written in Python using built-in libraries and aiogram.
Performs the functions of a mini store with its own database.

Customers can view the store menu, make an order and pay for the goods right inside the Telegram.
Each paid order is saved in the orders table of the database.
Administrators can add and delete products from the database, change the work schedule and the list of store addresses.



How to start using the bot:
    Go to the config.py file.
    Opposite the line with comments in the form:
        # <-------- *TEXT
    Insert the appropriate values.
    Save the changes and run start.bat.
    The bot has open source code, so you can always edit it to suit your needs.



The logic of the bot:
    The start.bat file launches main.py - the main program file.
    The main.py imports the admin and client modules from directory handlers, calls the admin_register and client_register commands, which are passed an instance of the Dispatcher class.
    The functions catch all messages sent to the bot in private or in groups where it exists.
    Caught commands are redirected to the appropriate functions.
    If a message or command is not in the list of registered ones, it is ignored.