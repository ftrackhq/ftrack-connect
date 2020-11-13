# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
import logging
import threading

import ftrack_api
import ftrack_api.exception
import ftrack_api.thread

# Create a session factory instead.
def session_creator():
    print('Created new session for thread {}'.format(threading.current_thread()))
    return ftrack_api.Session(
        auto_connect_event_hub=False, thread_safe_warning='raise'
    )

factory = ftrack_api.thread.SessionFactory(
    session_provider=session_creator,
    pool_size=10
)
