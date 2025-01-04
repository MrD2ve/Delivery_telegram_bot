from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from collections import deque
import methods
from database import Database
import globals

db = Database("db-evos.db")

Load = None
Chart = 1

def inline_handler(update, context):
    global Load
    global Chart
    query = update.callback_query
    data_sp = str(query.data).split("_")
    db_user = db.get_user_by_chat_id(query.message.chat_id)
    history = deque(maxlen=15)

    def process_data(new_data):
        history.append(new_data)

    for data in data_sp:
        process_data(data)

    if data_sp[0] == "category":
        if data_sp[1] == "product":
            if data_sp[2] == "back":
                query.message.delete()
                products = db.get_products_by_category(category_id=int(data_sp[3]))
                buttons = methods.send_product_buttons(products=products, lang_id=db_user["lang_id"])

                clicked_btn = db.get_category_parent(int(data_sp[3]))

                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text=f"{globals.BACK[db_user['lang_id']]}",
                        callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text=f"{globals.BACK[db_user['lang_id']]}", callback_data=f"category_back"
                    )])

                query.message.reply_text(
                    text=globals.TEXT_ORDER[db_user['lang_id']],
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=buttons,
                    )
                )

            else:
                if len(data_sp) == 4:
                    query.message.delete()
                    carts = context.user_data.get("carts", {})
                    carts[f"{data_sp[2]}"] = carts.get(f"{data_sp[2]}", 0) + int(data_sp[3])
                    context.user_data["carts"] = carts

                    categories = db.get_categories_by_parent()
                    buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

                    text = f"{globals.AT_KORZINKA[db_user['lang_id']]}:\n\n"
                    lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                    total_price = 0
                    for cart, val in carts.items():
                        product = db.get_product_for_cart(int(cart))
                        text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
                        total_price += product['price'] * val

                    text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price} {globals.SUM[db_user['lang_id']]}"
                    buttons.append(
                        [InlineKeyboardButton(text=f"{globals.BTN_KORZINKA[db_user['lang_id']]}", callback_data="cart")]
                    )

                    query.message.reply_text(
                        text=text,
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=buttons,
                        )
                    )
                else:
                    product = db.get_product_by_id(int(data_sp[2]))
                    query.message.delete()

                    if int(history[2]):
                        Load = int(history[2])

                    caption = f"{globals.TEXT_PRODUCT_PRICE[db_user['lang_id']]} " + str(product["price"]) + \
                              f" {globals.SUM[db_user['lang_id']]}\n{globals.TEXT_PRODUCT_DESC[db_user['lang_id']]} " + \
                              product[f"description_{globals.LANGUAGE_CODE[db_user['lang_id']]}"]


                    buttons = [
                        [
                            InlineKeyboardButton(
                                text="<",
                                callback_data=f"minus"
                            ),
                            InlineKeyboardButton(
                                text=f"{Chart}",
                                callback_data=f"chart"
                            ),
                            InlineKeyboardButton(
                                text=">",
                                callback_data=f"plus"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text=f"{globals.SEND_CHART[db_user['lang_id']]}",
                                callback_data=f"category_product_{data_sp[2]}_{Chart}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text=f"{globals.BACK[db_user['lang_id']]}",
                                callback_data=f"category_product_back_{product['category_id']}"
                            )
                        ]
                    ]
                    query.message.reply_photo(
                        photo=open(product['image'], "rb"),
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                    )
        elif data_sp[1] == "back":
            if len(data_sp) == 3:
                parent_id = int(data_sp[2])
            else:
                parent_id = None

            categories = db.get_categories_by_parent(parent_id=parent_id)
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

            if parent_id:
                clicked_btn = db.get_category_parent(parent_id)

                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text=f"{globals.BACK[db_user['lang_id']]}", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text=f"{globals.BACK[db_user['lang_id']]}", callback_data=f"category_back"
                    )])

            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )
        else:
            categories = db.get_categories_by_parent(parent_id=int(data_sp[1]))
            if categories:
                buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            else:
                products = db.get_products_by_category(category_id=int(data_sp[1]))
                buttons = methods.send_product_buttons(products=products, lang_id=db_user["lang_id"])

            clicked_btn = db.get_category_parent(int(data_sp[1]))

            if clicked_btn and clicked_btn['parent_id']:
                buttons.append([InlineKeyboardButton(
                    text=f"{globals.BACK[db_user['lang_id']]}", callback_data=f"category_back_{clicked_btn['parent_id']}"
                )])
            else:
                buttons.append([InlineKeyboardButton(
                    text=f"{globals.BACK[db_user['lang_id']]}", callback_data=f"category_back"
                )])

            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )
    elif data_sp[0] == "cart":
        if len(data_sp) == 2 and data_sp[1] == "clear":
            context.user_data.pop("carts")
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            text = globals.TEXT_ORDER[db_user['lang_id']]

            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons,
                )
            )

        elif len(data_sp) == 2 and data_sp[1] == "back":
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

                context.user_data.get('cart_text',text)

                buttons.append([InlineKeyboardButton(text=f"{globals.BTN_KORZINKA[db_user['lang_id']]}", callback_data="cart")])

            else:
                text = globals.TEXT_ORDER[db_user['lang_id']]
            query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons,
                )
            )

        else:
            buttons = [
                [
                    InlineKeyboardButton(text=f"{globals.BUY[db_user['lang_id']]}",  callback_data="order"),
                    InlineKeyboardButton(text=f"{globals.CLEAR_CLAIM[db_user['lang_id']]}",  callback_data="cart_clear")
                ],
                [InlineKeyboardButton(text=f"{globals.BACK[db_user['lang_id']]}",  callback_data="cart_back")],
            ]
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )

    elif data_sp[0] == "order":
        if len(data_sp) > 1 and data_sp[1] == "payment":
            context.user_data['payment_type'] = int(data_sp[2])
            query.message.delete()
            query.message.reply_text(
                text=globals.SEND_LOCATION[db_user["lang_id"]],
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text=globals.SEND_LOCATION[db_user["lang_id"]], request_location=True)]],
                                                 resize_keyboard=True)
            )
        else:
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(text=f"{globals.MONEY[db_user['lang_id']]}", callback_data="order_payment_1"),
                        InlineKeyboardButton(text=f"{globals.CARD[db_user['lang_id']]}", callback_data="order_payment_2"),
                    ]]
                )
            )

    if data_sp[0] == 'plus':
        Chart += 1
        product = db.get_product_by_id(Load)

        buttons = [
            [
                InlineKeyboardButton(
                    text="<",
                    callback_data=f"minus"
                ),
                InlineKeyboardButton(
                    text=f"{Chart}",
                    callback_data=f"chart"
                ),
                InlineKeyboardButton(
                    text=">",
                    callback_data=f"plus"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{globals.SEND_CHART[db_user['lang_id']]}",
                    callback_data=f"category_product_{Load}_{Chart}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{globals.BACK[db_user['lang_id']]}",
                    callback_data=f"category_product_back_{product['category_id']}"
                )
            ]
        ]
        query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    elif data_sp[0] == 'minus' and Chart > 1:
        Chart -= 1
        product = db.get_product_by_id(Load)

        buttons = [
            [
                InlineKeyboardButton(
                    text="<",
                    callback_data=f"minus"
                ),
                InlineKeyboardButton(
                    text=f"{Chart}",
                    callback_data=f"chart"
                ),
                InlineKeyboardButton(
                    text=">",
                    callback_data=f"plus"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{globals.SEND_CHART[db_user['lang_id']]}",
                    callback_data=f"category_product_{Load}_{Chart}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{globals.BACK[db_user['lang_id']]}",
                    callback_data=f"category_product_back_{product['category_id']}"
                )
            ]
        ]
        query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

        # db.create_order(db_user['id'], context.user_data.get("carts", {}))
################################