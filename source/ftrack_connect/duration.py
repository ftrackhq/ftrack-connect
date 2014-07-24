# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import re
import math

import ftrack_connect.error


class DurationParser(object):
    '''Parse human readable time durations into seconds.'''

    def __init__(self):
        '''Initialise parser.'''
        self._unit = dict(
            day=60 * 60 * 24,
            hour=60 * 60,
            minute=60,
            second=1
        )

        # Build expressions.
        self._expressions = []

        # Hour, minute, seconds specified using unit classifiers.
        # Example: 3.5hours 2 mins, 1s
        value = r'\d+(?:\.\d+)?'
        day = r'(?P<day>{0})\s*(?:days?|dys?|d)'.format(value)
        hour = r'(?P<hour>{0})\s*(?:hours?|hrs?|h)'.format(value)
        minute = r'(?P<minute>{0})\s*(?:minutes?|mins?|m)'.format(value)
        second = r'(?P<second>{0})\s*(?:seconds?|secs?|s)'.format(value)
        separators = r'[\s,/-]*'

        expression = ''
        for entry in [day, hour, minute, second]:
            expression += r'(?:{0})?{1}'.format(entry, separators)

        expression += '$'
        self._expressions.append(
            re.compile(expression, re.IGNORECASE)
        )

        # Minute, second clock format.
        # Example: 1:30 min -> 1 minute and 30 seconds
        self._expressions.append(
            re.compile(
                r'(?P<minute>\d+):(?P<second>\d+)\s*(?:minutes?|mins?|m)\s*$',
                re.IGNORECASE
            )
        )

        # Hour, minute clock format.
        # Example: 1:30 -> 1 hour and 30 minutes
        self._expressions.append(
            re.compile(
                r'(?P<hour>\d+):(?P<minute>\d+)\s*(?:hours?|hrs?|h)?\s*$',
                re.IGNORECASE
            )
        )

        # Hour, minute, second clock formats.
        # Example: 1:30:45 -> 1 hour, 30 minutes and 45 seconds.
        self._expressions.append(
            re.compile(
                r'(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)$',
                re.IGNORECASE
            )
        )

    def parse(self, text):
        '''Return *text* parsed into seconds as float.

        Supported formats are:

            * unit-less integer - Interpreted as minutes. Example: "90" is 1
              hour and 30 minutes.

            * unit-less float - Interpreted as hours. Example: "1.5" is 1 hour
              and 30 minutes.

            * hh:mm - Specify hours and minutes. Can use padded or unpadded
              digits. Example: "03:42" is 3 hours and 42 minutes.

            * mm:ss min - Specify minutes and seconds. Can use padded or
              unpadded digits. Example: "03:42 min" is 3 minutes and 42 seconds.

            * hh:mm:ss - Specify hours, minutes and seconds. Can use padded or
              unpadded digits. Example: "8:45:03" is 8 hours, 43 minutes and 3
              seconds.

            * {hours unit} {minutes unit} {seconds unit} - Can enter specific
              values for each optional unit. Valid unit specifiers include both
              full words and abbreviations. Example: "1h 2 minutes 5 sec"
              It is also possible to use fractions. Example: "1.5h 15seconds"

        Raise :exc:`~ftrack_connect.error.ParseError` if *text* could not be
        parsed.

        '''
        text = text.strip()

        # Interpret empty string as 0
        if not text:
            return 0.0

        # Interpret unit-less integer value as minutes.
        try:
            seconds = int(text)
        except ValueError:
            pass
        else:
            return float(self._unit['minute'] * seconds)

        # Interpret unit-less float value as hours.
        try:
            seconds = float(text)
        except ValueError:
            pass
        else:
            return self._unit['hour'] * seconds

        # Process as expression.
        for expression in self._expressions:
            match = expression.match(text)
            if match:
                seconds = 0.0
                for key, value in match.groupdict().items():
                    if value is not None:
                        seconds += (self._unit[key] * float(value))

                return seconds

        raise ftrack_connect.error.ParseError(
            'Failed to parse duration {0}'.format(text.encode('utf-8'))
        )


class DurationFormatter(object):
    '''Format durations in seconds into human readable strings.'''

    def format(self, seconds):
        '''Return human readable string representing *seconds* duration.'''
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        hours = int(hours)
        minutes = int(minutes)
        seconds = int(math.ceil(seconds))

        if seconds == 60:
            minutes += 1
            seconds = 0

        if minutes == 60:
            hours += 1
            minutes = 0

        if not hours and not minutes:
            text = '{0} sec'.format(seconds)
        elif not hours:
            text = '{0:02d}:{1:02d} min'.format(minutes, seconds)
        else:
            text = '{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)

        return text


# Top level helpers.
parser = DurationParser()
formatter = DurationFormatter()
