import json
from typing import Union, Dict, Any

from aiogram import Router, F
from aiogram.filters import CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from bot import bot
from keyboarads import main_kb, data_ikb, form_ikb
from states import DataStates

router = Router()

# Фильтр web_app_data
class WebAppDataFilter(Filter):
    async def __call__(self, message: Message, **kwargs) -> Union[bool, Dict[str, Any]]:
        return dict(web_app_data=message.web_app_data) if message.web_app_data else False


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(DataStates.get_data)
    bot_message = await message.answer('Для того чтобы внести данные откройте форму по кнопке ниже клавиатуры',
                                       reply_markup=form_ikb())
    await state.update_data(bot_message=bot_message)

# Хэндлер для обработки we_app_data
@router.message(WebAppDataFilter())
async def web_app_data(message: Message, state: FSMContext):
    dict_ = await state.get_data()
    bot_message = dict_['bot_message']
    await bot.delete_message(chat_id=message.chat.id, message_id=bot_message.message_id)
    data = json.loads(message.web_app_data.data)
    bot_message_2 = await message.answer(
        text=f'Способ оплаты-{data["payment_type"]}\nЦена аренды-{data["rent_price"]}\nЦена доставки-{data["delivery_price"]}',
        reply_markup=data_ikb())
    await state.update_data(bot_message=bot_message_2)


@router.callback_query(F.data == 'success')
async def success(callback_query: CallbackQuery, state: FSMContext):
    dict_ = await state.get_data()
    bot_message = dict_['bot_message']
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=bot_message.message_id)
    await callback_query.message.answer(text='Данные сохранены',
                                        reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.callback_query(F.data == 'edit')
async def edit(callback_query: CallbackQuery, state: FSMContext):
    dict_ = await state.get_data()
    bot_message = dict_['bot_message']
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=bot_message.message_id)
    bot_message_2 = await callback_query.message.answer(
        text='Для того чтобы внести данные откройте форму по кнопке ниже клавиатуры',
        reply_markup=form_ikb())
    await state.update_data(bot_message=bot_message_2)
