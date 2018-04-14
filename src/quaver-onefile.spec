# -*- mode: python -*-

block_cipher = None
import sys

a = Analysis(['quaver.py'],
             pathex=['/Users/aaron/Documents/Github/lyric-grabber/src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
a.datas += [('./assets/add_folder.png', './assets/add_folder.png', 'DATA'),
            ('./assets/add_folder_inverted.png', './assets/add_folder_inverted.png', 'DATA'),
            ('./assets/add_music.png', './assets/add_music.png', 'DATA'),
            ('./assets/add_music_inverted.png', './assets/add_music_inverted.png', 'DATA'),
            ('./assets/add_folder.png', './assets/add_folder.png', 'DATA'),
            ('./assets/add_folder_inverted.png', './assets/add_folder_inverted.png', 'DATA'),
            ('./assets/art_empty.png', './assets/art_empty.png', 'DATA'),
            ('./assets/complete.png', './assets/complete.png', 'DATA'),
            ('./assets/copy.png', './assets/copy.png', 'DATA'),
            ('./assets/copy_inverted.png', './assets/copy_inverted.png', 'DATA'),
            ('./assets/delete.png', './assets/delete.png', 'DATA'),
            ('./assets/delete_inverted.png', './assets/delete_inverted.png', 'DATA'),
            ('./assets/error.png', './assets/error.png', 'DATA'),
            ('./assets/finder.png', './assets/finder.png', 'DATA'),
            ('./assets/icon.png', './assets/icon.png', 'DATA'),
            ('./assets/in_progress.png', './assets/in_progress.png', 'DATA'),
            ('./assets/lyrics.png', './assets/lyrics.png', 'DATA'),
            ('./assets/lyrics_inverted.png', './assets/lyrics_inverted.png', 'DATA'),
            ('./assets/not_started.png', './assets/not_started.png', 'DATA'),
            ('./assets/settings.png', './assets/settings.png', 'DATA'),
            ('./assets/settings_inverted.png', './assets/settings_inverted.png', 'DATA'),
            ('./modules/settings.ini', './modules/settings.ini', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
if sys.platform == 'darwin':
  exe = EXE(pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            name='Quaver',
            debug=False,
            strip=False,
            upx=True,
            runtime_tmpdir=None,
            console=True,
            icon='assets/icon.icns')
elif sys.platform == 'win32':
  exe = EXE(pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            name='Quaver',
            debug=False,
            strip=False,
            upx=True,
            runtime_tmpdir=None,
            console=False,
            icon='assets/icon.ico')

# Build a .app if on OS X
if sys.platform == 'darwin':
   app = BUNDLE(exe,
                name='Quaver.app',
                info_plist={
                  'NSHighResolutionCapable': 'True'
                },
                icon='assets/icon.icns')
