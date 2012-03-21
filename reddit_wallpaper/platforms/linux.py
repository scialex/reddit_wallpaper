# Copyright 2012, Alex Light.
#
# This file is part of Reddit background updater (RBU).
#
# RBU is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# RBU is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RBU.  If not, see <http://www.gnu.org/licenses/>.
#
try:
    from gi.repository.Gio import Settings
    _HAS_GI_SETTINGS = True
except (ImportError, AttributeError):
    _HAS_GI_SETTINGS = False

try:
    from gi.repository.GConf import Client
    _HAS_GI_GCONF = True
except (ImportError, AttributeError):
    _HAS_GI_GCONF = False

#gi and old bindings do not play well together so make them seperate
if not _HAS_GI_GCONF and not _HAS_GI_SETTINGS:
    try:
        import gconf
        _HAS_GCONF = True
    except ImportError:
        _HAS_GCONF = False
else: _HAS_GCONF = False


from .. import _exceptions
from ..loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY

_GCONF_KEY = '/desktop/gnome/background/picture_filename'#key to write new wallpaper to
_GSETTINGS_SCHEMA = "org.gnome.desktop.background" #schema for gsettings
_GSETTINGS_KEY = "picture-uri" #key for gsettings

DEFAULT_SAVE_LOCATION = '~/.background_getter/@'

def _log_succsess(conf, mod = None):
    msg = 'changed the background{0} succsessfully'
    if mod is not None:
        msg = msg.format(" ".join((" in",str(mod))))
    else:
        msg = msg.format("")
    conf.logger(DEBUG, msg)

def _log_failed(conf, mod = None):
    msg = 'was unable to change the background, {0}client reported failure of key setting.'
    if mod is not None:
        msg = msg.format(mod)
    else:
        msg = msg.format("")
    conf.logger(ERROR, msg)

def _gconf_old_set_as_background(conf, file_location):
    """Sets the background path to the given path"""
    client = gconf.client_get_default()
    worked = client.set_string(_GCONF_KEY, file_location)
    client.suggest_sync()
    if worked:
        _log_succsess(conf,"gconf")
    else:
        _log_failed(conf,"gconf")
        raise _exceptions.Failed("could not set gconf key")
    return

def _gi_gconf_set_as_background(conf, file_location):
    client = Client.get_default()
    worked = client.set_string(_GCONF_KEY, file_location)
    client.suggest_sync()
    if worked:
        _log_succsess(conf, "gi gconf")
    else:
        _log_failed(conf, "gi gconf")
        raise _exceptions.Failed("could not set gconf key")
    return

def _gsettings_set_as_background(conf, file_location):
    """Sets the background path to the given path in gsettings"""
    gsettings = Settings.new(_GSETTINGS_SCHEMA)
    worked = gsettings.set_string(_GSETTINGS_KEY,"file://"+file_location)
    # I do not think i need this sync command.
    gsettings.sync()
    if worked:
        _log_succsess(conf,"gsetting")
    else:
        _log_failed(conf,"gsettings")
        raise _exceptions.Failed("could not set gsettings key")
    return

def set_as_background(conf, file_location):
    thrown = True
    if _HAS_GI_SETTINGS:
        try:
            _gsettings_set_as_background(conf, file_location)
            thrown = False
        except _exceptions.Failed:
            pass
    if _HAS_GI_GCONF:
        try:
            _gi_gconf_set_as_background(conf, file_location)
            thrown = False
        except _exceptions.Failed:
            pass
    if _HAS_GCONF:
        try:
            _gconf_old_set_as_background(conf, file_location)
            thrown = False
        except _exceptions.Failed:
            pass
    if thrown:
        raise _exceptions.Failed("was unable to set background using any backend")
    return

__all__ = ['DEFAULT_SAVE_LOCATION', 'set_as_background']
