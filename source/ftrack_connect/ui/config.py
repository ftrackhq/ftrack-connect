# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import os
import os.path
import appdirs
import json
import logging


logger = logging.getLogger('ftrack_connect.ui.config')

def get_all_server_url_configs():
    config_file_dir = os.path.join(
        appdirs.user_data_dir('ftrack-connect', 'ftrack'))

    valid_configs = []
    for i in os.listdir(config_file_dir):
        if i.lower() == 'config.json':
            continue
        if i.lower().endswith('.json'):
            valid_configs.append(os.path.join(config_file_dir,i))
    data = {}
    for config in valid_configs:
        logger.debug(u'Reading config from {0}'.format(config))

        with open(config, 'r') as file:
            try:
                temp_config = json.load(file)
            except Exception:
                logger.exception(
                    u'Exception reading json config in {0}.'.format(
                        config
                    )
                )
            else:
                data[temp_config['server_url']] = temp_config
    return data


def get_short_name_from_domain(domain):
    return domain.split("/")[-1].replace(".", "")


def get_config_file_path(domain=None):
    '''Return config file path.'''
    if domain:
        config_file = os.path.join(
            appdirs.user_data_dir('ftrack-connect', 'ftrack'), '{}.json'.format(get_short_name_from_domain(domain))
        )
    else:
        config_file = os.path.join(
            appdirs.user_data_dir('ftrack-connect', 'ftrack'),
            'config.json'
        )

    return config_file


def read_json_config(domain=None):
    '''Return json config from disk storage.'''
    config = None
    general_config = None

    general_config_file = get_config_file_path(domain=None)
    if os.path.isfile(general_config_file):
        logger.debug(u'Reading config from {0}'.format(general_config_file))

        with open(general_config_file, 'r') as file:
            try:
                general_config = json.load(file)
            except Exception:
                logger.exception(
                    u'Exception reading json config in {0}.'.format(
                        general_config
                    )
                )
    if general_config:
        if "last_used_server_url" in general_config and not domain:
            domain = general_config["last_used_server_url"]

    config_file = get_config_file_path(domain=domain)

    if os.path.isfile(config_file):
        logger.debug(u'Reading config from {0}'.format(config_file))

        with open(config_file, 'r') as file:
            try:
                config = json.load(file)
            except Exception:
                logger.exception(
                    u'Exception reading json config in {0}.'.format(
                        config_file
                    )
                )

    if general_config and config:
        general_config.update(config)
        return general_config
    if general_config and not config:
        return general_config


def write_json_config(config, domain=None):
    '''Write *config* as json file.'''
    if domain:
        domain_specific_keys = ['accounts', 'last_used_api_user']
        domain_config = {}
        for k in domain_specific_keys:
            if k in config:
                domain_config[k] = config[k]
        domain_config['server_url'] = config['last_used_server_url']
        config_file = get_config_file_path(domain=domain)

        # Create folder if it does not exist.
        folder = os.path.dirname(config_file)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        with open(config_file, 'w') as file:
            json.dump(domain_config, file)

        for k in domain_specific_keys:
            config.pop(k)

    config_file = get_config_file_path()

    # Create folder if it does not exist.
    folder = os.path.dirname(config_file)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    with open(config_file, 'w') as file:
        json.dump(config, file)
