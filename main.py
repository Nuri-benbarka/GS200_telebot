import logging
import json
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import gspread

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def is_numeric(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""Please use the command mid_term in this format:
/mid_term email student_id 
Example:
/mid_term muhammad@gmail.com 2200202020""")


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
            if context.args[0].lower() != student_info[0]:  # remove spaces
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Unknown email {context.args[0]} or serial number {context.args[1]}")
            else:
                print(update.effective_user.username)
                print(update.effective_chat.full_name)
                print(context.args[0])
                print(context.args[1])
                if student_info[3] + student_info[5] < student_info[4] + student_info[6]:
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


async def mid_term(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="""Please use the command in this format:
/mid_term email student_id 
Example:
/mid_term muhammad@gmail.com 2200202020""")
    else:
        try:
            student_info = grades[context.args[1]]
            if context.args[0].lower() != student_info[0]:  # remove spaces
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Unknown email {context.args[0]} or serial number {context.args[1]}")
            else:
                print(update.effective_user.username)
                print(update.effective_chat.full_name)
                print(context.args[0])
                print(context.args[1])
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"""هذه هي النتيحة الامتحان النصفي للطالب / الطالبة:
                                                                                           {student_info[1]}
                                                                       السؤال الاول:      6/{student_info[2]} 
                                                                       السؤال الثاني:   10/{student_info[10]} 
                                                                       السؤال الثالث:   10/{student_info[11]}
                                                                       المجموع:         25/{student_info[12]} 
                    """)
        except KeyError:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Unknown email {context.args[0]} or serial number {context.args[1]}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    gc = gspread.service_account(filename="my-drive-575757-6d5fe30b79ac.json")

    sh = gc.open("GS200_spring_2023")

    worksheet = sh.worksheet("Midterm")

    list_of_lists = worksheet.get_all_values()

    grades = {}
    for row in list_of_lists:
        if row[1].isnumeric():
            num = [float(x) if is_numeric(x) else 0 for x in row[4:15]]
            grades[row[1]] = [row[2].strip().lower()] + [row[3]] + num

    print(grades)
    token = json.load(open("tele_token.json"))
    application = ApplicationBuilder().token(token["TELE_API_KEY"]).build()

    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    result_handler = CommandHandler('result', result)
    mid_term_handler = CommandHandler('mid_term', mid_term)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    application.add_handler(result_handler)
    application.add_handler(mid_term_handler)
    application.add_handler(echo_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
