from bottex2.chat import Keyboard, Button
from bottex2.conditions import if_text_eq, if_any
from bottex2.ext.users import state_cond
from bottex2.handler import Request
from bottex2.router import Router

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
    return request.resp('lol', kb)


async def switch(r: Request):
    await r.user.update(state=states[r.user.state])
    await send_settings(r)
    return r.resp(f'switched', kb)


async def send_settings(r: Request):
    text = '\n'.join([
        f'id: {r.user.uid}',
        f'state: {r.user.state}',
    ])
    return r.resp(text, kb)


async def set_state(r: Request):
    state = next(iter(states))
    await r.user.update(state=state)
    return r.resp(f'hi, user {r.user.uid}', kb=kb)


router = Router({
    if_text_eq('send'): send,
    if_text_eq('stop'): stop,
    if_any([state_cond(s) for s in states]): switch,
}, default=set_state)
