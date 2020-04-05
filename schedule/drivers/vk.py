import asyncio

from vk_api.keyboard import VkKeyboard as VkApiKeyboard, VkKeyboardColor as VkColor

from aiovk import TokenSession, API
from aiovk.longpoll import BotsLongPoll

from bases import rand
from bottex.utils import json
from bottex.messaging.drivers import AbstractDriver
from bottex.messaging.keyboard import Keyboard, Color
from bottex.messaging import Request

vk_empty_text = '\u200b'


class VkKeyboard(Keyboard):
    colors = {
        Color.RED: VkColor.NEGATIVE,
        Color.WHITE: VkColor.DEFAULT,
        Color.BLUE: VkColor.PRIMARY,
        Color.GREEN: VkColor.POSITIVE,
        None: VkColor.DEFAULT,
    }

    def __init__(self):
        self.kb = VkApiKeyboard()

    def add_button(self, button):
        self.kb.add_button(button.label, self.colors[button.color])

    def add_line(self):
        self.kb.add_line()

    def pop_line(self):
        self.kb.lines.pop()

    def get_str(self):
        return self.kb.get_keyboard()

    @classmethod
    def from_buttons(cls, button_lines):
        if button_lines is None:
            return ''
        self = cls()
        for line in button_lines:
            for button in line:
                self.add_button(button)
            self.add_line()
        self.pop_line()
        return self.get_str()


class VerticalKeyboard(VkKeyboard):
    @classmethod
    def from_buttons(cls, buttons):
        if buttons is None:
            return ''
        self = cls()
        for line in buttons:
            for button in line:
                self.add_button(button)
                self.add_line()
        self.pop_line()
        return self.get_str()


class VkDriver(AbstractDriver):
    site_name = 'vk'
    kb_class = VkKeyboard

    def __init__(self, name, config_filename):
        super().__init__(name)
        config = json.from_path(config_filename)
        session = TokenSession(access_token=config['token'])
        self.api = API(session)
        self.longpoll = BotsLongPoll(session, mode=0, group_id=config['group_id'])

    async def send_text(self, message, peer_id):
        if not message.text:
            message.text = '...'
        keyboard = self.create_kb(message.buttons)
        await self.api.messages.send(random_id=rand(),
                                     user_id=peer_id,
                                     message=message.text,
                                     # attachment=attachments,
                                     keyboard=keyboard)

    async def send(self, response, user):
        if response.messages:
            for msg in response[:-1]:
                await self.send_text(msg, user.uid)
            msg = response[-1]
            msg.buttons = response.buttons
            while True:
                try:
                    await self.send_text(msg, user.uid)
                    break
                except asyncio.TimeoutError:
                    pass

    async def listen(self):
        while True:
            try:
                response = await self.longpoll.wait(need_pts=True)
            except asyncio.TimeoutError:
                continue
            for event in response['updates']:
                if event['type'] == 'message_new':
                    msg = event['object']['message']
                    user_info = event['object']['client_info']
                    text, uid = msg['text'], msg['peer_id']
                    user = self.get_user(uid)
                    yield Request(user, text)
