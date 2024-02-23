from current_bot import _, filters, types, dp, bot
from keyboards.inline.set_questions_key import set_question_key
from aiogram.filters.callback_data import CallbackData
from data.search_questions import IslomUz


@dp.message(filters.CommandStart())
async def start_command(message: types.Message):
    await message.answer("Assalomu alaykum ushbu bot sizga savollar.islom.uz saytidagi malumotlarni osongina "
                         "telegramga o'tkazish imkonini beradi. Siz menga savolning bo'lishi mumkin bo'lgan "
                         "sarlavhasini yuboring men sizga shunga o'xshash bo'lgan savol javoblarni beraman.\n"
                         "Masalan ''Bankdan muddatli to'lovga mashina olishim mumkinmi?'' o'rniga 'Kredit' kabi.")


@dp.message()
async def search_questions(message: types.Message):
    await bot.send_chat_action(message.from_user.id, 'typing')
    search_result = await IslomUz().search_topic(message.text)
    if len(search_result) == 0:
        await message.answer("Bu mavzuda hech qanday savol-javoblar topilmadi")
    else:
        answer_text = "Natijalar"
        i = 1
        for response in search_result:
            answer_text += "\n"
            answer_text += f"{i}. {response.question_paragraph}"
            i += 1
        answer_keyboard = set_question_key(message.text, search_result)
        await message.answer(text=answer_text, reply_markup=answer_keyboard)


class SearchInlineKeyboard(CallbackData, prefix="search"):
    search_topic_name: str


@dp.callback_query(SearchInlineKeyboard.filter())
async def back_search_result(call: types.CallbackQuery, callback_data: SearchInlineKeyboard):
    search_topic = callback_data.search_topic_name
    search_result = await IslomUz().search_topic(search_topic)
    answer_text = "Natijalar"
    i = 1
    for response in search_result:
        answer_text += "\n"
        answer_text += f"{i}. {response.question_paragraph}"
        i += 1
    answer_keyboard = set_question_key(search_topic, search_result)
    await call.message.edit_text(text=answer_text, reply_markup=answer_keyboard)


@dp.callback_query()
async def answer_info(call: types.CallbackQuery):
    question_url = call.data.split(":")
    answer_text = await IslomUz().get_info(question_url[1])
    answer_all_text = f"Savol:\n{answer_text.question}\n\nJavob:\n{answer_text.answer}\n\nManba: https://savollar.islom.uz{question_url[1]}"
    answer_keyboard = types.InlineKeyboardMarkup(inline_keyboard=
    [
        [
            types.InlineKeyboardButton(text="Orqaga",
                                       callback_data=SearchInlineKeyboard(search_topic_name=question_url[0]).pack())
        ]
    ]
    )
    if len(answer_all_text) < 4096:
        await call.message.edit_text(text=answer_all_text, reply_markup=answer_keyboard, disable_web_page_preview=True)
    else:
        await call.answer()
        await call.message.answer(f"Bu juda ham uzun matn ekan. Uni to'liq quyidgai sahifada o'qing\n"
                                  f"https://savollar.islom.uz{question_url[1]}")
