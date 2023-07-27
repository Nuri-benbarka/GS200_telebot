import logging
import json
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from codewars import get_kata
import gspread
import datetime

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


async def codewars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 2:
        url_head = context.args[1][:31]
        if url_head != "https://www.codewars.com/users/":
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"invalid url")
        else:
            cell = codewars_worksheet.find(context.args[0])
            if cell is None:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Unknown student_id {context.args[0]}")
            else:
                saved_user = codewars_worksheet.cell(2, cell.col).value
                user = context.args[1][31:].split('/')[0]
                if user != saved_user:
                    if cell.col <= 26:
                        codewars_worksheet.update(chr(ord("@") + cell.col) + "2", user)
                    else:
                        codewars_worksheet.update(chr((ord("@") + cell.col - ord("A")) // 26 + ord("@")) + chr(
                            (ord("@") + cell.col - ord("A")) % 26 + ord("A")) + "2", user)

                    await context.bot.send_message(chat_id=update.effective_chat.id,
                                                   text=f"""student id: {context.args[0]}, has the codewars profile:
                            {url_head + user}""")
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id,
                                                   text=f"""student id: {context.args[0]}, has the codewars profile:
                            {url_head + user}""")

    elif len(context.args) == 1:
        cell = codewars_worksheet.find(context.args[0])
        if cell is None:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Unknown student_id {context.args[0]}")
        else:
            saved_user = codewars_worksheet.cell(2, cell.col).value
            if saved_user is None:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="""Please update your profile using the command:
                                /codewars student_id codewars_url """)

            else:

                now = datetime.datetime.now()
                last_time = codewars_worksheet.cell(3, cell.col).value
                try:
                    last_time = datetime.datetime.strptime(last_time, '%m/%d/%y %H:%M:%S')
                except TypeError:
                    last_time = datetime.datetime.min

                dur = now - last_time

                if dur.total_seconds() > 3600 * 3:
                    kata_list = get_kata(saved_user)
                    if cell.col <= 26:
                        codewars_worksheet.update(chr(ord("@") + cell.col) + "3", now.strftime('%m/%d/%y %H:%M:%S'))
                        codewars_worksheet.update(
                            chr(ord("@") + cell.col) + "4:" + chr(ord("@") + cell.col) + str(4 + len(kata_list)),
                            [[x] for x in kata_list])
                    else:
                        codewars_worksheet.update(chr((ord("@") + cell.col - ord("A")) // 26 + ord("@")) + chr(
                            (ord("@") + cell.col - ord("A")) % 26 + ord("A")) + "3", now.strftime('%m/%d/%y %H:%M:%S'))
                        codewars_worksheet.update(
                            chr((ord("@") + cell.col - ord("A")) // 26 + ord("@")) + chr(
                                (ord("@") + cell.col - ord("A")) % 26 + ord("A")) + "4:" + chr(
                                (ord("@") + cell.col - ord("A")) // 26 + ord("@")) + chr(
                                (ord("@") + cell.col - ord("A")) % 26 + ord("A")) + str(4 + len(kata_list)),
                            [[x] for x in kata_list])
                else:
                    kata_list = codewars_worksheet.col_values(cell.col)[3:]

                for i, kata in enumerate(kata_list):
                    kata_list[i] = str(i + 1) + ") " + kata_list[i]
                kata_str = '\n'.join(kata_list)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"""You solved {len(kata_list)} problems and these problems are: 
    {kata_str}""")

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="""Please use the command in this format to update your profile:
            /codewars student_id codewars_url 
            Example:
            /codewars 2200202020 https://www.codewars.com/users/MYUSERNAME
            or in this format to check the questions we saw:
            /codewars student_id
            Example:
            /codewars 2200202020""")


async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="""Please use the command in this format:
/result email student_id 
Example:
/result muhammad@gmail.com 2200202020""")
    else:
        try:

            student_info = grades[context.args[1]]
            if context.args[0].lower() != student_info[0]:  # remove spaces
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Unknown email {context.args[0]} or student_id {context.args[1]}")
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
                                           text=f"Unknown email {context.args[0]} or student_id {context.args[1]}")


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
                                               text=f"Unknown email {context.args[0]} or student id {context.args[1]}")
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
                                           text=f"Unknown email {context.args[0]} or student_id {context.args[1]}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    gc = gspread.service_account(filename="my-drive-575757-6d5fe30b79ac.json")

    sh = gc.open("GS200_spring_2023")

    worksheet = sh.worksheet("Midterm")
    codewars_worksheet = sh.worksheet("codewars")

    list_of_lists = worksheet.get_all_values()

    grades = {}
    for row in list_of_lists:
        if row[1].isnumeric():
            num = [float(x) if is_numeric(x) else 0 for x in row[4:15]]
            grades[row[1]] = [row[2].strip().lower()] + [row[3]] + num + [row[15]]

    print(grades)
    token = json.load(open("tele_token.json"))
    application = ApplicationBuilder().token(token["TELE_API_KEY"]).build()

    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    result_handler = CommandHandler('result', result)
    mid_term_handler = CommandHandler('mid_term', mid_term)
    codewars_handler = CommandHandler('codewars', codewars)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    #    application.add_handler(result_handler)
    application.add_handler(mid_term_handler)
    application.add_handler(codewars_handler)
    application.add_handler(echo_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
