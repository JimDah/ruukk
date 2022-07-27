# -*- coding: utf-8 -*-
import xbmc

from base import DefaultWindowReader, NullReader, KeymapKeyInputReader
from progressdialog import ProgressDialogReader
from virtualkeyboard import VirtualKeyboardReader
from pvrguideinfo import PVRGuideInfoReader
from textviewer import TextViewerReader
from busydialog import BusyDialogReader
from contextmenu import ContextMenuReader
from pvr import PVRWindowReader
from weather import WeatherReader
from playerstatus import PlayerStatusReader
from settings import SettingsReader
from selectdialog import SelectDialogReader
from yesnodialog import YesNoDialogReader

READERS = (
    KeymapKeyInputReader,
    DefaultWindowReader,
    NullReader,
    ProgressDialogReader,
    VirtualKeyboardReader,
    PVRGuideInfoReader,
    TextViewerReader,
    BusyDialogReader,
    ContextMenuReader,
    PVRWindowReader,
    WeatherReader,
    PlayerStatusReader,
    SettingsReader,
    YesNoDialogReader,
    SelectDialogReader
)

READERS_WINID_MAP = {
                10004: SettingsReader, #settings
                10012: SettingsReader, #picturesettings
                10013: SettingsReader, #programsettings
                10014: SettingsReader, #weathersettings
                10015: SettingsReader, #musicsettings
                10016: SettingsReader, #systemsettings
                10017: SettingsReader, #videosettings
                10018: SettingsReader, #servicesettings
                10019: SettingsReader, #appearancesettings
                10021: SettingsReader, #livetvsettings
                10034: SettingsReader, #profilesettings
                14000: SettingsReader, #pvrclientspecificsettings
                10100: YesNoDialogReader, #yesnodialog
                10101: ProgressDialogReader,
                10103: VirtualKeyboardReader,
                10106: ContextMenuReader,
                10109: VirtualKeyboardReader,
                10120: PlayerStatusReader, #musicosd
                10123: SettingsReader, #osdvideosettings
                10124: SettingsReader, #osdaudiosettings
                10131: SettingsReader, #locksettings
                10132: SettingsReader, #contentsettings
                10138: BusyDialogReader,
                10140: SettingsReader, #addonsettings
                10147: TextViewerReader,
                10150: SettingsReader, #peripheralsettings
                10601: PVRWindowReader,
                10602: PVRGuideInfoReader,
                12000: SelectDialogReader,
                12002: YesNoDialogReader,
                12005: PlayerStatusReader, #fullscreenvideo
                12006: PlayerStatusReader, #visualization
                12600: WeatherReader,
                12901: SettingsReader, #videoosd
}

READERS_MAP = {}
for r in READERS: READERS_MAP[r.ID] = r

def getWindowReader(winID):
    reader = xbmc.getInfoLabel('Window({0}).Property(TTS.READER)'.format(winID))
    if reader and reader in READERS_MAP:
        return READERS_MAP[reader]
    return READERS_WINID_MAP.get(winID,DefaultWindowReader)