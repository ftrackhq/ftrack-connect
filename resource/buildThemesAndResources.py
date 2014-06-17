import subprocess
subprocess.call(['compass', 'compile'])
subprocess.call(
    [
        'pyside-rcc',
        '-o',
        '../source/ftrack_connect/resource.py',
        'resource.qrc'
    ]
)
