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
from MMV.Editor.UI.Dialogs.PleaseRestart import PleaseRestartUI

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

        PleaseRestartUI(Editor, "Change Language")

    Editor.DearPyStuff.ToggleLoadingIndicator()

    with DearCenteredWindow(
        Editor.Context, width=300, height=200, min_size=[300,0],
        max_size=[10000, DearCenteredWindowsSuggestedMaxVSize(Editor.Context)]
    ) as LanguageSelectWindow:

        Dear.add_text(Speak("Select Language") + " | " + Speak("Missing") + f" [{len(Polyglot.Speak.UnknownPhrases)}]")
        Dear.add_separator()

        for Key, Value in Polyglot.Languages.__dict__.items():
            if (not "__" in Key) and (Key != "MakeCountries"):
                ThisLanguage = copy.deepcopy( Polyglot.Languages.__dict__[Key] )
                isThisLangSelected =  ThisLanguage.EnName == Editor.Context.DotMap.LANGUAGE.EnName

                # Add Flag button and text on the right
                Flag = Editor.PackageInterface.IconDir/"Flags"/f"{ThisLanguage.CountryFlag}.png"
                Flag = DearAddDynamicTexture(Flag, Editor.DearPyStuff.TextureRegistry, size=45+(20*isThisLangSelected))

                # Different Background to show that we are selected
                Dear.add_image_button(
                    texture_id=Flag,
                    user_data=ThisLanguage,
                    callback=lambda d,s,UserData: ConfigureLanguage(UserData, LanguageSelectWindow))
                Dear.add_same_line()
                with Dear.group():
                    NativeLangName = Dear.add_text(("● "*isThisLangSelected) + ThisLanguage.NativeName, color=(Editor.DearPyStuff.ThemeYaml.mmvSectionText))

                    # Percentage of completion of the language
                    Total = 0
                    Have = 0
                    for Key, Values in Polyglot.Speak.Data.items():
                        if (ThisLanguage.LanguageCode in [*Values, "en-us"]):
                            Have += len(Key)
                        Total += len(Key)
                    Total += len(Polyglot.Speak.UnknownPhrases)
                    Percentage = Have / Total
                    Dear.add_text(f"[{Percentage*100:06.2f} %] ", color=(120,120,120))
                    Dear.add_same_line()
                    PercentageTranslatedText = Dear.add_text(f"" + Speak("Translated", ForceLanguage=ThisLanguage), color=(120,120,120))
                for Item in [NativeLangName, PercentageTranslatedText]:
                    Dear.set_item_font(Item, Editor.DearPyStuff.LoadedFonts[ThisLanguage.Font])
                Dear.add_separator()

        Editor.DearPyStuff.ToggleLoadingIndicator()
