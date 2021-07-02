"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Node Editor testing

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""
import hashlib
import importlib.util
import itertools
import logging
import subprocess
import threading
import webbrowser
from contextlib import contextmanager
from pathlib import Path

import dearpygui.dearpygui as dear
import numpy as np
import yaml
from dotmap import DotMap
from PIL import Image, JpegImagePlugin, PngImagePlugin
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from mmv.Common.PackUnpack import PackUnpack
from mmv.Common.Utils import Utils
from mmv.Editor.BaseNode import BaseNode
from mmv.Editor.Scene import mmvEditorScene
from mmv.Editor.UI.AddNodeUI import mmvEditorAddNodeUI
from mmv.Editor.UI.ExternalsUI import mmvEditorExternalsUI
from mmv.Editor.UI.MenuBarUI import mmvEditorMenuBarUI


class DotMapPersistentSetter:
    def __init__(self, dotmap): self.dotmap = dotmap
    def __call__(self, name, default_value):
        self.dotmap[name] = self.dotmap.get(name, default_value)
    def Set(self, key, value):
        print(f"[DotMapPersistentSetter.Set] {key} => {value}")
        self.dotmap[key] = value


class EnterContainerStack:
    def __init__(self, dpg_id):
        dear.push_container_stack(dpg_id)
    def __enter__(self): ...
    def __exit__(self, *args, **kwargs):
        dear.pop_container_stack()


@contextmanager
def CenteredWindow(Context, **k):
    try:
        # Default values
        for item, value in [
            ("modal",True), ("no_move",True),
            ("autosize",True), ("label","")
        ]:
            k[item] = k.get(item, value)

        # Add centered window
        window = dear.add_window(**k)
        dear.push_container_stack(window)
        dear.set_item_pos(
            item=window,
            pos=[
                ( Context.WINDOW_SIZE[0] - k.get("width", 0) - k.get("offx",0) ) / 2,
                ( Context.WINDOW_SIZE[1] - k.get("height",0) - k.get("offy",0) ) / 2,
            ])
        yield window
    finally: dear.pop_container_stack()


class PayloadTypes:
    Image  = "image"
    Shader = "shader"
    Number = "Number"


def WatchdogTemplate():
    T = PatternMatchingEventHandler(["*"], None, False, True)
    T.on_created  = lambda *args: None
    T.on_deleted  = lambda *args: None
    T.on_modified = lambda *args: None
    T.on_moved    = lambda *args: None
    return T


class mmvEditor:
    def __init__(self, PackageInterface):
        self.PackageInterface = PackageInterface
        self.LogoImage = self.PackageInterface.ImageDir/"mmvLogoWhite.png"
        self.LoadLastConfig()
        self.MenuBarUI = mmvEditorMenuBarUI(self)
        self.ExternalsUI = mmvEditorExternalsUI(self)
        self.AddNodeUI = mmvEditorAddNodeUI(self)
        self.Scene = mmvEditorScene(self)

        # Stuff we can access
        self.EnterContainerStack = EnterContainerStack
        self.PayloadTypes = PayloadTypes
        self.CenteredWindow = CenteredWindow
        self.AssignLocals = Utils.AssignLocals

        # Watch for Nodes directory changes
        self.WatchdogNodeDir = Observer()
        T = WatchdogTemplate()
        T.on_modified = lambda *args: self.AddNodeFilesDataDirRecursive()
        self.WatchdogNodeDir.schedule(T, self.PackageInterface.NodesDir, recursive=True)
        self.WatchdogNodeDir.start()

        # Interactive
        self.MouseDown = False
        self.ViewportX = 0
        self.ViewportY = 0

    # Attempt to load last Context configuration if it existed
    def LoadLastConfig(self, defaults = False):
        self.USER_CONFIG_FILE = self.PackageInterface.RuntimeDir/"UserEditorConfig.pickle.zlib"
        if self.USER_CONFIG_FILE.exists():
            self.Context = PackUnpack.Unpack(self.USER_CONFIG_FILE)
            logging.info(f"[mmvEditor.LoadLastConfig] Unpacked last config: [{self.Context}]")
        else: defaults = True
        
        # Create brand new Context DotMap
        if defaults: 
            logging.info(f"[mmvEditor.LoadLastConfig] Reset to default config")
            self.Context = DotMap(_dynamic=False)

        self.ContextSafeSetVar = DotMapPersistentSetter(self.Context)
        self.ContextSafeSetVar("FIRST_TIME", True)
        self.ContextSafeSetVar("WINDOW_SIZE", [1280, 720])
        self.ContextSafeSetVar("BUILTIN_WINDOW_DECORATORS", True)
        self.ContextSafeSetVar("STARTUP_MAXIMIZE", True)
        self.ContextSafeSetVar("UI_SOUNDS", True)
        self.ContextSafeSetVar("UI_VOLUME", 40)
        self.ContextSafeSetVar("UI_FONT", "DejaVuSans-Bold.ttf")
        self.ContextSafeSetVar("UI_FONT_SIZE", 16)
        self.ContextSafeSetVar("DEBUG_SHOW_IDS", True)

    # Play some sound from a file (usually UI FX, info, notification)
    def PlaySound(self, file):
        if self.Context.UI_SOUNDS:
            subprocess.Popen([
                self.PackageInterface.FFplayBinary, "-loglevel", "panic",
                "-hide_banner", "-volume", f"{self.Context.UI_VOLUME}", 
                "-nodisp", "-autoexit", Path(file).resolve()], stdout=subprocess.DEVNULL)

    # Adds a image on current DPG stack, returns the raw numpy array of its content and the
    # assigned DearPyGui id
    def AddImageWidget(self, path, size=100) -> np.ndarray:
        self.ToggleLoadingIndicator()
        img = Image.open(path).convert("RGBA")
        original_image_data = np.array(img)
        width, height = img.size
        ratio = width / height
        img = img.resize((int(size*ratio), int(size)), resample=Image.LANCZOS)
        width, height = img.size
        data = np.array(img).reshape(-1)
        tex = dear.add_dynamic_texture(width, height, list(data/256), parent=self.TextureRegistry)
        dpg_widget = dear.add_image(tex)
        self.ToggleLoadingIndicator()
        return original_image_data, dpg_widget

    # Dynamically import a file from a given Path
    def ImportFileFromPath(self, path):
        logging.info(f"[mmvEditor.ImportFileFromPath] Import file [{path}]")
        spec = importlib.util.spec_from_file_location(f"DynamicImport[{path}]", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # Add some Node file to the Editor
    def AddNodeFile(self, path):
        path = Path(path).resolve(); assert path.exists
        node = self.ImportFileFromPath(path).GetNode(BaseNode)
        node.hash = hashlib.sha256(Path(path).read_text().encode()).hexdigest()
        logging.info(f"[mmvEditor.AddNodeFile] Add node [{node.name}] category [{node.category}] from [{path}]")
        self.Scene.AvailableNodes[node.category][node.name] = node

    # Re-read the node files from NodeDir, add (replace) them.
    # Also resets the NodeUI items and redisplays the ones we have
    def AddNodeFilesDataDirRecursive(self, render=True):
        self.ToggleLoadingIndicator()
        logging.info("[mmvEditor.AddNodeFilesDataDirRecursive] Reloading..")
        self.Scene.ClearAvailableNodes()
        for candidate in self.PackageInterface.NodesDir.rglob("**/*.py"): self.AddNodeFile(candidate)
        if render: self.AddNodeUI.Reset(); self.AddNodeUI.Render()
        self.ToggleLoadingIndicator()

    def _log_sender_data(self, sender, app_data, user_data=None):
        logging.info(f"[mmvEditor Event Log] Sender: [{sender}] | App Data: [{app_data}] | User Data: [{user_data}]")
    
    # user_data is "pointer" to some Node class
    def AddNodeToEditor(self, sender, app_data, node, *a,**k):
        print("ADDD", a, k)
        self._log_sender_data(sender, app_data, node)
        node.Init(self)
        self.Scene.Nodes.append(node)
        node.Render(parent=self.DPG_NODE_EDITOR)
    
    # Some Node was linked
    def NodeLinked(self, sender, app_data):
        dpfx = f"[mmvEditor.NodeLinked] [Sender: {sender}]"
        logging.info(f"{dpfx} Link {app_data}")
        N1, N2 = app_data
        dear.add_node_link(N1, N2, parent=sender)
        if not N1 in self.Scene.Links: self.Scene.Links[N1] = []
        if not N2 in self.Scene.Links[N1]: self.Scene.Links[N1] += [N2]
        logging.info(f"{dpfx} Links: {self.Scene.Links}")
        self.NodeLinksDebug()
        self.PlaySound(self.PackageInterface.DataDir/"Sound"/"connect.ogg")
    
    # Some Node was delinked
    def NodeDelinked(self, sender, app_data):
        logging.info(f"[mmvEditor.NodeLinked] [Sender: {sender}] Delink {app_data}")
        dear.delete_item(app_data)
        self.NodeLinksDebug()

    # [Debug] Show Node connections
    def NodeLinksDebug(self):
        logging.info(f"[mmvEditor.NodeLinksDebug] Connections:")
        for line in yaml.dump(self.Scene.Links, default_flow_style=True, width=50, indent=2).split("\n"):
            if line: logging.info(f"[mmvEditor.NodeLinksDebug] {line}")

    # Init the main Window but Async
    def InitMainWindowAsync(self):
        self.MainThread = threading.Thread(target=self.InitMainWindow, daemon=True).start()

    # Wrapper for calling dear.add_theme_color or dear.add_theme_style inputting a string
    def SetDearPyGuiThemeString(self, key, value):
        target = dear.__dict__[key]
        if not isinstance(value, list): value = [value]
        category = 2 if "Node" in key else 0
        if "Col_" in key: dear.add_theme_color(target, value, category=category)
        if "StyleVar_" in key: dear.add_theme_style(target, *value, category=category)

    # # Loops, Layout

    # Create DearPyGui items
    def InitMainWindow(self):
        dpfx = "[mmvEditor.InitMainWindow]"

        # Add node files we have, but don't render it
        self.AddNodeFilesDataDirRecursive(render=False)
  
        # Load theme YAML, set values
        with dear.theme(default_theme=True) as self.DPG_THEME:
            self.ThemeYaml = DotMap( yaml.load(Path(self.PackageInterface.DataDir/"Theme.yaml").read_text(), Loader = yaml.FullLoader) )
            for key, value in self.ThemeYaml.Global.items():
                logging.info(f"{dpfx} Customize Theme [{key}] => [{value}]")
                self.SetDearPyGuiThemeString(key, value)
                
        # Load font, add circles unicode
        with dear.font_registry() as self.DPG_FONT_REGISTRY:
            logging.info(f"{dpfx} Loading Interface font")
            self.DPG_UI_FONT = dear.add_font(
                self.PackageInterface.DataDir/"Fonts"/self.Context.UI_FONT, self.Context.UI_FONT_SIZE, default_font=True)
            dear.add_font_chars([
                0x2B24, # ⬤ Large Black Circle
                0x25CF, # ●  Black Circle
            ], parent=self.DPG_UI_FONT)

        # Handler
        with dear.handler_registry() as self.DPG_HANDLER_REGISTRY: ...
            # dear.add_mouse_drag_handler(0, callback=self._MouseWentDrag)

        # Creating main window
        with dear.window(
            width=int(self.Context.WINDOW_SIZE[0]),
            height=int(self.Context.WINDOW_SIZE[1]),
            on_close=self.Exit, no_scrollbar=True
        ) as self.DPG_MAIN_WINDOW:
            # Main Loop thread
            threading.Thread(target=self.MainLoop).start()

            dear.set_primary_window(self.DPG_MAIN_WINDOW, True)
            # dear.add_resize_handler(self.DPG_MAIN_WINDOW, callback=self.MainWindowResized)
            dear.configure_item(self.DPG_MAIN_WINDOW, menubar=True)
            dear.configure_item(self.DPG_MAIN_WINDOW, no_resize=True)
            dear.configure_item(self.DPG_MAIN_WINDOW, no_resize=True)

            # # Render stuff
            self.MenuBarUI.Render()

            with dear.child(border = False, height = -28):
                with dear.tab_bar() as self.DPG_MAIN_TAB_BAR:
                    with dear.tab(label="Node Editor") as self.DPG_NODE_EDITOR_TAB:

                        with dear.table(header_row=False, no_clip=True, precise_widths=True):
                            dear.add_table_column(width_fixed=False)

                            with dear.table(header_row=False, no_clip=True, precise_widths=True):
                                dear.add_table_column()
                                
                                dear.add_button(label="A")
                                dear.add_same_line()
                                dear.add_button(label="B")
                                dear.add_same_line()
                                dear.add_button(label="C")
                                dear.add_same_line()
                                dear.add_button(label="D")
                                dear.add_same_line()
                                dear.add_button(label="E")
                                dear.add_same_line()
                                dear.add_button(label="F")
                                dear.add_same_line()

                                dear.add_table_next_column()
                                with dear.table(header_row=False, no_clip=True, precise_widths=True):
                                    dear.add_table_column(width_fixed=True)
                                    dear.add_table_column()
                                    dear.add_table_column(width_fixed=True)
                                    
                                    self.AddNodeUI.Here()
                                    self.AddNodeUI.Render()

                                    dear.add_table_next_column()
                                    with dear.child(border = False, height = -14):
                                        with dear.node_editor(callback=self.NodeLinked, delink_callback=self.NodeDelinked) as self.DPG_NODE_EDITOR: ...

                                    dear.add_table_next_column()
                                    dear.add_text("Hello I'll be toolbar")
                                    dear.add_table_next_column()
                            # # Footer
                            dear.add_table_next_column()
                            dear.add_same_line()

                    with dear.tab(label="Live Config") as self.DPG_LIVE_CONFIG_TAB: ...
                    with dear.tab(label="Export") as self.DPG_EXPORT_TAB: ...
                    with dear.tab(label="Performance") as self.DPG_PERFORMANCE_TAB: ...
            
            dear.add_separator()
            self.DPG_LOADING_INDICATOR_GLOBAL = dear.add_loading_indicator(radius=1.4, color=(0,0,0,0), secondary_color=(0,0,0,0), speed=2, circle_count=10)
            self.ToggleLoadingIndicator()
            dear.add_same_line()
            dear.add_text(f"MMV v{self.PackageInterface.VersionNumber}", color = (230,70,75))
            dear.add_same_line()
            dear.add_text(f" | ", color = (80,80,80))
            dear.add_same_line()
            self.DPG_CURRENT_PRESET_TEXT = dear.add_text(f"\"{self.Scene.PresetName}\"")
            dear.add_same_line()
            dear.add_text(f" | ", color = (80,80,80))
            dear.add_same_line()
            self.DPG_NOTIFICATION_TEXT = dear.add_text("", color=(140,140,140))

        # # Custom StreamHandler logging class for updating the DPG text to show latest
        # notifications on the UI for the user
        class UpdateUINotificationDPGTextHandler(logging.StreamHandler):
            def __init__(self, mmv_editor): self.mmv_editor = mmv_editor
            def write(self, message): dear.configure_item(self.mmv_editor.DPG_NOTIFICATION_TEXT, default_value=f"{message}")
            def flush(self, *args, **kwargs): ...

        # Add the handler
        logging.getLogger().addHandler(logging.StreamHandler(
            stream=UpdateUINotificationDPGTextHandler(mmv_editor=self)))
    
    # Toggle the loading indicator on the main screen to show we are doing something
    def ToggleLoadingIndicator(self, force: bool = None):
        if not hasattr(self, "_ToggleLoadingIndicator"): self._ToggleLoadingIndicator = False
        P, S, NO = (255,51,55,255), (29,151,236,100), (0,0,0,0)
        if force: self._ToggleLoadingIndicator = force
        if not hasattr(self, "DPG_LOADING_INDICATOR_GLOBAL"): return
        if self._ToggleLoadingIndicator: dear.configure_item(self.DPG_LOADING_INDICATOR_GLOBAL, color=P, secondary_color=S)
        else: dear.configure_item(self.DPG_LOADING_INDICATOR_GLOBAL, color=NO, secondary_color=NO)
        self._ToggleLoadingIndicator = not self._ToggleLoadingIndicator

    # Handler when window was resized
    def ViewportResized(self, _, Data):
        self.Context.WINDOW_SIZE = Data[0], Data[1]
        # dear.configure_item(self.DPG_MAIN_WINDOW, max_size=self.Context.WINDOW_SIZE)

    # def MainWindowResized(self, _, Data):
    #     dear.configure_viewport(self.Viewport, width=Data[0], height=Data[1])

    def MainLoop(self):
        logging.info(f"[mmvEditor.MainLoop] Enter MainLoop, start MMV")
        self.__Stop = False
        self.Viewport = dear.create_viewport(
            title="Modular Music Visualizer Editor",
            caption=not self.Context.BUILTIN_WINDOW_DECORATORS,
            resizable=True, border=False)
        dear.set_viewport_resize_callback(self.ViewportResized)
        dear.setup_dearpygui(viewport=self.Viewport)
        dear.show_viewport(self.Viewport)
        with dear.texture_registry() as self.TextureRegistry: ...
        # if self.Context.STARTUP_MAXIMIZE: dear.maximize_viewport()
        try:
            for iteration in itertools.count(1):
                if (self.__Stop) or (not dear.is_dearpygui_running()): break
                self.Next(iteration)
                dear.render_dearpygui_frame()
        except KeyboardInterrupt: pass
        self.__True_Exit()

    def Next(self, iteration):
        if iteration == 3:
            self.FirstTimeWarning()

    def Exit(self): self.__Stop = True
    def __True_Exit(self):
        logging.info(f"[mmvEditor.AddNodeFile] Exiting [Modular Music Visualizer Editor] *Safely*")
        self.Context = PackUnpack.Pack(self.Context, self.USER_CONFIG_FILE)
        dear.cleanup_dearpygui()






    # First time opening MMV warning
    def __FirstTimeWarningOK(self, _): self.ContextSafeSetVar.Set("FIRST_TIME", False); dear.delete_item(_)
    def FirstTimeWarning(self):
        if self.Context.FIRST_TIME:
            with self.CenteredWindow(self.Context, width=400, height=100) as _:
                dear.add_text((
                    "Hello first time user!!\n\n"
                    "Modular Music Visualizer is Free Software\n"
                    "distributed under the GPLv3 License.\n\n"
                ))
                dear.add_button(label='Close', callback=lambda d,s: self.__FirstTimeWarningOK(_))