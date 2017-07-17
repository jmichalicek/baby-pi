from amcrest import AmcrestCamera
import json
import time
import os
import subprocess


#kivy.require('1.10.0') # replace with your current kivy version !
from kivy.config import Config
Config.set('kivy', 'desktop', 1)
Config.set('kivy', 'exit_on_escape', 1)
Config.set('graphics', 'show_cursor', 1)
Config.set('graphics', 'fullscreen', 1)
Config.set('graphics', 'width',  800)
Config.set('graphics', 'height', 480)


import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window


import logging

logger = logging.getLogger(__name__)

# hard coding the UI for the raspberry pi 7" display which is 800x480
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

def handle_exit_button(instance):
    App.get_running_app().stop()

def handle_record_to_camera(instance):
    pass

def handle_record_to_pi(instance):
    pass


## move this elsewhere
layout_string = '''
<TouchEventLayout>:
    FloatLayout:
        spacing: 10
        size_hint: (.2, 1)
        Button:
            text: 'Exit'
            size_hint: (1, .1)
            pos_hint: {'top': 1}
            on_Press: handle_exit_button

        Button:
            text: 'Pan Up'
            size_hint: (1, .1)
            pos_hint: {top: .7}
            on_press: handle_pan_up
    FloatLayout:
        spacing: 10
        size_hint: (.8, 1)
'''


class OmxAmcrestCamera(AmcrestCamera):
    """

    AmcrestCamera extended with data for omxplayer for streaming
    """

    def __init__(self, name, player_window_position, *args, **kwargs):
        self.player_window_position = player_window_position
        self.omx_player = None
        self.name = name

        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def stop_omx_player(self):
        # using Popen.communicate() to send omxplayer the q (quit) command
        # quits omxplayer properly, but an exception is raised because omxplayer
        # quits and subprocess.Popen is still trying to work with it.
        # using stdin.write('q') theoretically should solve this problem, but as
        # the subprocess docs warn about, a deadlock occurs.
        # using terminate() or kill() end up disconnectng subprocess.Popen(), but
        # omxplayer continues to run.  So go with using communicate() and catch
        # the exception.
        # self.omx_player.stdin.write('q')
        # self.omx_player.wait()
        # self.omx_player.kill()
        try:
            self.omx_player.communicate(input='q')
        except ValueError:
            pass

    def create_omx_player_process(self):
        stream_url = self.camera.rtsp_url()
        self.omx_player = subprocess.Popen(['omxplayer', '--live', '--win', self.player_window_position, stream_url],
                                           stdin=subprocess.PIPE, universal_newlines=True)


class TouchEventLayout(GridLayout):
    """
    A layout to wrap everything which handles touch events
    """

    # This breaks out buttons in the controls layout...
    def on_touch_down(self, touch):
        # TODO:
        # check if coords within an omxplayer instance and set selected camera
        # for controls
        selected_camera = self.get_selected_camera(touch_pos=touch.pos)
        if selected_camera:
            App.get_running_app().selected_camera = selected_camera
            # stop processing touch
            return True

        # keep going
        return super().on_touch_down(touch)

    def get_selected_camera(self, touch_pos):
        click_x = touch_pos[0]
        click_y = touch_pos[1]
        
        # fiddle with mouse coordinates because the click coords from kivy have 0, 0 at bottom left
        # but the omxplayer positions being checked has 0, 0 at the top left.
        adjusted_click_y = Window.height - click_y
        selected_camera = None
        for camera in App.get_running_app().cameras:
            camera_coords = [float(p) for p in camera.player_window_position.split(' ')]
            if click_x >= camera_coords[0] and adjusted_click_y >= camera_coords[1] and click_x <= camera_coords[2] and adjusted_click_y <= camera_coords[3]:
                selected_camera = camera
        return selected_camera


class MonitorUI(App):
    """
    Kivy app to run the UI for Amcrest IP camera viewing using omxplayer
    for rtsp rather than kivy rtsp player.
    """
    title = 'Baby Pi'

    def __init__(self, config_file='', *args, **kwargs):
        self.camera_configs = []
        self.cameras = []
        self.selected_camera = None

        with open(config_file) as json_data:
            self.camera_configs = json.load(json_data)
        self.cameras = self.get_camera_instances()
        self.selected_camera = self.cameras[0]

        super().__init__()

    def press_zoom_in(self, instance):
        # TODO: figure out how to async the delay.  asyncio + kivy does not play nicely
        # due to network + camera response, this may actually zoom too fast
        # for the stop on release.  If that is the case then have this set a
        # `self.is_zooming` and loop with short .1 or .2 second delay doing
        # action start and action stop while self.is_zooming is true.
        # release_zoom_in() can then just set is_zooming to false.
        # if this is blocking then an alternate solution may be to play with zoom in speed
        self.selected_camera.camera.zoom_in(action='start')
        #time.sleep(0.5)
        #self.selected_camera.camera.zoom_in(action='stop')

    def release_zoom_in(self, instance):
        self.selected_camera.camera.zoom_in(action='stop')

    def press_zoom_out(self, instance):
        self.selected_camera.camera.zoom_out(action='start')

    def release_zoom_out(self, instance):
        self.selected_camera.camera.zoom_out(action='stop')

    def press_pan_up(self, instance):
        self.selected_camera.camera.move_up(action='start')

    def release_pan_up(self, instance):
        self.selected_camera.camera.move_up(action='stop')

    def press_pan_down(self, instance):
        self.selected_camera.camera.move_down(action='start')

    def release_pan_down(self, instance):
        self.selected_camera.camera.move_down(action='stop')

    def press_pan_left(self, instance):
        self.selected_camera.camera.move_left(action='start')

    def release_pan_left(self, instance):
        self.selected_camera.camera.move_left(action='stop')

    def press_pan_right(self, instance):
        self.selected_camera.camera.move_right(action='start')

    def release_pan_right(self, instance):
        self.selected_camera.camera.move_right(action='stop')

    def on_stop(self):
        for camera in self.cameras:
            camera.stop_omx_player()

    #def build(self, *args, **kwargs):
    #    Builder.load_string(layout_string)
    #    return TouchEventLayout()

    def build(self, *args, **kwargs):
    #    # TODO: Use the kivy KVL for this, not code.  It's getting gross.

        layout = TouchEventLayout(cols=3, rows=1, height=480, width=800)
        controls_layout_left = GridLayout(cols=1, width=200, height=480,  size_hint_x=None, size_hint_y=None)
        videos_layout = GridLayout(cols=1, width=400, height=480, size_hint_x=None, size_hint_y=None)
        controls_layout_right = GridLayout(cols=1, width=200, height=480, size_hint_x=None, size_hint_y=None)

        exit_button = Button(text='Exit', size_hint_x=1, size_hint_y=None, height=100)
        exit_button.bind(on_press=handle_exit_button)
        controls_layout_left.add_widget(exit_button)

        record_to_pi = Button(text='Record to Monitor', size_hint_x=1, size_hint_y=None, height=100)
        record_to_camera = Button(text='Record to Camera', size_hint_x=1, size_hint_y=None, height=100)
        snapshot_stream = Button(text='Snapshot', size_hint_x=1, size_hint_y=None, height=100)
        controls_layout_left.add_widget(record_to_pi)
        controls_layout_left.add_widget(record_to_camera)
        controls_layout_left.add_widget(snapshot_stream)

        zoom_in = Button(text='Zoom In', size_hint_x=1, size_hint_y=None, height=80)
        zoom_in.bind(on_press=self.press_zoom_in, on_release=self.release_zoom_in)
        controls_layout_right.add_widget(zoom_in)

        zoom_out = Button(text='Zoom Out', size_hint_x=1, size_hint_y=None, height=80)
        zoom_out.bind(on_press=self.press_zoom_out, on_release=self.release_zoom_out)
        controls_layout_right.add_widget(zoom_out)

        pan_up = Button(text='Pan Up', size_hint_x=1, size_hint_y=None, height=80)
        pan_up.bind(on_press=self.press_pan_up, on_release=self.release_pan_up)
        controls_layout_right.add_widget(pan_up)

        pan_down = Button(text='Pan Down', size_hint_x=1, size_hint_y=None, height=80)
        pan_down.bind(on_press=self.press_pan_down, on_release=self.release_pan_down)
        controls_layout_right.add_widget(pan_down)

        pan_left = Button(text='Pan Left', size_hint_x=1, size_hint_y=None, height=80)
        pan_left.bind(on_press=self.press_pan_left, on_release=self.release_pan_left)
        controls_layout_right.add_widget(pan_left)

        pan_right = Button(text='Pan Right', size_hint_x=1, size_hint_y=None, height=80)
        pan_right.bind(on_press=self.press_pan_right, on_release=self.release_pan_right)
        controls_layout_right.add_widget(pan_right)

        layout.add_widget(controls_layout_left)
        layout.add_widget(videos_layout)
        layout.add_widget(controls_layout_right)

        return layout 


    def get_camera_instances(self):
        # for now this will be a list which is parallel to the configs, but
        # may change these to working off of ordered dicts.
        cameras = []
        for conf in self.camera_configs:
            position = conf.get('position')
            camera = OmxAmcrestCamera(
                    name=conf.get('name', 'Missing Name'),
                    player_window_position=position, user=conf['user'], password=conf['password'], host=conf['host'],
                    port=80, protocol='http')
            camera.create_omx_player_process()
            cameras.append(camera)

        return cameras


if __name__ == '__main__':
    config_file = os.environ.get('BABY_PI_CONFIG', '')
    if not config_file:
        home = os.environ.get('HOME')
        config_file = os.path.abspath(os.path.join(home, '.amcrest_pi', 'cameras.json'))
    MonitorUI(config_file=config_file).run()
