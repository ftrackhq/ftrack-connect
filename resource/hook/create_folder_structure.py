import os
import ftrack_api
import logging
from ftrack_action_handler.action import BaseAction

class CreateFolderStructure(BaseAction):
    label = 'create fodler structire'
    identifier = 'com.ftrack.test.create_folder_structure'
    description = 'Create Folder Structure on location'
    api_min_version =  ['2','3','1']

    skip_entities = [
        'AssetVersion', 
        'Asset', 
        'Component', 
        'FileComponent', 
        'SequenceComponent'
    ]

    def _ensure_api_version(self):
        if ftrack_api.__version__.split('.')[0:3] >= self.api_min_version:
           return True

        self.logger.warning(
            'Feature not supported by your current api version : {}'
            'you need api >= 2.3.1'
        )
        return False

    def __init__(self, session):
        super(CreateFolderStructure, self).__init__(session)
        self.location = self.session.pick_location()

    def validate_selection(self, entities):
        '''Utility method to check *entities* validity.

        Return True if the selection is valid.
        '''
        if not entities:
            return False

        all_states = []
        for entity_type, entity_id in entities:
            all_states.append(entity_type not in self.skip_entities)
                
        return all(all_states)

    def discover(self, session, entities, event):
        '''Return True if the action can be discovered.

        Check if the current selection can discover this action.

        '''
        if not self._ensure_api_version():
            return False

        return self.validate_selection(entities)

    def _filter_entities(self, entities):
        valid_entities = []
        for entity in entities:
            if entity.entity_type not in self.skip_entities:
                valid_entities.append(entity)
        return valid_entities
                

    def create_structure(self, entities):
        filtered_entities = self._filter_entities(entities)
        path_results = self.location.get_filesystem_paths(filtered_entities)
        for path_result in path_results:
            if not os.path.exists(path_result):
                os.makedirs(path_result)

    def launch(self, session, entities, event):
        '''Return result of running action.'''
        data, event = self._translate_event(self.session, event)
        _resolved_entities = []
        for datum in data:
            _resolved_entities.append(self.session.get(datum[0], datum[1]))
        self.create_structure(_resolved_entities)
        return True



def register(api_object, **kw):
    '''Register hook with provided *api_object*.'''

    # Validate that session is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an old or incompatible API and
    # return without doing anything.
    if not isinstance(api_object, ftrack_api.session.Session):
        return

    action = CreateFolderStructure(api_object)
    action.register()


if __name__ == '__main__':
    # To be run as standalone code.
    logging.basicConfig(level=logging.INFO)
    session = ftrack_api.Session(auto_connect_event_hub=True)
    register(session)

    # Wait for events
    logging.info('Registered actions and listening for events. Use Ctrl-C to abort.')
    session.event_hub.wait()