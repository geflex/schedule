from bottex2.handler import request_handler, Request
from bottex2.router import Router, any_cond, text_cond
from bottex2.chat import Keyboard, Button
from bottex2.middlewares.users import state_cond

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
@request_handler
async def set_state(r: Request):
    state = next(iter(states))
    await r.user.update(state=state)
    await r.chat.send_message(f'hi, user {r.user.uid}', kb=kb)


@router.register(text_cond('bug'))
@request_handler
async def bug(request: Request):
    raise RuntimeError('bug!')


@router.register(text_cond('lol'))
@request_handler
async def bug(request: Request):
    await request.chat.send_message('lol')


@router.register(any_cond([state_cond(s) for s in states]))
@request_handler
async def switch(r: Request):
    await r.user.update(state=states[r.user.state])
    await r.chat.send_message(f'switched')
    await send_settings(r)


async def send_settings(r: Request):
    text = '\n'.join([
        f'id: {r.user.uid}',
        f'state: {r.user.state}',
    ])
    await r.chat.send_message(text)
