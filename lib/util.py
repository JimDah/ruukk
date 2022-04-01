# -*- coding: utf-8 -*-
import os, sys, re, xbmc, time, binascii, xbmcaddon

ADDON_ID = 'service.xbmc.tts'

def ERROR(txt,hide_tb=False,notify=False):
	if isinstance (txt,str): txt = txt.decode("utf-8")
	short = str(sys.exc_info()[1])
	if hide_tb:
		LOG('ERROR: {0} - {1}'.format(txt,short))
		return short
	LOG('ERROR: ' + txt)
	import traceback
	traceback.print_exc()
	if notify: showNotification('ERROR: {0}'.format(short))
	return short

def LOG(message):
	message = '{0}: {1}'.format(ADDON_ID,message)
	xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGNOTICE)

def sleep(ms):
	xbmc.sleep(ms)

def abortRequested():
	return xbmc.abortRequested

def info(key):
	return xbmcaddon.Addon(ADDON_ID).getAddonInfo(key)

def configDirectory():
	return profileDirectory()

def profileDirectory():
	return xbmc.translatePath(xbmcaddon.Addon(ADDON_ID).getAddonInfo('profile')).decode('utf-8')

def backendsDirectory():
	return os.path.join(xbmc.translatePath(info('path')).decode('utf-8'),'lib','backends')

def getTmpfs():
	for tmpfs in ('/run/shm','/dev/shm','/tmp'):
		if os.path.exists(tmpfs): return tmpfs
	return None

def playSound(name):
	wavPath = os.path.join(xbmc.translatePath('special://home').decode('utf-8'),'addons','service.xbmc.tts','resources','wavs','{0}.wav'.format(name))
	#wavPath = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8'),'resources','wavs','{0}.wav'.format(name))
	xbmc.playSFX(wavPath)

def showNotification(message,time_ms=3000,icon_path=None,header='XBMC TTS'):
	try:
		icon_path = icon_path or xbmc.translatePath(xbmcaddon.Addon(ADDON_ID).getAddonInfo('icon')).decode('utf-8')
		xbmc.executebuiltin('Notification({0},{1},{2},{3})'.format(header,message,time_ms,icon_path))
	except RuntimeError: #Happens when disabling the addon
		LOG(message)

def getXBMCVersion():
	import json
	resp = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
	data = json.loads(resp)
	if not 'result' in data: return None
	if not 'version' in data['result']: return None
	return data['result']['version']

XBMC_VERSION_TAGS = ('prealpha','alpha','beta','releasecandidate','stable')

def versionTagCompare(tag1,tag2):
	t1 = -1
	t2 = -1
	for i in range(len(XBMC_VERSION_TAGS)):
		if XBMC_VERSION_TAGS[i] in tag1: t1 = i
		if XBMC_VERSION_TAGS[i] in tag2: t2 = i
	if t1 < t2:
		return -1
	elif t1 > t2:
		return 1
	if tag1 < tag2:
		return -1
	elif tag1 > tag2:
		return 1
	return 0

def getXBMCVersionTag(tag):
	versionInfo = xbmc.getInfoLabel('System.BuildVersion')
	v_t_g = re.split('[- ]',versionInfo)
	if not len(v_t_g) > 1: return tag
	return v_t_g[1].lower()

def xbmcVersionGreaterOrEqual(major,minor=0,tag=None):
	version = getXBMCVersion()
	if not version: return False
	if major < version['major']:
		return True
	elif major > version['major']:
		return False
	if minor < version['minor']:
		return True
	elif minor > version['minor']:
		return False
	if not tag: return True
	vtag = getXBMCVersionTag(version.get('tag'))
	if not vtag: return True
	tagCmp = versionTagCompare(tag,vtag)
	return tagCmp < 1

def getSetting(key,default=None):
	setting = xbmcaddon.Addon(ADDON_ID).getSetting(key)
	return _processSetting(setting,default)

def _processSetting(setting,default):
	if not setting: return default
	if isinstance(default,bool):
		return setting.lower() == 'true'
	elif isinstance(default,float):
		return float(setting)
	elif isinstance(default,int):
		return int(float(setting or 0))
	elif isinstance(default,list):
		if setting: return binascii.unhexlify(setting).split('\0')
		else: return default
	
	return setting

def setSetting(key,value):
	value = _processSettingForWrite(value)
	xbmcaddon.Addon(ADDON_ID).setSetting(key,value)

def _processSettingForWrite(value):
	if isinstance(value,list):
		value = binascii.hexlify('\0'.join(value))
	elif isinstance(value,bool):
		value = value and 'true' or 'false'
	return str(value)

def isWindows():
	return sys.platform.lower().startswith('win')

def isOSX():
	return sys.platform.lower().startswith('darwin')

def isATV2():
	return xbmc.getCondVisibility('System.Platform.ATV2')

def isOpenElec():
	return xbmc.getCondVisibility('System.HasAddon(os.openelec.tv)')

def commandIsAvailable(command):
	for p in os.environ["PATH"].split(os.pathsep):
		if os.path.isfile(os.path.join(p,command)): return True
	return False

def _keymapTarget():
	return os.path.join(xbmc.translatePath('special://userdata').decode('utf-8'),'keymaps','service.xbmc.tts.keyboard.xml')

def _copyKeymap():
	import xbmcvfs
	targetPath = _keymapTarget()
	sourcePath = os.path.join(xbmc.translatePath(xbmcaddon.Addon(ADDON_ID).getAddonInfo('path')).decode('utf-8'),'resources','service.xbmc.tts.keyboard.xml')
	if os.path.exists(targetPath): xbmcvfs.delete(targetPath)
	return xbmcvfs.copy(sourcePath,targetPath)

def installKeymap():
	import xbmcgui
	success = _copyKeymap()
	if success:
		xbmcgui.Dialog().ok('Installed','Keymap installed successfully!','','Restart XBMC to use.')
	else:
		xbmcgui.Dialog().ok('Failed','Keymap installation failure.')

def updateKeymap():
	target = _keymapTarget()
	if os.path.exists(target):
		try:
			_copyKeymap()
		except:
			ERROR('Failed to update keymap')

def selectBackend():
	import backends
	import xbmcgui
	choices = ['auto']
	display = ['Auto']
	available = backends.getAvailableBackends()
	for b in available:
		choices.append(b.provider)
		display.append(b.displayName)
	idx = xbmcgui.Dialog().select('Choose Backend',display)
	if idx < 0: return
	setSetting('backend',choices[idx])
	
def selectPlayer(provider):
	import xbmcgui
	import backends
	players = backends.getPlayers(provider)
	if not players:
		xbmcgui.Dialog().ok('Not Available','No players to select.')
		return
	players.insert(0,('','Auto'))
	disp = []
	for p in players: disp.append(p[1])
	idx = xbmcgui.Dialog().select('Choose Player',disp)
	if idx < 0: return
	player = players[idx][0]
	LOG('Player for {0} set to: {1}'.format(provider,player))
	setSetting('player.{0}'.format(provider),player)
	
def selectSetting(provider,setting,*args):
	import xbmcgui
	import backends
	settingsList = backends.getSettingsList(provider,setting,*args)
	if not settingsList:
		xbmcgui.Dialog().ok('Not Available','No options to select.')
		return
	ids = []
	displays = []
	for ID,display in settingsList:
		ids.append(ID)
		displays.append(display)
	idx = xbmcgui.Dialog().select('Choose Option',displays)
	if idx < 0: return
	choice = ids[idx]
	LOG('Setting {0} for {1} set to: {2}'.format(setting,provider,choice))
	setSetting('{0}.{1}'.format(setting,provider),choice)
	
LAST_COMMAND_DATA = ''

def initCommands():
	global LAST_COMMAND_DATA
	LAST_COMMAND_DATA = ''
	setSetting('EXTERNAL_COMMAND','')

def sendCommand(command):
	commandData = '{0}:{1}'.format(time.time(),command)
	setSetting('EXTERNAL_COMMAND',commandData)

def getCommand():
	global LAST_COMMAND_DATA
	commandData = getSetting('EXTERNAL_COMMAND','')
	if commandData == LAST_COMMAND_DATA: return None
	LAST_COMMAND_DATA = commandData
	return commandData.split(':',1)[-1]

DEBUG = getSetting('debug_logging',True)
