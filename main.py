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

                # if dur.total_seconds() > 3600 * 3:
                if False:
                    kata_list = get_kata(saved_user)
                    if cell.col <= 26:
                        codewars_worksheet.update(chr(ord("@") + cell.col) + "3", now.strftime('%m/%d/%y %H:%M:%S'))
                        codewars_worksheet.update(
                            chr(ord("@") + cell.col) + "5:" + chr(ord("@") + cell.col) + str(5 + len(kata_list)),
                            [[x] for x in kata_list])
                    else:
                        codewars_worksheet.update(chr((ord("@") + cell.col - ord("A")) // 26 + ord("@")) + chr(
                            (ord("@") + cell.col - ord("A")) % 26 + ord("A")) + "3", now.strftime('%m/%d/%y %H:%M:%S'))
                        codewars_worksheet.update(
                            chr((ord("@") + cell.col - ord("A")) // 26 + ord("@")) + chr(
                                (ord("@") + cell.col - ord("A")) % 26 + ord("A")) + "5:" + chr(
                                (ord("@") + cell.col - ord("A")) // 26 + ord("@")) + chr(
                                (ord("@") + cell.col - ord("A")) % 26 + ord("A")) + str(5 + len(kata_list)),
                            [[x] for x in kata_list])
                else:
                    kata_list = codewars_worksheet.col_values(cell.col)[4:]

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
        if context.args[1] in result_grades:
            student_info = result_grades[context.args[1]]
            if context.args[0].lower() == student_info[result_headers.index("email") - 1].lower():  # remove spaces
                print(update.effective_user.username)
                print(update.effective_chat.full_name)
                print(context.args[0])
                print(context.args[1])
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"""هذه هي النتيحة النهائية للطالب / الطالبة:
                                                                       {student_info[result_headers.index("الاسم") - 1]}
                                                                       الواجبات:             10/{student_info[result_headers.index("HW / 10") - 1]} 
                                                                       الامتحان النصفي: 25/{student_info[result_headers.index("mid-term / 25") - 1]} 
                                                                       الامتحان العملي:  30/{student_info[result_headers.index("lab / 30") - 1]}
                                                                       الامتحان النهائي:  35/{student_info[result_headers.index("final / 35") - 1]} 
                                                                       الاضافي:               5/{student_info[result_headers.index("Extra / 5") - 1]} 
                                                                       المجموع:       100/{student_info[result_headers.index("Total / 100") - 1]} 
                    """)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Email {context.args[0]} and student id {context.args[1]} don't match")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Unknown student_id {context.args[1]}")


async def mid_term(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="""Please use the command in this format:
/mid_term email student_id 
Example:
/mid_term muhammad@gmail.com 2200202020""")
    else:
        if context.args[1] in mid_grades:
            student_info = mid_grades[context.args[1]]
            if context.args[0].lower() == student_info[headers.index("email") - 1].lower():  # remove spaces
                print(update.effective_user.username)
                print(update.effective_chat.full_name)
                print(context.args[0])
                print(context.args[1])
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"""هذه هي النتيحة الامتحان النصفي للطالب / الطالبة:
                                                                                           {student_info[headers.index("الاسم") - 1]}
                                                                       السؤال الاول:      6/{student_info[headers.index("Q1") - 1]} 
                                                                       السؤال الثاني:   10/{student_info[headers.index("Q2") - 1]} 
                                                                       السؤال الثالث:   10/{student_info[headers.index("Q3") - 1]}
                                                                       المجموع:         25/{student_info[headers.index("Total") - 1]} 
                    """)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Email {context.args[0]} and student id {context.args[1]} don't match")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Unknown student_id {context.args[1]}")


async def final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="""Please use the command in this format:
/mid_term email student_id 
Example:
/mid_term muhammad@gmail.com 2200202020""")
    else:
        if context.args[1] in final_grades:
            student_info = final_grades[context.args[1]]
            if context.args[0].lower() == student_info[headers.index("email") - 1].lower():  # remove spaces
                print(update.effective_user.username)
                print(update.effective_chat.full_name)
                print(context.args[0])
                print(context.args[1])
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"""هذه هي النتيحة الامتحان النهائي النظري للطالب / الطالبة:
                                                                                           {student_info[headers.index("الاسم") - 1]}
                                                                       السؤال الاول:      4/{student_info[headers.index("Q1") - 1]} 
                                                                       السؤال الثاني:   16/{student_info[headers.index("Q2") - 1]} 
                                                                       السؤال الثالث:   15/{student_info[headers.index("Q3") - 1]}
                                                                       المجموع:         35/{student_info[headers.index("Total") - 1]} 
                    """)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Email {context.args[0]} and student id {context.args[1]} don't match")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Unknown student_id {context.args[1]}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def get_grades(sheet_lists, headers):
    header_indeces = []
    for header in headers:
        header_indeces.append(sheet_lists[0].index(header))
    grades = {}
    for row in sheet_lists[1:]:
        if row[header_indeces[0]].isnumeric():
            grades[row[header_indeces[0]]] = [float(row[h]) if is_numeric(row[h]) else row[h] for h in
                                              header_indeces[1:]]

    return grades


if __name__ == '__main__':
    gc = gspread.service_account(filename="my-drive-575757-6d5fe30b79ac.json")

    sh = gc.open("GS200_spring_2023")

    mid_lists = sh.worksheet("Midterm").get_all_values()
    final_lists = sh.worksheet("Final").get_all_values()
    result_lists = sh.worksheet("Total").get_all_values()
    codewars_worksheet = sh.worksheet("codewars")

    headers = ["رقم القيد", "الاسم", "email", "Q1", "Q2", "Q3", "Total"]
    result_headers = ["رقم القيد", "الاسم", "email", "mid-term / 25", "final / 35", "HW / 10", "lab / 30", "Extra / 5",
                      "Total / 100"]

    mid_grades = get_grades(mid_lists, headers)
    final_grades = get_grades(final_lists, headers)
    result_grades = get_grades(result_lists,result_headers)

    token = json.load(open("tele_token.json"))
    application = ApplicationBuilder().token(token["TELE_API_KEY"]).build()

    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    result_handler = CommandHandler('result', result)
    mid_term_handler = CommandHandler('mid_term', mid_term)
    final_handler = CommandHandler('final', final)
    codewars_handler = CommandHandler('codewars', codewars)
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    application.add_handler(result_handler)
    application.add_handler(mid_term_handler)
    application.add_handler(final_handler)
    application.add_handler(codewars_handler)
    # application.add_handler(echo_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
