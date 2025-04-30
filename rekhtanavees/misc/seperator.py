# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2024. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from demucs import separate


def clean(audioFilePath: str, stems: str = "vocals"):
    separate.main([
        "--mp3",
        "--two-stems", stems,
        "-n", "htdemucs_ft", audioFilePath])


if __name__ == '__main__':
    aufile = r'D:\tools\urdu-youtube\rahain\PTV Drama Serial Raahain Episode1 [CcIRyli25Uw].opus'

    clean(aufile)
