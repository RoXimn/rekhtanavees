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

from rekhtanavees.misc.utils import hmsTimestamp

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
    words: list[Word] | None = None

    speakerId: PositiveInt | None = None
    tags: List[str] | None = None

    def __contains__(self, t: float):
        """Check if given time (in seconds) overlaps with this segment"""
        return self.start <= t <= self.end


# ******************************************************************************
def findSegment(segments: list[Segment], targetTime: float) -> int:
    """
    Performs a binary search on the sorted list Segments to find the target.

    Args:
        segments: The sorted list of Segments to search within.
        targetTime: The time stamp (in seconds) to search for.

    Returns:
        The index of the target Segment if found, otherwise -1.
    """
    low = 0
    high = len(segments) - 1

    while low <= high:
        mid = (low + high) // 2  # Calculate the middle index

        if targetTime in segments[mid]:
            return mid  # Target found at mid index
        elif segments[mid].end < targetTime:
            low = mid + 1  # Target is in the right half
        else:
            high = mid - 1  # Target is in the left half

    return -1  # Target not found in the list


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
    """Save the list of transcription Segments as JSON file"""
    assert isinstance(transcriptFile, Path)
    assert isinstance(segments, list)

    for s in segments:
        s.words = None

    ts = {"segments": [s.model_dump() for s in segments],
          "text": ''.join([s.text for s in segments])}
    transcriptFile.write_text(json.dumps(ts, ensure_ascii=False, indent=2),
                              encoding='utf-8')

# ******************************************************************************
def writeSrtFile(fname: str, subtitles: list[Segment]):
    """Write the list of subtitles to an SRT file.

    Args:
        fname (str): The name of the SRT file to create.
        subtitles (list): A list of segments.
    """
    with open(fname, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, start=1):
            f.write(f"{i}\n")
            f.write(f"{hmsTimestamp(int(sub.start * 1000))} --> {hmsTimestamp(int(sub.end * 1000))}\n")
            f.write(f"{sub.text}\n\n")

# ******************************************************************************
if __name__ == '__main__':
    pass


# ******************************************************************************
