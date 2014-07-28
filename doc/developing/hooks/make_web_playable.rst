..
    :copyright: Copyright (c) 2014 ftrack

*******************
make-web-reviewable
*******************

The make-web-reviewable hook is triggered when publishing a new version. The
default hook will upload the selected component to cloud storage and encode it
to appropriate formats(:term:`mp4` and :term:`webm`).

Parameters
==========

:event: The specific event being handled.
:versionId: The id of the version that has been created for the publish.
:path: The path to the file to use as component.

.. literalinclude:: /../resource/hook/make_web_playable.py
    :language: python
