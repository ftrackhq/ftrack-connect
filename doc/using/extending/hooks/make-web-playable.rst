..
    :copyright: Copyright (c) 2014 ftrack

*******************
make-web-reviewable
*******************

The make-web-reviewable hook is triggered when publishing a new version. The
default hook will upload the selected component to cloud storage and encode it
to appropriate formats(mp4 and webm).

.. literalinclude:: /../resource/hooks/make_web_playable.py
    :language: python
