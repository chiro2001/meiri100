# -*- mode: python ; coding: utf-8 -*-

# block_cipher = pyi_crypto.PyiBlockCipher(key='chiro3521#*')
block_cipher = None

# find files
import os
files = []


def find(dir_name, origin=None, replace=None):
    if origin is None:
        origin = dir_name
    result = []
    if not os.path.exists(dir_name):
        return []
    li = os.listdir(dir_name)
    for i in li:
        path = os.path.join(dir_name, i)
        if os.path.isdir(path):
            result.extend(find(path, origin, replace))
            continue
        if replace is not None and path.startswith(origin):
            path2 = path[len(origin):]
            path2 = replace + path2
            result.append((path, os.path.dirname(path2)))
        else:
            result.append((path, os.path.dirname(path)))
    return result


files.extend(find('public'))
files.extend(find('../dist/chrome_pure', replace='chrome'))
print(files)



a = Analysis(['server.py'],
             pathex=['D:\\Programs\\group-buying-killer\\backend'],
             binaries=[],
             datas=files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='server',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='server')

