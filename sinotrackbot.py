
import logging
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
from decouple import config

# Load environment variables from the .env file
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
ORDER_URL = config('ORDER_URL')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SELECTING_ACTION, ST_902, ST_903, ST_907 = map(chr, range(4))

SELECTING_LEVEL = map(chr, range(4, 5))

SELECTING_FEATURE = map(chr, range(5, 6))

STOPPING, ORDERING = map(chr, range(6, 8))

END = ConversationHandler.END

(
    INFO,
    INSTALLATION,
    START_OVER,
    FEATURES,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
) = map(chr, range(8, 14))

installation_instructions = {
    "ST-902": [
    "التعليمة: ضبط رقم التحكم",
    "commande: Number+pass+blank+serial",
    "المثال: 139504434650000 1",
    "الوصف: 13950443465 هو رقم الجوال",
    "0000 هو كلمة المرور",
    "1 يعني الرقم التسلسلي ويمثل الرقم الأول. عندما يرد المتتبع بـ 'SET OK' يعني أن الإعداد صحيح. يمكنك أيضًا ضبط الرقم التسلسلي الثاني والثالث.",
    "التعليمة: لضبط APN:",
    "commande: 8030000 internet  ",
    "الوصف: (APN هو اسم نقطة الوصول لبطاقة SIM الخاصة بك، يرجى التحقق منه مع مزود بطاقة SIM الخاص بك إذا لم تكن تعرفه)",
    "التعليمة: إرسال رسالة نصية لضبط المتتبعات إلى خادمنا",
    "commande: 8040000 45.112.204.245 8090",
    "الوصف: ",
    "التعليمة: الحصول على الموقع بواسطة رابط Google",
    "commande: 669+password",
    "المثال: 6690000",
    "الوصف: عندما يتلقى جهاز ST-907 الأمر، سيُرسل الموقع برابط Google الخاص به. يمكنك فتح الرابط للتحقق من موقع المتتبع على الخرائط.",

],
    "ST-903": [
    "التعليمة: ضبط رقم التحكم",
    "commande: Number+pass+blank+serial",
    "المثال: 139504434650000 1",
    "الوصف: 13950443465 هو رقم الجوال",
    "0000 هو كلمة المرور",
    "1 يعني الرقم التسلسلي ويمثل الرقم الأول. عندما يرد المتتبع بـ 'SET OK' يعني أن الإعداد صحيح. يمكنك أيضًا ضبط الرقم التسلسلي الثاني والثالث.",
    "التعليمة: لضبط APN:",
    "commande: 8030000 internet  ",
    "الوصف: (APN هو اسم نقطة الوصول لبطاقة SIM الخاصة بك، يرجى التحقق منه مع مزود بطاقة SIM الخاص بك إذا لم تكن تعرفه)",
    "التعليمة: إرسال رسالة نصية لضبط المتتبعات إلى خادمنا",
    "commande: 8040000 45.112.204.245 8090",
    "الوصف: ",
    "التعليمة: الحصول على الموقع بواسطة رابط Google",
    "commande: 669+password",
    "المثال: 6690000",
    "الوصف: عندما يتلقى جهاز ST-907 الأمر، سيُرسل الموقع برابط Google الخاص به. يمكنك فتح الرابط للتحقق من موقع المتتبع على الخرائط.",
"التعليمة: مراقبة الصوت",
    "commande: 66",
    "الوصف: إرسال الأمر 66 إلى متتبع GPS من رقم التحكم. سيتصل المتتبع بالعودة إلى هذا الرقم."

    ],
    "ST-907": [
    "التعليمة: ضبط رقم التحكم",
    "commande: Number+pass+blank+serial",
    "المثال: 139504434650000 1",
    "الوصف: 13950443465 هو رقم الجوال",
    "0000 هو كلمة المرور",
    "1 يعني الرقم التسلسلي ويمثل الرقم الأول. عندما يرد المتتبع بـ 'SET OK' يعني أن الإعداد صحيح. يمكنك أيضًا ضبط الرقم التسلسلي الثاني والثالث.",
    "التعليمة: لضبط APN:",
    "commande: 8030000 internet  ",
    "الوصف: (APN هو اسم نقطة الوصول لبطاقة SIM الخاصة بك، يرجى التحقق منه مع مزود بطاقة SIM الخاص بك إذا لم تكن تعرفه)",
    "التعليمة: إرسال رسالة نصية لضبط المتتبعات إلى خادمنا",
    "commande: 8040000 45.112.204.245 8090",
    "الوصف: ",
    "التعليمة: الحصول على الموقع بواسطة رابط Google",
    "commande: 669+password",
    "المثال: 6690000",
    "الوصف: عندما يتلقى جهاز ST-907 الأمر، سيُرسل الموقع برابط Google الخاص به. يمكنك فتح الرابط للتحقق من موقع المتتبع على الخرائط.",
    "التعليمة: قطع المحرك عن بُعد",
    "commande: 940+password",
    "المثال: 9400000",
    "الوصف: بعد أن يتلقى المتتبع الأمر، سيُقطع المحرك ويُرسل رد برسالة نصية 'SET OK'",
    "التعليمة: أمر استعادة المحرك",
    "commande: 941+password",
    "الوصف: بعد أن يتلقى المتتبع الأمر، سيُعيد المحرك ويُرسل رد برسالة نصية 'SET OK'"
]
    # Add instructions for other products
}

product_information = {
    "ST-902": [
        [
        "التتبع في الوقت الحقيقي: يتيح لك الجهاز تتبع موقع سيارتك بدقة في الوقت الحقيقي، مما يساعدك في مراقبة حركتها وموقعها باستمرار.",
        "التنبيهات والإشعارات: يمكنك ضبط إعدادات التنبيه لتلقي إشعارات عند تشغيل السيارة أو إيقاف تشغيلها، مما يساعد في تعزيز الأمان والمتابعة الفعالة.",
        "تخزين تاريخ التحرك: يمكن للجهاز تخزين تاريخ التحرك وتاريخ الوقوف، مما يساعد في تحليل أنماط الاستخدام والتشغيل.",
        "متانة ومقاومة: يتميز الجهاز بتصميم مقاوم للماء والغبار، مما يجعله مناسبًا للاستخدام في مجموعة متنوعة من الظروف البيئية.",
        "تطبيق الجوال: يأتي مع تطبيق للهواتف الذكية يتيح لك متابعة الموقع وإدارة الإعدادات بسهولة عبر الهاتف.",
        "مدة البطارية: يحتوي على بطارية تعمل حتى في حالة انقطاع بطارية السيارة أو فصل الجهاز.",
        "التوافق العالمي: يدعم الجهاز مجموعة واسعة من ترددات الاتصال، مما يسمح بتتبع الأصول في معظم مناطق العالم."

    ], [
"https://gps-trace.com/api/gw/device/image?device_id=590159283"
        ]
    ],

    "ST-903": [
        [
    "الوظيفة الرئيسية: أجهزة تتبع السيارات الصغيرة من SinoTrack للدراجات النارية، مزودة بنظام تحديد المواقع والتتبع عبر الإنترنت والجي بي إس والجي بي آر إس والجي إس إم والرسائل النصية. جهاز تتبع السيارات ST-903، بسيط جدًا وسهل الاستخدام للدراجات النارية والشاحنات والتاكسي والأفراد وما إلى ذلك. إشعارات الرسائل النصية للحركة والسرعة ومغادرة أو دخول المناطق والبطارية المنخفضة والصدمات، يتم حفظ بيانات التاريخ والتقارير القيادة خلال الخدمة. بطارية احتياطية مدمجة بسعة 1050 مللي أمبير في الساعة. جهاز تتبع جي بي إس مخفي مع وظيفة مراقبة الصوت.",
    "المنصة المجانية: جهاز تحديد المواقع ومتعقب مقاوم للماء مع خدمة تتبع عبر الإنترنت بدون اشتراك. اشترِ بطاقة SIM للجهاز (لا يتضمن جهاز تحديد المواقع هذا بطاقة SIM، يجب عليك شراء واحدة أخرى. ابحث عن تسجيل الدخول SinoTrackerPro على الويب أو ابحث عن تطبيق GPS \"SinotrackPro\" للتنزيل من الكمبيوتر اللوحي أو الكمبيوتر الشخصي أو الهاتف الخلوي. التتبع الحي متاح بدون تكلفة إضافية.",
    "التتبع في الوقت الحقيقي: جهاز تتبع السيارات في الوقت الحقيقي، إنذار فقدان الموقع بناءً على شبكة الجي إس إم والجي بي آر إس والأقمار الصناعية جي بي إس، حيث يمكن تحديد ومراقبة الأهداف عن بُعد باستخدام تطبيق تتبع الجي بي إس الذي يعرض معلومات الموقع بدقة (دقة تحديد الموقع تصل إلى 10 أمتار).",
    "ذاكرة التاريخ: جهاز تتبع السيارات Sinotrack يمكنه حفظ سجلات التتبع لمدة عامين. بفاصل زمني مُحدد، يمكنك عرض وتشغيل سجلات التتبع اليومية، وعندما تذهب السيارة إلى مكان ما يمكنك اتخاذ قرار أكثر وضوحًا."
],[
"https://gps-trace.com/api/gw/device/image?device_id=979640423"
        ]
    ],
    "ST-907": [
        [
    "دعم شبكة 2G فقط: البطاقة SIM غير مدرجة، يرجى شراء بطاقة SIM محلية تدعم شبكة 2G (GSM). يدعم جهاز تتبع السيارات Sinotrack ST-907 شبكة 2G (GSM) فقط، يرجى التأكد مما إذا كان مكان إقامتك المحلي يدعم شبكة 2G قبل شرائه.",
    "الوظيفة الرئيسية: أجهزة تتبع السيارات الصغيرة من SinoTrack للدراجات النارية، مزودة بهوائيين مزدوجين للجي إس إم والجي بي آر إس (البطاقة SIM غير مدرجة). جهاز تتبع السيارات ST-907 مزود ببطارية احتياطية مدمجة بجهد 3.7 فولت وبسعة 50 مللي أمبير في الساعة. إن جهاز تتبع السيارات هذا سهل الاستخدام جدًا للدراجات النارية والشاحنات والتاكسي وما إلى ذلك. إشعارات الرسائل النصية للزيادة في السرعة، والصدمات، ومغادرة أو دخول المناطق، والبطارية المنخفضة، وقطع المحرك عن بُعد واستعادته. يمكنك التحقق من تقارير القيادة وبيانات التاريخ المحفوظة خلال الخدمة على منصتنا.",
    "قطع المحرك عن بُعد: باستخدام جهاز تتبع السيارات ST-907 مع ريلاي، عندما تجد أن سيارتك قد تمت سرقتها، يمكنك التحكم في سيارتك عن بُعد على هاتفك، وقطع المحرك عن طريق إرسال أمر الرسالة النصية، ستتوقف السيارة عن الحركة حتى تتلقى أمر الرسالة النصية الخاص بك \"9400000\"، وهذا يمنع سرقة سيارتك في موقف السيارات. يمكنك أيضًا استعادة المحرك عبر أمر الرسالة النصية. فقط عندما تكون السيارة تسير بسرعة أقل من 20 كم/ساعة، يمكن أن تتوقف سيارتك عندما تحصل على أمر الرسالة النصية خلال ثوانٍ قليلة. أكثر من 20 كم/ساعة، فإن محركك لا يمكن قطعه.",
    "دعم منصة التتبع مدى الحياة: جهاز تحديد المواقع ومتعقب مقاوم للماء مع اشتراك في خدمة التتبع عبر الإنترنت. اشترِ بطاقة SIM للجهاز (لا يتضمن جهاز تحديد المواقع هذا بطاقة SIM، يجب عليك شراء واحدة أخرى)، ابحث عن Sinotrackerpro على الويب لتسجيل الدخول أو ابحث عن تطبيق GPS SinotrackPro للتنزيل من الكمبيوتر اللوحي أو الكمبيوتر الشخصي أو الهاتف الخلوي مدى الحياة. التتبع الحي متاح بدون تكلفة إضافية.",
    "التتبع في الوقت الحقيقي: جهاز تتبع السيارات في الوقت الحقيقي ST-907 Anti Lost Alarm Locator بناءً على شبكة الجي إس إم، حيث يمكن تحديد ومراقبة الأهداف عن بُعد باستخدام منصتنا الخاصة لتتبع الجي بي إس، والتي تعرض معلومات الموقع بدقة (دقة تحديد الموقع تصل إلى 10 أمتار). يمكن لجهاز تتبع السيارات الخاص بشركة Sinotrack حفظ سجلات التتبع لمدة عامين. جهاز تحديد المواقع بتكنولوجيا جي بي إس مع فاصل زمني يمكنك من عرض وتشغيل سجلات التتبع اليومية الخاصة بك، عندما تذهب السيارة إلى مكان ما، يمكن أن تساعدك في اتخاذ قرار أوضح."
],
    [
"https://gps-trace.com/api/gw/device/image?device_id=267076593"
    ]]
}

# Top level conversation callbacks
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action: Adding parent/child or show data."""
    text = (
        "You may choose a Sinotrack product, or end the "
        "conversation. To abort, simply type /stop."
    )

    buttons = [
        [
            InlineKeyboardButton(text="ST-902", callback_data=str(ST_902)),
            InlineKeyboardButton(text="ST-903", callback_data=str(ST_903)),
            InlineKeyboardButton(text="ST-907", callback_data=str(ST_907)),
        ],
        [InlineKeyboardButton(text="Done", callback_data=str(END))],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need to send a new message
    if context.user_data.get(START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(
            "Hi, I'm Sinotrack Bot and I'm here to help you gather information, do the installation for your Sinotrack product."
        )
        await update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Forward the user to a website to complete the order process."""
    # URL of the website where the user can complete the order process
    order_url = ORDER_URL  # Replace this URL with the actual order URL
    # Create an inline keyboard button to redirect the user to the order website
    buttons = [[InlineKeyboardButton(text="Order", url=order_url)]]
    keyboard = InlineKeyboardMarkup(buttons)

    # Send a message with the order button and forward the user to the website
    text = "Click the button below to complete your order:"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    # Return the ORDERING state
    return ORDERING


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Okay, bye.")

    return END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    await update.callback_query.answer()

    text = "See you around!"
    await update.callback_query.edit_message_text(text=text)

    return END


async def select_product_st_902(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Choose to add a parent or a child."""
    context.user_data[CURRENT_FEATURE] = "ST-902"
    text = "You may want to check product information or see the installation. Also you can make an order or go back."
    buttons = [
        [
            InlineKeyboardButton(text="product information", callback_data=str(INFO)),
            InlineKeyboardButton(text="product Installation", callback_data=str(INSTALLATION)),
        ],
        [
            InlineKeyboardButton(text="Order", callback_data=str(ORDERING)),
            InlineKeyboardButton(text="Back", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_FEATURE


async def select_product_st_903(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Choose to add a parent or a child."""
    context.user_data[CURRENT_FEATURE] = "ST-903"
    text = "You may want to check product information or see the installation. Also you can make an order or go back."
    buttons = [
        [
            InlineKeyboardButton(text="product information", callback_data=str(INFO)),
            InlineKeyboardButton(text="product Installation", callback_data=str(INSTALLATION)),
        ],
        [
            InlineKeyboardButton(text="Order", callback_data=str(ORDERING)),
            InlineKeyboardButton(text="Back", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_FEATURE

async def select_product_st_907(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Choose to add a parent or a child."""
    context.user_data[CURRENT_FEATURE] = "ST-907"
    text = "You may want to check product information or see the installation. Also you can make an order or go back."
    buttons = [
        [
            InlineKeyboardButton(text="product information", callback_data=str(INFO)),
            InlineKeyboardButton(text="product Installation", callback_data=str(INSTALLATION)),
        ],
        [
            InlineKeyboardButton(text="Order", callback_data=str(ORDERING)),
            InlineKeyboardButton(text="Back", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_FEATURE


async def display_installation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    product = context.user_data[CURRENT_FEATURE]
    instructions = installation_instructions.get(product)

    if instructions:
        text = "Installation Instructions for {}:\n".format(product)
        text += "\n".join(instructions)
    else:
        text = "Installation instructions are not available for this product."

    buttons = [[InlineKeyboardButton("Back", callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_LEVEL


async def display_product_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    product = context.user_data[CURRENT_FEATURE]
    # Retrieve product information based on the selected product
    product_info = product_information.get(product)[0]
    product_image = product_information.get(product)[1][0]

    if product_info and product_image:
        text = "معلومات حول المنتج لـ {} :\n".format(product)
        text += "\n".join(product_info)
    else:
        text = "Product information is not available for this product."

    # Send the image first
    await context.bot.send_photo(chat_id=update.callback_query.message.chat_id, photo=product_image)

    # Send the text as a separate message
    await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=text)

    buttons = [[InlineKeyboardButton("Back", callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Press Back to return to the main list", reply_markup=keyboard)

    return SELECTING_LEVEL




async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END


async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Completely end conversation from within nested conversation."""
    await update.message.reply_text("Okay, bye.")

    return STOPPING



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
    st_902_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_product_st_902, pattern="^" + str(ST_902) + "$")],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(display_product_info, pattern="^" + str(INFO) + "$"),
                CallbackQueryHandler(display_installation, pattern="^" + str(INSTALLATION) + "$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(order, pattern="^" + str(ORDERING) + "$"),
            CallbackQueryHandler(end_second_level, pattern="^" + str(END) + "$"),
            CommandHandler("stop", stop_nested),
        ],
        map_to_parent={
            # After showing data return to top level menu
            ORDERING: ORDERING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: END,
        },
    )

    st_903_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_product_st_903, pattern="^" + str(ST_903) + "$")],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(display_product_info, pattern="^" + str(INFO) + "$"),
                CallbackQueryHandler(display_installation, pattern="^" + str(INSTALLATION) + "$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(order, pattern="^" + str(ORDERING) + "$"),
            CallbackQueryHandler(end_second_level, pattern="^" + str(END) + "$"),
            CommandHandler("stop", stop_nested),
        ],
        map_to_parent={
            # After showing data return to top level menu
            ORDERING: ORDERING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: END,
        },
    )

    st_907_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_product_st_907, pattern="^" + str(ST_907) + "$")],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(display_product_info, pattern="^" + str(INFO) + "$"),
                CallbackQueryHandler(display_installation, pattern="^" + str(INSTALLATION) + "$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(order, pattern="^" + str(ORDERING) + "$"),
            CallbackQueryHandler(end_second_level, pattern="^" + str(END) + "$"),
            CommandHandler("stop", stop_nested),
        ],
        map_to_parent={
            # After showing data return to top level menu
            ORDERING: ORDERING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: END,
        },
        # per_message=True,
    )

    selection_handlers = [
        st_902_conv,
        st_903_conv,
        st_907_conv,
        CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ORDERING: [CallbackQueryHandler(start, pattern="^" + str(END) + "$")],
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            STOPPING: [CommandHandler("start", start)],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

