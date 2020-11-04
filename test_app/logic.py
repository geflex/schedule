from bottex2.handler import Request
from bottex2.router import Router, any_cond, text_cond
from bottex2.chat import Keyboard, Button
from bottex2.ext.users import state_cond


kb = Keyboard([
    [Button('1'), Button('2'), Button('3')],
    [Button('4'), Button('5'), Button('6')],
    [Button('7'), Button('8'), Button('9')],
    [Button('send'), Button('stop')],
])


states = {
    '1': '2',
    '2': '3',
    '3': '1'
}


async def stop(request: Request):
    raise RuntimeError('stopped from user')


async def send(request: Request):
    await request.chat.send_message('lol', kb)


async def switch(r: Request):
    await r.user.update(state=states[r.user.state])
    await r.chat.send_message(f'switched', kb)
    await send_settings(r)


async def send_settings(r: Request):
    text = '\n'.join([
        f'id: {r.user.uid}',
        f'state: {r.user.state}',
    ])
    await r.chat.send_message(text, kb)


async def set_state(r: Request):
    state = next(iter(states))
    await r.user.update(state=state)
    await r.chat.send_message(f'hi, user {r.user.uid}', kb=kb)


router = Router({
    text_cond('send'): send,
    text_cond('stop'): stop,
    any_cond([state_cond(s) for s in states]): switch,
}, default=set_state)
