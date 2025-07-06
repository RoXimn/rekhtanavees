# -*- coding: utf-8 -*-

# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
"""YouTube source management module for audio extraction.

This module uses PyTube to download audio streams for processing.
"""
from enum import auto

from pytube import Playlist, YouTube, Stream
from strenum import StrEnum
import subprocess
import os
from pathlib import Path
from glob import glob
from tqdm import tqdm
from pydantic import BaseModel


demucs: str = r'd:\tools\stemroller-2.0.6-win-cuda\ThirdPartyApps\demucs-cxfreeze\demucs-cxfreeze.exe'
whisper: str = r'D:\tools\Faster-Whisper-XXL\faster-whisper-xxl.exe'
originalsDir: str = r'D:\tools\urdu-youtube\ertugrul-ghazi\downloads'
vocalsDir: str = r'D:\tools\urdu-youtube\ertugrul-ghazi'


ErtugrulGhazi: tuple[str, ...] = (
    'https://www.youtube.com/playlist?list=PLgirwYDDPtS2Tz7K6PZMYi_d8SeXQg-T5',
    'https://www.youtube.com/playlist?list=PLgirwYDDPtS05gyfru0ETfmc9B5Fgh2kM',
    'https://www.youtube.com/playlist?list=PLgirwYDDPtS1fWzj8IBUxjN07pF9Y9wdg',
    'https://www.youtube.com/playlist?list=PLgirwYDDPtS3xais5ixHnE5PXNn2-0c3_',
    'https://www.youtube.com/playlist?list=PLgirwYDDPtS0itM3thU7jV44cbcUCMiV1',
)


class DemucsModels(StrEnum):
    htdemucs = auto()
    """first version of Hybrid Transformer Demucs. 
    Trained on MusDB + 800 songs. Default model."""
    htdemucs_ft = auto()
    """fine-tuned version of htdemucs, separation will take 4 times more time 
    but might be a bit better. Same training set as htdemucs."""
    htdemucs_6s = auto()
    """6 sources version of htdemucs, with piano and guitar being added 
    as sources. Note that the piano source is not working great at the moment."""
    hdemucs_mmi = auto()
    """Hybrid Demucs v3, retrained on MusDB + 800 songs."""
    mdx = auto()
    """trained only on MusDB HQ, winning model on track A at the MDX challenge."""
    mdx_extra = auto()
    """trained with extra training data (including MusDB test set), ranked 2nd 
    on the track B of the MDX challenge."""
    mdx_q = auto()
    """quantized version fo mdx"""
    mdx_extra_q = auto()
    """quantized version fo mdx_extra"""


class Devices(StrEnum):
    cpu = auto()
    cuda = auto()
    cuda0 = 'cuda:0'
    cuda1 = 'cuda:1'
    cuda2 = 'cuda:2'
    cuda3 = 'cuda:3'
    cuda4 = 'cuda:4'
    cuda5 = 'cuda:5'


# ******************************************************************************
def walkdir(folder: str, ext: str):
    """Walk through each files in a directory and retrieve files of given ext"""
    for dirPath, dirs, files in os.walk(folder):
        for filename in files:
            filePath = os.path.abspath(os.path.join(dirPath, filename))
            if Path(filePath).suffix == ext:
                yield filePath


# ******************************************************************************
def downloadAudio():
    from pytube.innertube import _default_clients
    _default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]
    from tqdm import tqdm

    pp: list[list[int]] = []  # list of lengths of all videos in all playlists
    for p in tqdm([Playlist(pl) for pl in ErtugrulGhazi], desc='ErtugrulGhazi', unit='playlists'):  # type: Playlist
        vv: list[int] = []  # list of length of all videos in one playlist
        for v in tqdm(p.videos, desc=p.title, unit='videos'):  # type: YouTube
            vv.append(v.length)
            for s in v.streams.filter(only_audio=True):  # type: Stream
                if s:
                    with tqdm(desc=v.title, total=s.filesize, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                        v.register_on_progress_callback(lambda stream, chunk, remaining: pbar.update(len(chunk)))
                        s.download(output_path=originalsDir)
        pp.append(vv)

    print(pp, sum([sum(vv) for vv in pp]))


# ******************************************************************************
def separateVocals():
    # **************************************************************************
    MP3_BITRATE: int = 192
    MP3_PRESET: int = 2  # {2,3,4,5,6,7} Encoder preset of MP3, 2 for highest quality, 7 for fastest speed.
    DEVICE: Devices = Devices.cuda
    MODEL: DemucsModels = DemucsModels.htdemucs
    JOBS: int = 1
    os.chdir(originalsDir)
    filenames = [fn for fn in walkdir(originalsDir, ext='.mp4')]
    for fn in tqdm(filenames, unit='files', ncols=80):
        returnCode = subprocess.call([demucs,
                                      '--verbose',
                                      '--out', vocalsDir,
                                      # '--mp3',
                                      '--flac',
                                      # '--mp3-bitrate', MP3_BITRATE,
                                      # '--two-stems', 'vocals',
                                      '--filename', '{track}-{stem}.{ext}',
                                      '--device', str(DEVICE),
                                      '--name', str(MODEL),
                                      '--jobs', str(JOBS),
                                      fn])
        if returnCode == 0:
            for audioFile in glob(str(Path(vocalsDir) / str(MODEL) / f'{Path(fn).stem}*')):
                if Path(audioFile).stem[-7:] != '-vocals':
                    print(f'Deleting {audioFile}...')
                    os.unlink(audioFile)


# ******************************************************************************
def transcribeAudios():
    # **************************************************************************
    DEVICE: Devices = Devices.cuda
    os.chdir(originalsDir)
    filenames = [fn for fn in walkdir(originalsDir, ext='.mp4')]
    for fn in tqdm(filenames, unit='files', ncols=80):
        f = Path(fn)
        jf = Path(f.parent / f'{f.stem}.json')
        newName: Path = jf.parent / f'{jf.stem}-v2{jf.suffix}'
        if newName.exists():
            print(f'Skipping {newName!s}...')
            continue

        # Model large-v2
        subprocess.call([whisper,
                         '--verbose', 'True',
                         '--output_dir', originalsDir,
                         '--output_format', 'json',
                         '--device', str(DEVICE),
                         '--model', 'large-v2',
                         '--compute_type', 'int8_float32',
                         # '--best_of', '1',
                         # '--beam_size', '1',
                         # '-fallback', 'None',
                         # '--temperature', '0',
                         '--task', 'transcribe',
                         '--language', 'Urdu',
                         '--word_timestamps', 'True',
                         '--threads', '4',
                         '--vad_filter', 'True',
                         '--beep_off',
                         fn])

        print(f'renaming {jf!s}...')
        jf.rename(newName)

        # # Model large-v3
        # subprocess.call([whisper,
        #                  '--verbose', 'True',
        #                  '--output_dir', originalsDir,
        #                  '--output_format', 'json',
        #                  '--device', str(DEVICE),
        #                  '--model', 'large-v3',
        #                  '--compute_type', 'int8_float32',
        #                  # '--best_of', '1',
        #                  # '--beam_size', '1',
        #                  # '-fallback', 'None',
        #                  # '--temperature', '0',
        #                  '--task', 'transcribe',
        #                  '--language', 'Urdu',
        #                  '--word_timestamps', 'True',
        #                  '--threads', '4',
        #                  '--vad_filter', 'True',
        #                  '--beep_off',
        #                  fn])
        # f = Path(fn)
        # jf = Path(f.parent / f'{f.stem}.json')
        # print(f'renaming {jf!s}...')
        # jf.rename(jf.parent / f'{jf.stem}-v3{jf.suffix}')


# ******************************************************************************
if __name__ == '__main__':
    # downloadAudio()
    # separateVocals()
    transcribeAudios()


# ******************************************************************************
