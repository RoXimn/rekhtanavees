# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2024. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
import json
import logging
from pathlib import Path
from typing import List

from pydantic import BaseModel, PositiveInt


# ******************************************************************************
class Word(BaseModel):
    """A transcribed word"""
    start: float
    end: float
    word: str
    probability: float


# ******************************************************************************
class Segment(BaseModel):
    """A transcribed segment"""
    id: int
    start: float
    end: float
    text: str
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    words: list[Word]

    speakerId: PositiveInt | None = None
    tags: List[str] | None = None


# ******************************************************************************
def loadTranscript(transcriptFile: Path) -> list[Segment]:
    """Load a transcript from a JSON file"""
    assert isinstance(transcriptFile, Path)
    assert transcriptFile.exists(), f"Transcript file does not exist: {transcriptFile}"

    segments = []
    try:
        j = json.loads(transcriptFile.read_text(encoding='utf-8'))
        segments = [Segment.model_validate(s) for s in j['segments']]
    except Exception as e:
        logging.error(f"Error parsing JSON from transcript file:({transcriptFile}: {e!s})")
    else:
        logging.debug(f"Parsed {len(segments)} segments from transcript file: {transcriptFile}")
    return segments


# ******************************************************************************
def saveTranscript(transcriptFile: Path, segments: list[Segment]) -> None:
    """"""
    assert isinstance(transcriptFile, Path)
    assert isinstance(segments, list)

    transcriptFile.write_text(json.dumps([s.model_dump() for s in segments]), encoding='utf-8')

# ******************************************************************************
if __name__ == '__main__':
    pass


# ******************************************************************************
