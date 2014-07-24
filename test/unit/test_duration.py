# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import pytest

import ftrack_connect.duration


@pytest.mark.parametrize(('duration', 'expected'), [
    ('', 0),
    ('1h', 60 * 60),
    ('1 hours / 30m, 30 seconds', (60 * 60) + (30 * 60) + 30),
    ('1.5h 10s', (60 * 60 * 1.5) + 10),
    ('01:30:30', (60 * 60) + (30 * 60) + 30),
    ('1:3:3', (60 * 60) + (3 * 60) + 3),
    ('1:30', (60 * 60) + (30 * 60)),
    ('90', 90 * 60),
    ('1.5', 60 * 60 * 1.5),
    ('10:30 min', (60 * 10) + 30),
], ids=[
    'empty string',
    'single hour',
    'separators',
    'fractional',
    'full-hour-clock',
    'single-digit-full-hour-clock',
    'half-hour-clock',
    'unit-less integer',
    'unit-less float',
    'minute-clock'
])
def test_parse_duration(duration, expected):
    '''Successfully parse duration.'''
    parser = ftrack_connect.duration.DurationParser()
    value = parser.parse(duration)

    assert value == expected
