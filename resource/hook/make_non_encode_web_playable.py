# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import json
import functools
import os.path
import logging
import tempfile
import subprocess
import ftrack_api.session
import shutil

log_path = tempfile.gettempdir()
log_file_path = os.path.join(log_path, 'ftrack_non_encode_web_playable.log')
print('saving logs to {}'.format(log_file_path))

# formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# log debug file.
fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

# console info.
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)

# setup logger.
logger = logging.getLogger('ftrack.connect.publish.make-non-encode-web-playable')
logger.addHandler(fh)
logger.addHandler(ch)


#change these to match full path to the exact executables.
ffmpeg_cmd = shutil.which('ffmpeg')
ffprobe_cmd = shutil.which('ffprobe')

if not ffmpeg_cmd:
    msg = 'ffmpeg executable not fund in $PATH'
    logger.error(msg)
    raise IOError(msg)

if not ffprobe_cmd:
    msg = 'ffprobe executable not fund in $PATH'
    logger.error(msg)
    raise IOError(msg)

def exec_cmd(cmd):
    '''execute the provided *cmd*'''
    logger.debug('Running command {}'.format(cmd))
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    (stdout, stderr) = process.communicate()

    if process.returncode:
        msg =  'Error "{}" while running:'.format(stderr, cmd[0])
        logger.error(msg)
        raise IOError('Subprocess failed:{}'.format(msg))

    return stdout


def generate_thumbnail(filepath):
    '''generate thumbnail from the given *filepath*'''
    destination = tempfile.NamedTemporaryFile(suffix='.jpg').name
    logger.info('Saving thumbnail in {}'.format(destination))

    cmd = [
        ffmpeg_cmd, '-v', 'error', '-i', filepath, '-filter:v',
        'scale=300:-1', '-ss', '0', '-an', '-vframes', '1', '-vcodec',
        'mjpeg', '-f', 'image2', destination
    ]
    exec_cmd(cmd)
    return destination


def get_info(filepath):
    '''get file information from the given *filepath*'''
    cmd = [ffprobe_cmd]
    cmd += ['-v', 'error']
    cmd += ['-print_format', 'json']
    cmd += ['-show_format']
    cmd += ['-show_streams']
    cmd += [filepath]
    
    result = exec_cmd(cmd)

    try:
        result = json.loads(result)
    except Exception as error:
        raise IOError('ffprobe failed with {}'.format(str(error)))

    try:
        streams = result.get('streams', {})
        videoInfo = [
            stream for stream in streams if stream.get('codec_type') == 'video'
        ][0]
        formatInfo = result.get('format', {})

        frameRates = videoInfo.get('r_frame_rate', '0/0').split('/')
        frameRate = float(frameRates[0]) / float(frameRates[1])
    except Exception:
        frameRate = 0

    frameOut = int(videoInfo.get('nb_frames', 0))
    if not frameOut:
        duration = float(formatInfo.get('duration', 0))
        frameOut = int(duration * frameRate)

    meta = {
        'frameIn': 0,
        'frameOut': frameOut,
        'frameRate': frameRate,
        'location': 'byjus-review-location'
    }
    logger.debug('get_info result {}'.format(meta))
    return meta
    

def callback(event, session):
    '''Non encoding make-web-playable hook.
    '''
    # http://ftrack-python-api.rtd.ftrack.com/en/stable/example/web_review.html?highlight=reviewable

    # disable previous event
    event.stop()

    # run new event
    versionId = event['data']['versionId']
    path = event['data']['path']

    version = session.get('AssetVersion', versionId)
    session.commit()

    # Validate that the path is an accessible file.
    if not os.path.isfile(path):
        raise ValueError(
            '"{0}" is not a valid filepath.'.format(path)
        )

    # change name of component and update metadata to enable review.
    component = session.get('Component', version['components'][0]['id'])
    metadata = get_info(path)
    component['name'] = 'ftrackreview-mp4'
    component['metadata']['ftr_meta'] = json.dumps(metadata)

    # generate and publish thumbnail
    thumbnail_path = generate_thumbnail(path)
    version.create_thumbnail(thumbnail_path)

    session.commit()
    logger.info('make-non-encode-web-reviewable hook completed for {}'.format(version))


def subscribe(session):
    '''Subscribe to events.'''
    topic = 'ftrack.connect.publish.make-web-playable'
    logger.debug('Subscribing to event topic: {0!r}'.format(topic))

    # add new make web playable without encoding
    session.event_hub.subscribe(
        u'topic="{0}" and source.user.username="{1}"'.format(
            topic, session.api_user
        ),
        functools.partial(callback, session=session),
        priority=20
    )


def register(session, **kw):
    '''Register plugin. Called when used as an plugin.'''
    # Validate that session is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an old or incompatible API and
    # return without doing anything.
    if not isinstance(session, ftrack_api.session.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack_api.Session instance.'.format(session)
        )
        return

    subscribe(session)
    logger.debug('Non encode web playable plugin registered')