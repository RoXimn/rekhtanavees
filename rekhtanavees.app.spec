# ******************************************************************************
# Copyright (c) 2024. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
block_cipher = None

a = Analysis(['rekhtanavees/main.py'],
             pathex=[],
             binaries=None,
             datas=[],
             hiddenimports=[],
             hookspath=None,
             hooksconfig=None,
             runtime_hooks=None,
             cipher=block_cipher,
             excludes=['sphinx', 'autodoc-pydantic', 'sphinx-book-theme', 'pydata-sphinx-theme', 'sklearn', 'mypy'])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='rekhtanavees',
          debug=False,
          bootloader_ignore_signals=False,
          strip=True,
          upx=False,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None, icon='rekhtanavees/ui/icons/feather.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=False,
               upx_exclude=[],
               name='rekhtanavees')
