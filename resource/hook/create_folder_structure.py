# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import itertools
import ftrack_api
import logging
import threading

from ftrack_action_handler.action import BaseAction


def _async(fn):
    '''Run *fn* asynchronously.'''

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()

    return wrapper


class CreateFolderStructure(BaseAction):
    label = 'create fodler structire'
    identifier = 'com.ftrack.test.create_folder_structure'
    description = 'Create Folder Structure on location'
    api_min_version =  ['2','3','1']

    # Do not consider building paths for these entities.
    skip_entities = [
        'AssetVersion', 
        'Asset', 
        'Component', 
        'FileComponent', 
        'SequenceComponent'
    ]

    def is_supported(self):
        '''check if the action is supported by the current api version'''
        if ftrack_api.__version__.split('.')[0:3] >= self.api_min_version:
           return True

        self.logger.warning(
            'Feature not supported by your current api version : {},'
            'you need api >= 2.3.1'.format(ftrack_api.__version__)
        )

        return False

    def __init__(self, session):
        '''initialise action with *session*'''
        super(CreateFolderStructure, self).__init__(session)
        self.location = self.session.pick_location()

    def validate_selection(self, entities):
        '''Utility method to check *entities* validity.

        Return True if the selection is valid.
        '''
        if not entities:
            return False

        return True

    
    def discover(self, session, entities, event):
        '''Return True if the action can be discovered.

        Check if the current selection can discover this action.

        '''
        if not self.is_supported():
            return False

        return self.validate_selection(entities)

    def _filter_entities(self, entities):
        '''return filtered *entities* based on supported types'''
        valid_entities = []
        for entity in entities:
            if entity.entity_type not in self.skip_entities:
                valid_entities.append(entity)
        return valid_entities
                
    @_async
    def create_structure(self, entities):
        '''create folder structure based on provided *entities*'''

        filtered_entities = self._filter_entities(entities)
        leafs = [
            list(entity['descendants']) 
            if len(entity['descendants']) > 0 
            else entity 
            for entity in filtered_entities 
        ]
        merged_leafs = list(itertools.chain.from_iterable(leafs))
        valid_leaf_entities = self._filter_entities(merged_leafs)
        path_results = self.location.get_filesystem_paths(valid_leaf_entities)

        for path_result in path_results:
            if not os.path.exists(path_result):
                self.logger.info(
                    'creating folder : {} in location {}'.format(
                        path_result, self.location['name']
                    )
                )
                os.makedirs(path_result)
            else:
                self.logger.info(
                    '{} folder already exist in location {}' .format(
                        path_result,  
                        self.location['name']
                    )
                )

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