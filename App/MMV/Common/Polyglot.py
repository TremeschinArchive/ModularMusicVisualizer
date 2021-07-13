"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Translations support for static text, a good way for new contributors
helping accessibility

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
from pathlib import Path

import yaml
from dotmap import DotMap


class Language:
    def __str__(self): return f"[{self.EnName}] | [{self.NativeName}] | Language"
    def __init__(self, EnName, NativeName, LanguageCode, CountryFlag, Font):
        self.EnName = EnName
        self.NativeName = NativeName
        self.LanguageCode = LanguageCode
        self.CountryFlag = CountryFlag
        self.Font = Font

# Prefer in order of most spoken, not only native L1 but L1+L2 speakers
class Languages:
#---------------------------------------------------------------------------------------------------------------------------------------
#                         | English Name             | Native Name             | Language Code   | Country Flag   | Font
#---------------------------------------------------------------------------------------------------------------------------------------
    English    = Language("English",                 "English",                "en-us",          "us",            "DejaVuSans-Bold.ttf")
    Hindi      = Language("Hindi",                   "हिंदी",                    "hi",             "in",            "unifont-13.0.06.ttf")
    Spanish    = Language("Spanish",                 "Español",                "es",             "es",            "DejaVuSans-Bold.ttf")
    French     = Language("French",                  "Français",               "fr",             "fr",            "DejaVuSans-Bold.ttf")
    Russian    = Language("Russian",                 "русский",                "ru",             "ru",            "DejaVuSans-Bold.ttf")
    Portuguese = Language("Brazillian Portuguese",   "Português Brasileiro",   "pt-br",          "br",            "DejaVuSans-Bold.ttf")
    German     = Language("German",                  "Deutsch",                "de",             "de",            "DejaVuSans-Bold.ttf")
    Japanese   = Language("Japanese",                "日本語",                  "ja",             "jp",            "unifont-13.0.06.ttf")
    Korean     = Language("Korean",                  "한국어",                  "kr",             "kr",            "unifont-13.0.06.ttf")
    Italian    = Language("Italian",                 "Italiano",               "it",             "it",            "DejaVuSans-Bold.ttf")

 
class PolyglotBrain:
    def Init(self, LangsYamlPath, SpokenLanguage=Languages.English):
        Data = Path(LangsYamlPath).resolve().read_text(encoding="utf-8")
        self.Data = DotMap(yaml.load(Data, Loader = yaml.FullLoader), _dynamic=False)
        self.SpokenLanguage = SpokenLanguage

    def __call__(self, Phrase, ForceLanguage=None):
        if ForceLanguage is None:
            GetL = self.SpokenLanguage
        else:
            GetL = ForceLanguage
        Have = self.Data.get(Phrase, {}).get(GetL.LanguageCode, None)
        if (not Have) and (GetL.EnName != Languages.English.EnName): 
            logging.warning(f"[PolyglotBrain] I don't know [{Phrase}] in {GetL.EnName} ({GetL.NativeName})")
        if Have: return Have
        return Phrase

    # Change language
    def Language(self, SpokenLanguage):
        self.SpokenLanguage = SpokenLanguage

class Polyglot:
    Speak = PolyglotBrain()
    Languages = Languages
    ICanSpeak = [
        Languages.English,
        Languages.Portuguese,
        Languages.Japanese,
    ]
