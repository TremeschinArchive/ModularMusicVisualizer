"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: 

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
import logging

import dearpygui.dearpygui as Dear
from MMV.Common.DearPyGuiUtils import *
from MMV.Common.Polyglot import Polyglot

Speak = Polyglot.Speak

def ExternalsManagerDialog(Editor):
    logging.info(f"[ExternalsManagerDialog] Show Externals window")

    def DownloadSomething(TargetExternal, _ForceNotFound=False):
        Editor.ToggleLoadingIndicator()

        with DearCenteredWindow(
            Editor.Context, width=600, no_close=True,
        ) as DownloadWindow:
            Dear.add_text(Speak("Downloading") + f" [{TargetExternal}]")
            Dear.add_same_line();
            Dear.add_loading_indicator(**Editor.DearPyStuff.ThemeYaml.LoadingIndicator.Loading.toDict())
            ProgressBar = Dear.add_progress_bar(width=600)
            CurrentInfo = Dear.add_text(Speak("Requesting Download Info") + "..")

        def KeepUpdatingProgressBar(Status):
            Dear.configure_item(ProgressBar,
                label=Status.Name,
                default_value=Status.Completed
            )
            Dear.configure_item(CurrentInfo, default_value=Status.Info)

        Editor.PackageInterface.Externals.DownloadInstallExternal(
            TargetExternal=TargetExternal,
            Callback=KeepUpdatingProgressBar,
            _ForceNotFound=_ForceNotFound,
            Locale=Speak.SpokenLanguage.LanguageCode
        )

        Dear.delete_item(DownloadWindow)
        Editor.PackageInterface.FindExternals()
        ExternalsManagerDialog(Editor)
        Editor.ToggleLoadingIndicator()

    with DearCenteredWindow(
        Editor.Context, width=200,
        max_size=[10000, DearCenteredWindowsSuggestedMaxVSize(Editor.Context)]
    ) as ExternalsWindow:
        Dear.add_text(Speak("Externals Manager"), color = (Editor.DearPyStuff.ThemeYaml.mmvSectionText))

        Dear.add_text("FFmpeg: ")
        Dear.add_same_line()
        HaveFFmpeg = not Editor.PackageInterface.FFmpegBinary is None
        
        if HaveFFmpeg:
            Dear.add_text(Speak("Yes"), color=(Editor.DearPyStuff.ThemeYaml.mmvSectionText))
            Action = Speak("Reinstall")
        else:
            Dear.add_text("No, required for rendering videos", color=(255,0,0))
            Action = Speak("Download")

        Dear.add_same_line()
        Dear.add_button(label=Action, callback=
            lambda s,d: DownloadSomething(
                Editor.PackageInterface.Externals.AvailableExternals.FFmpeg,
                _ForceNotFound=HaveFFmpeg
            )
        )
