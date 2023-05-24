import Constants as keys
import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from grade_processor import grades

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""Please use the command result in this format:
/result email serial_number 
Example:
/result muhammad@gmail.com 2200202020""")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="""Please use the command in this format:
/result email serial_number 
Example:
/result muhammad@gmail.com 2200202020""")
    else:
        try:

            student_info = grades[context.args[1]]
            if context.args[0].lower() != student_info[0]: # remove spaces
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Unknown email {context.args[0]} or serial number {context.args[1]}")
            else:
                print(update.effective_user.username)
                print(update.effective_chat.full_name)
                print(context.args[0])
                print(context.args[1])
                if student_info[3]+student_info[5] < student_info[4] + student_info[6]:
                    await context.bot.send_message(chat_id=update.effective_chat.id,
                                                   text=f"""هذه هي النتيحة النهائية للطالب / الطالبة:
                                                                       {student_info[1]}
                                                                       الواجبات:             10/{student_info[2]} 
                                                                       الامتحان النصفي: 30/{student_info[4]} 
                                                                       الامتحان العملي:  20/{student_info[6]}
                                                                       الامتحان النهائي:  40/{student_info[7]} 
                                                                       الاضافي:               5/{student_info[8]} 
                                                                       المجموع:       100/{student_info[11]} 
                    """)
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id,
                                                   text=f"""هذه هي النتيحة النهائية للطالب / الطالبة:
                                                              {student_info[1]}
                                                              الواجبات:              10/{student_info[2]} 
                                                              الامتحان النصفي:  25/{student_info[3]} 
                                                              الامتحان العملي:  25/{student_info[5]}
                                                              الامتحان النهائي:  40/{student_info[7]} 
                                                              الاضافي:                 5/{student_info[8]} 
                                                              المجموع:        100/{student_info[11]} 
                                                    """)
        except KeyError:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Unknown email {context.args[0]} or serial number {context.args[1]}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(keys.API_KEY).build()

    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    result_handler = CommandHandler('result', result)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    application.add_handler(result_handler)
    application.add_handler(echo_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
