# -*- coding: utf-8 -*-

# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from random import choice, randint

from rekhtanavees.misc.utils import isValidProjectName


# ******************************************************************************
class TestUtils:
    ValidCharset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ '

    # **************************************************************************
    @staticmethod
    def getInvalidNames(count: int) -> list[str]:
        TotalCharSet = ''.join([chr(i) for i in range(0x20, 0x80)])
        names = []
        while len(names) < count:
            # Random length name between 5 and 15
            charCount = randint(5, 15)
            name = ''
            hasInvalid = False
            for _ in range(charCount):
                ch = choice(TotalCharSet)
                hasInvalid = hasInvalid or (ch not in TestUtils.ValidCharset)
                name += ch
            if hasInvalid:
                names.append(name)

        return names

    # **************************************************************************
    @staticmethod
    def getValidNames(count: int) -> list[str]:
        names = []
        while len(names) < count:
            # Random length name between 5 and 15
            charCount = randint(5, 15)
            name = ''
            for _ in range(charCount):
                name += choice(TestUtils.ValidCharset)
            name = name.strip()
            # Exclude white space only names
            if name:
                names.append(name)

        return names

    # **************************************************************************
    def test_EmptyFilename(self):
        assert not isValidProjectName('')

    # **************************************************************************
    def test_WhitespaceFilename(self):
        assert not isValidProjectName('   ')
        assert not isValidProjectName('\t')
        assert not isValidProjectName('\n')

    # **************************************************************************
    def test_InvalidCharFilename(self):
        for name in self.getInvalidNames(5):
            assert not isValidProjectName(name)

    # **************************************************************************
    def test_ValidCharFilename(self):
        for name in TestUtils.getValidNames(5):
            assert isValidProjectName(name)

# ******************************************************************************
