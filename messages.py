import methods
from register import check, check_data_decorator
from database import Database
import globals
from telegram import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from collections import deque
db = Database("db-evos.db")

Load = None
@check_data_decorator
def message_handler(update, context):
    global Load
    message = update.message.text
    user = update.message.from_user
    state = context.user_data.get("state", 0)
    db_user = db.get_user_by_chat_id(user.id)
    his_sp = str(message).split(" ")
    history = deque(maxlen=3)
    def process_data(new_data):
        history.append(new_data)

    for data in his_sp:
        process_data(data)

    if state == 0:
        check(update, context)

    elif state == 1:
        if not db_user["lang_id"]:

            if message == globals.BTN_LANG_UZ:
                db.update_user_data(user.id, "lang_id", 1)
                check(update, context)

            elif message == globals.BTN_LANG_RU:
                db.update_user_data(user.id, "lang_id", 2)
                check(update, context)

            else:
                update.message.reply_text(
                    text=globals.TEXT_LANG_WARNING
                )

        elif not db_user["first_name"]:
            db.update_user_data(user.id, "first_name", message)
            check(update, context)

        elif not db_user["last_name"]:
            db.update_user_data(user.id, "last_name", message)
            buttons = [
                [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
            ]
            check(update, context)

        elif not db_user["phone_number"]:
            db.update_user_data(user.id, "phone_number", message)
            check(update, context)

        else:
            check(update, context)

################## lesson-4 ###################
    elif state == 2:
        if message == globals.BTN_ORDER[db_user['lang_id']]:
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

            if context.user_data.get("carts", {}):
                carts = context.user_data.get("carts")
                text = f"{globals.AT_KORZINKA[db_user['lang_id']]}:\n\n"
                lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                total_price = 0
                for cart, val in carts.items():
                    product = db.get_product_for_cart(int(cart))
                    text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
                    total_price += product['price'] * val

                text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price}"
                buttons.append(
                    [InlineKeyboardButton(text=globals.BTN_KORZINKA[db_user['lang_id']], callback_data="cart")])

            else:
                text = globals.TEXT_ORDER[db_user['lang_id']]
            update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons,
                )
            )

        elif message == globals.BTN_MY_ORDERS[db_user['lang_id']]:
            if context.user_data.get("carts", {}):
                carts = context.user_data.get("carts")
                text = "\n"
                lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                total_price = 0
                for cart, val in carts.items():
                    product = db.get_product_for_cart(int(cart))
                    text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
                    total_price += product['price'] * val
                text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price} {globals.SUM[db_user['lang_id']]}"

                update.message.reply_text(
                    text=f"<b>{globals.DATA[db_user['lang_id']]}:</b>\n\n"
                         f"👤 <b>{globals.NAME[db_user['lang_id']]}:</b> {db_user['first_name']} {db_user['last_name']}\n"
                         f"📞 <b>{globals.PHONE_NUMBER[db_user['lang_id']]}:</b> {db_user['phone_number']} \n\n"
                         f"📥 <b>{globals.ZAKAZ[db_user['lang_id']]}:</b> \n"
                         f"{text}",
                    parse_mode='HTML'
                )

            else:
                update.message.reply_text(
                    text=globals.NO_ZAKAZ[db_user['lang_id']])

        elif message == globals.BTN_ABOUT_US[db_user['lang_id']]:
            update.message.reply_text(
                text=globals.ABOUT_COMPANY[db_user['lang_id']],
                parse_mode="HTML"
            )

        elif message == globals.BTN_SETTINGS[db_user['lang_id']]:
            buttons = [
                [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)]
            ]
            update.message.reply_text(
                text=globals.CHOOSE_LANG,
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=buttons,
                    resize_keyboard=True
                )
            )
            context.user_data["state"] = globals.STATES["settings"]

        elif message == globals.BTN_COMMENTS[db_user['lang_id']] or Load == "✍️":
            Load = history[0]
            if Load == "✍️":
                update.message.reply_text(
                    f"{globals.FEEDBACK_START[db_user['lang_id']]}"
                )
            elif message != f"{globals.BTN_COMMENTS[db_user['lang_id']]}":
                db.suggestions(update.message.from_user.id, message)
                update.message.reply_text(
                    f"{globals.FEEDBACK_END[db_user['lang_id']]}"
                )
                Load = None

    elif state == 3:
        if message == globals.BTN_LANG_UZ:
            db.update_user_data(db_user['chat_id'], "lang_id", 1)
            context.user_data["state"] = globals.STATES["reg"]
            check(update, context)

        elif message == globals.BTN_LANG_RU:
            db.update_user_data(db_user['chat_id'], "lang_id", 2)
            context.user_data["state"] = globals.STATES["reg"]
            check(update, context)


        else:
            update.message.reply_text(
                text=globals.TEXT_LANG_WARNING
            )

    #############################################
    else:
        update.message.reply_text("Salom")
