# -*- coding: utf-8 -*-
from lib import util
from base import LogOnlyTTSBackend
from nvda import NVDATTSBackend
from festival import FestivalTTSBackend
from pico2wave import Pico2WaveTTSBackend
from flite import FliteTTSBackend
from osxsay import OSXSayTTSBackend
from sapi import SAPITTSBackend
from espeak import ESpeakTTSBackend, ESpeakCtypesTTSBackend
from speechdispatcher import SpeechDispatcherTTSBackend
from jaws import JAWSTTSBackend

backendsByPriority = [JAWSTTSBackend,NVDATTSBackend,SAPITTSBackend,SpeechDispatcherTTSBackend,FliteTTSBackend,ESpeakTTSBackend,Pico2WaveTTSBackend,FestivalTTSBackend,OSXSayTTSBackend,ESpeakCtypesTTSBackend,LogOnlyTTSBackend]

def selectVoice(provider):
	import xbmcgui
	voices = None
	bClass = getBackendByProvider(provider)
	if bClass:
		b = bClass()
		voices = b.voices()
	if not voices:
		xbmcgui.Dialog().ok('Not Available','No voices to select.')
		return
	idx = xbmcgui.Dialog().select('Choose Voice',voices)
	if idx < 0: return
	voice = voices[idx]
	util.LOG('Voice for {0} set to: {1}'.format(b.provider,voice))
	util.setSetting('voice.{0}'.format(b.provider),voice)
		
def getBackend():
	provider = util.getSetting('backend')
	b = getBackendByProvider(provider)
	if not b or not b._available():
 		for b in backendsByPriority:
			if b._available(): break
	return b
			
def getBackendByProvider(name):
	if name == 'auto': return None
	for b in backendsByPriority:
		if b.provider == name and b._available():
			return b
	return None
