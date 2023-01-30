from aiogram.types import PollAnswer
from aiogram.dispatcher.filters import Filter
from create_bot import dp


class PollStateFilter(Filter):
    async def check(self, poll_answer: PollAnswer) -> bool:
        state = dp.get_current().current_state()
        async with state.proxy() as data:
            poll_id = data.get('poll_id')
        return poll_answer.poll_id == poll_id
