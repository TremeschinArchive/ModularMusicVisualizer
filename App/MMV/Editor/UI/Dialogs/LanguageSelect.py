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
import copy
import logging

import dearpygui.dearpygui as Dear
from MMV.Common.DearPyGuiUtils import *
from MMV.Common.Polyglot import Polyglot

Speak = Polyglot.Speak

def LanguageSelectUI(Editor):
    dpfx = "[LanguageSelectUI]"
    logging.info(f"{dpfx} Show Language Select")

    def ConfigureLanguage(UserData, LanguageSelectWindow):
        Dear.delete_item(LanguageSelectWindow)
        if UserData.EnName == Editor.Context.DotMap.LANGUAGE.EnName:
            logging.info(f"{dpfx} Already using language [{UserData}]")
            return
        logging.info(f"{dpfx} Configuring language [{UserData}]")
        Editor.Context.ForceSet("LANGUAGE", UserData)
        Polyglot.Speak.Language(UserData)
        Editor.DearPyStuff.UpdateLanguageButtonText()
        Editor.Context.ForceSet("UI_FONT", UserData.Font)

        with DearCenteredWindow(Editor.Context, width=500, height=200, min_size=[500,0]) as RestartWindow:
            A=Dear.add_text(Speak("We need to restart for language settings to take effect, proceed?"))
            B=Dear.add_button(label=Speak("Ok (Restart)"), callback=Editor.Restart)
            C=Dear.add_button(label=Speak("No (Continue)"), callback=lambda d,s,UserData: Dear.delete_item(RestartWindow))
            for Item in [A,B,C]:
                Dear.set_item_font(Item, Editor.LoadedFonts[UserData.Font])


    with DearCenteredWindow(
    Editor.Context, width=300, height=200, min_size=[300,0],
        max_size=[10000, DearCenteredWindowsSuggestedMaxVSize(Editor.Context)]
    ) as LanguageSelectWindow:
        Dear.add_text(Speak("Select Language [Needs Restart]"))
        Dear.add_separator()
        for Key, Value in Polyglot.Languages.__dict__.items():
            if not "__" in Key:
                ThisLanguage = copy.deepcopy( Polyglot.Languages.__dict__[Key] )

                # Add Flag button and text on the right
                Flag = Editor.PackageInterface.IconDir/"Flags"/f"{ThisLanguage.CountryFlag}.png"
                Flag = DearAddDynamicTexture(Flag, Editor.DearPyStuff.TextureRegistry, size=45)

                # Different Background to show that we are selected
                if ThisLanguage.EnName == Editor.Context.DotMap.LANGUAGE.EnName:
                    ImageButtonExtra = {}
                else:
                    ImageButtonExtra = dict(tint_color=[220]*3)
                Dear.add_image_button(
                    texture_id=Flag,
                    user_data=ThisLanguage,
                    **ImageButtonExtra,
                    callback=lambda d,s,UserData: ConfigureLanguage(UserData, LanguageSelectWindow))
                Dear.add_same_line()
                with Dear.group():
                    NativeLangName = Dear.add_text(("● "*(ImageButtonExtra=={})) + ThisLanguage.NativeName, color=(Editor.DearPyStuff.ThemeYaml.mmvSectionText))

                    # Percentage of completion of the language
                    Total = 0
                    Have = 0
                    for Key, Values in Polyglot.Speak.Data.items():
                        if (ThisLanguage.LanguageCode in [*Values, "en-us"]):
                            Have += len(Key)
                        Total += len(Key)
                    Percentage = Have / Total
                    Dear.add_text(f"[{Percentage*100:06.2f} %] ", color=(120,120,120))
                    Dear.add_same_line()
                    PercentageTranslatedText = Dear.add_text(f"" + Speak("Translated", ForceLanguage=ThisLanguage), color=(120,120,120))
                for Item in [NativeLangName, PercentageTranslatedText]:
                    Dear.set_item_font(Item, Editor.DearPyStuff.LoadedFonts[ThisLanguage.Font])
                Dear.add_separator()


