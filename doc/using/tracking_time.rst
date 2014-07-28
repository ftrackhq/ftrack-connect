..
    :copyright: Copyright (c) 2014 ftrack

.. _using/tracking_time:

*************
Tracking time
*************

Tracking time helps productions understand how they are progressing on a project
against the initial bid, but it can help you understand where all your time
went.

However, time logs are pretty useless and nothing more than a pointless chore if
they are not accurate. With this in mind, ftrack is building time tracking
features to help get the most accurate information in the least painful way. We
also want to make the information more usable so that you can give better
estimates and also get control over your time (perhaps even cut down a few
meetings!).

.. _using/tracking_time/timer:

Timer
=====

A first step is the time tracking feature in Connect. Simply select the
:guilabel:`Track time` tab from the main window and you will see a list of your
unresolved tasks.

.. image:: /image/time_tracking_tab_overview.png

.. note::

    Currently the task list does not automatically refresh. Instead, you can
    click the :guilabel:`Refresh` icon to manually refresh the list.

Click the :guilabel:`Play` icon next to a task to immediately start tracking
time against that task. The total tracked time for that task for the current
day will be displayed in the timer and will auto increment.

.. image:: /image/time_tracking_timer_running.png

You can stop the timer by clicking the :guilabel:`Stop` button. Once stopped
the timer will no longer auto increment until you click :guilabel:`Start` again.

.. image:: /image/time_tracking_timer_stopped.png

If you switch to another task by clicking its :guilabel:`Play` icon the current
task timer will be automatically stopped.

You can close the window and, so long as the main Connect service is running,
your timer will continue to track time in the background.

The tracked time for a task is persisted back to the ftrack server when you
click :guilabel:`Stop`, :ref:`set the time manually
<using/tracking_time/timer/setting_time_manually>` or start tracking another
task.

.. _using/tracking_time/timer/setting_time_manually:

Setting time manually
---------------------

As well as using the timer, it is possible to set the elapsed time manually by
clicking in the elapsed time field. The timer will pause if it is running and
allow you to enter a new elapsed time.

.. image:: /image/time_tracking_timer_edit.png

Press :kbd:`Enter` or click anywhere outside of the field to commit your change.
Alternatively, press :kbd:`Esc` to cancel the change and revert to the previous
value.

.. note::

    Remember, currently the time in the field represents the *total* elapsed
    time for a task for the current day. In future, multiple entries for a task
    in a day will be supported.

The edit field supports many different formats for entering time quickly.

.. warning::

    If an invalid time format is entered, the previous valid time will be used.
    Currently, there is no additional visual indicator that the time was entered
    incorrectly.

Natural Units
^^^^^^^^^^^^^

Specify values with units to quickly enter a variety of times. There are
different formats for each unit available.

==============  ===============================
Unit            Formats
==============  ===============================
Day             d, dy, dys, day, days
Hour            h, hr, hrs, hour, hours
Minute          m, min, mins, minute, minutes
Second          s, sec, secs, second, seconds
==============  ===============================

Spacing is optional and you can use either float or integer values for each
unit specified.

=================== ==================================
Example             Meaning
=================== ==================================
1h                  1 hour
1.5 hours 2s        1 hour, 30 minutes and 2 seconds
45 minutes          45 minutes
45 mins 15 secs     45 minutes and 15 seconds
1 day               1 day (24 hours)
4hr 15m             4 hours and 15 minutes
60 seconds          60 seconds
=================== ==================================

Float value
^^^^^^^^^^^

Interpreted as fractional hours.

=================== ==================================
Example             Meaning
=================== ==================================
1.0                 1 hour
1.5                 1 hour and 30 minutes
2.25                2 hours and 15 minutes
=================== ==================================

Integer value
^^^^^^^^^^^^^

Interpreted as minutes.

=================== ==================================
Example             Meaning
=================== ==================================
90                  1 hour and 30 minutes
45                  45 minutes
2880                2 days
=================== ==================================

Hour clock
^^^^^^^^^^

Interpreted as hours and minutes. General format is `{hh:mm}`. Can optionally
specify the unit `{hh:mm} {hour-unit}`.

=================== ==================================
Example             Meaning
=================== ==================================
1:30                1 hour and 30 minutes
01:10               1 hour and 10 minutes
5:45 hours          5 hours and 45 minutes
1:30h               1 hour and 30 minutes
=================== ==================================

Minute clock
^^^^^^^^^^^^

Interpreted as minutes and seconds. Format is `{mm:ss} {minute-unit}`.

=================== ==================================
Example             Meaning
=================== ==================================
1:30 min            1 minute and 30 seconds
01:10m              1 minute and 10 seconds
=================== ==================================
