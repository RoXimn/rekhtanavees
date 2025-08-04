# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 202. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
"""Collection of miscellaneous helper functions.

This module contains assorted helper functions which do not yet have a
separate module.
"""
# ******************************************************************************
import re
import unicodedata
import string

# ******************************************************************************
MinimumValidChars: str = "-_.()" + string.ascii_letters + string.digits
"""Set of characters which can be universally used in names and titles."""
FilenameCharLimit: int = 255
"""Upper limit to filename length."""


# ******************************************************************************
def hmsTimestamp(milliseconds: int, shorten: bool = False, useDays: bool = False) -> str:
    """
    Converts milliseconds to timestamp format (HH:MM:SS,ms).

    Args:
      milliseconds (int): An integer representing the time in milliseconds.
      shorten (bool): Skip leading empty values.
      useDays (bool): Resolve hours into days

    Returns:
      Timestamp formated as (HH:MM:SS,ms).
    """
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if useDays:
        days, hours = divmod(hours, 24)
    else:
        days = 0

    if shorten:
        timestamp = ''
        if days:
            timestamp += f"{days}d "
        if hours:
            timestamp += f"{hours}:{minutes}:"
        elif minutes:
            timestamp += f"{minutes}:"
        timestamp += f"{seconds + milliseconds / 1000.0}"

    elif useDays:
        timestamp = f"{days}d {hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
    else:
        timestamp = f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    return timestamp


# ******************************************************************************
def isValidProjectName(name: str) -> bool:
    """Check the given name is valid to be used as a filename

    The name should be non-zero length of ascii upper(A-Z) and lower case(a-z)
    characters, digits (0-9), and `Space` character, in any order. The validation
    is done *after* stripping any leading or trailing whitespace from the given
    string.

    Args:
        name (str): the name to be validated. Validation is done *after*
            stripping any leading or trailing whitespace.

    Returns:
        bool: True if valid, False otherwise.
    """
    assert isinstance(name, str)
    return bool(re.search('^[A-Za-z0-9 _-]+$', name.strip()))


# ******************************************************************************
def slugify(name: str, whitelist: str = MinimumValidChars, replace: str = ' ') -> str:
    """Reduce given string to acceptable set of characters

    .. note::

        A *slug* is a short label for something, containing only letters, numbers,
        underscores or hyphens (as in `Django` docs).

    The characters matching the `replace` string characters are replaced,
    followed by *decomposed normalization* to `ASCII` characters,
    then the whitelisted characters are filtered
    and lastly the name length is truncated to :py:const:`~rekhtanavees.misc.FilenameCharLimit`.

    Args:
        name (str): the string to *slugify*.
        whitelist (str): the set of allowed characters
        replace (str): the characters to be replaced with *hyphen*
    """
    # replace spaces
    for r in replace:
        name = name.replace(r, '-')

    # keep only valid ascii chars
    slug = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    slug = ''.join(c for c in slug if c in whitelist)

    # Truncate to maximum allowed characters
    return slug[:FilenameCharLimit]

# ******************************************************************************
