# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
import logging

import ftrack_api
import ftrack_api.exception


# Create a session factory instead.
def session_creator():
    return ftrack_api.Session(
        auto_connect_event_hub=False, thread_safe_warning='raise'
    )


get_scoped = ftrack_api.util.session_factory(
    creator=session_creator,
    registry=ftrack_api.util.ThreadLocalRegistry()
)
