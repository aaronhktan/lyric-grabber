# -*- mode: python -*-

block_cipher = None


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
a.datas += [('./assets/add_folder.png', './assets/add_folder.png', 'DATA')]
a.datas += [('./assets/add_music.png', './assets/add_music.png', 'DATA')]
a.datas += [('./assets/add_folder.png', './assets/add_folder.png', 'DATA')]
a.datas += [('./assets/art_empty.png', './assets/art_empty.png', 'DATA')]
a.datas += [('./assets/browser.png', './assets/browser.png', 'DATA')]
a.datas += [('./assets/complete.png', './assets/complete.png', 'DATA')]
a.datas += [('./assets/copy.png', './assets/copy.png', 'DATA')]
a.datas += [('./assets/delete.png', './assets/delete.png', 'DATA')]
a.datas += [('./assets/error.png', './assets/error.png', 'DATA')]
a.datas += [('./assets/finder.png', './assets/finder.png', 'DATA')]
a.datas += [('./assets/icon.png', './assets/icon.png', 'DATA')]
a.datas += [('./assets/in_progress.png', './assets/in_progress.png', 'DATA')]
a.datas += [('./assets/lyrics.png', './assets/lyrics.png', 'DATA')]
a.datas += [('./assets/not_started.png', './assets/not_started.png', 'DATA')]
a.datas += [('./assets/settings.png', './assets/settings.png', 'DATA')]
a.datas += [('./modules/settings.ini', './modules/settings.ini', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='quaver',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='quaver')
