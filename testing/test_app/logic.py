from bottex2.router import Router, any_cond, text_cond
from bottex2.chat import Keyboard, Button
from bottex2.users import state_cond

kb = Keyboard([
    [Button('1'), Button('2'), Button('3')],
    [Button('4'), Button('5'), Button('6')],
    [Button('7'), Button('8'), Button('9')],
    [Button('*'), Button('0'), Button('#')],
])


states = {
    '1': '2',
    '2': '3',
    '3': '1'
}


router = Router()


@router.set_default
async def set_state(chat, user, **params):
    state = next(iter(states))
    await user.update(state=state)
    await chat.send_message(f'hi, user {user.uid}', kb=kb)


@router.register(text_cond('bug'))
def bug(**params):
    raise RuntimeError('bug!')


@router.register(any_cond([state_cond(s) for s in states]))
async def switch(chat, user, **params):
    await user.update(state=states[user.state])
    await chat.send_message(f'switched')
    # await asyncio.sleep(2)
    await send_settings(chat=chat, user=user, **params)


async def send_settings(chat, user, **params):
    text = '\n'.join([
        f'id: {user.uid}',
        f'state: {user.state}',
    ])
    await chat.send_message(text)
