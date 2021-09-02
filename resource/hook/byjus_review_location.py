
import ftrack_api

def configure_locations(event):
    session = event['data']['session']

    location = session.ensure(
        'Location', {
            'name': 'ftrack.server'
        }
    )
    location.priority = 0

def register(session, **kw):
    if not isinstance(session, ftrack_api.Session):
        return

    session.event_hub.subscribe(
        'topic=ftrack.api.session.configure-location',
        configure_locations
    )
