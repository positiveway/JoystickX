from controller import controller
from kivy.app import App
from garden_joystick import Joystick
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class ConnectionType:
    GREQ = 0
    SOCK = 2
    THREADED = 3
    AIOHTTP = 4


server_ip_num = 54
server_ip = f'192.168.1.{server_ip_num}'
server_port = 8000
server_address = f'http://{server_ip}:{server_port}'
endpoint_addr = f'{server_address}/send_letter'

CONNECTION_TYPE = ConnectionType.GREQ

if CONNECTION_TYPE == ConnectionType.GREQ:
    import grequests


    def send_letter(letter):
        rs = [grequests.post(endpoint_addr, json={'letter': letter})]
        grequests.map(rs)

elif CONNECTION_TYPE == ConnectionType.SOCK:
    import socket

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((server_ip, server_port))


    def send_letter(letter):
        pass

elif CONNECTION_TYPE == ConnectionType.THREADED:
    print('THREADED')
    import requests
    import threading


    def request_task(letter):
        requests.post(endpoint_addr, json={'letter': letter})


    def send_letter(letter):
        threading.Thread(target=request_task, args=[letter]).start()

elif CONNECTION_TYPE == ConnectionType.AIOHTTP:
    import aiohttp
    import asyncio
    from aiohttp import ClientConnectionError

    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession()


    async def _send(letter):
        try:
            await session.post(endpoint_addr, json={'letter': letter})
        except ClientConnectionError as err:
            pass


    def send_letter(letter):
        loop.run_until_complete(_send(letter))

else:
    raise NotImplemented()


def get_zone_number(attr_prefix):
    zone = controller.get_zone(attr_prefix)
    return {
        "🢂": 1,
        "🢅": 2,
        "🢁": 3,
        "🢄": 4,
        "🢀": 5,
        "🢇": 6,
        "🢃": 7,
        "🢆": 8,
        controller.NEUTRAL_ZONE: -1,
        controller.EDGE_ZONE: -2,
    }[zone]


class DemoApp(App):
    def build(self):
        self.root = BoxLayout()
        self.root.padding = 50

        left_joystick = Joystick()
        left_joystick.bind(pad=self.update_left)
        self.root.add_widget(left_joystick)
        self.left_label = Label()
        self.root.add_widget(self.left_label)

        right_joystick = Joystick()
        right_joystick.bind(pad=self.update_right)
        self.root.add_widget(right_joystick)
        self.right_label = Label()
        self.root.add_widget(self.right_label)

    def update_coordinates(self, joystick, pad, attr_prefix):
        x = str(pad[0])[0:5]
        y = str(pad[1])[0:5]
        radians = str(joystick.radians)[0:5]
        magnitude = str(joystick.magnitude)[0:5]
        angle = str(joystick.angle)[0:5]

        letter = controller.update_zone(joystick.magnitude, joystick.angle, attr_prefix)
        if letter:
            print(letter)

            letter = ord(letter[0])

        text = "Zone: {}\nletter: {}\nx: {}\ny: {}\nradians: {}\nmagnitude: {}\nangle: {}"

        return text.format(get_zone_number(attr_prefix), letter, x, y, radians, magnitude, angle)

    def update_left(self, joystick, pad):
        self.left_label.text = self.update_coordinates(joystick, pad, "Left")

    def update_right(self, joystick, pad):
        self.right_label.text = self.update_coordinates(joystick, pad, "Right")


class APISenderApp(App):
    def build(self):
        self.root = BoxLayout()
        self.root.padding = 50

        left_joystick = Joystick()
        left_joystick.bind(pad=self.update_left)
        self.root.add_widget(left_joystick)

        self.label = Label()
        self.root.add_widget(self.label)

        right_joystick = Joystick()
        right_joystick.bind(pad=self.update_right)
        self.root.add_widget(right_joystick)

    def update_coordinates(self, joystick, pad, attr_prefix):
        letter = controller.update_zone(joystick.magnitude, joystick.angle, attr_prefix)
        if letter:
            send_letter(letter)
            self.label.text = letter

    def update_left(self, joystick, pad):
        # send_letter('n')
        self.update_coordinates(joystick, pad, "Left")

    def update_right(self, joystick, pad):
        self.update_coordinates(joystick, pad, "Right")


def main():
    # DemoApp().run()
    APISenderApp().run()


if __name__ == '__main__':
    main()
