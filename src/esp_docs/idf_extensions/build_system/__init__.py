# Sphinx extension to integrate IDF build system information
# into the Sphinx Build
#
# Runs early in the Sphinx process, runs CMake to generate the dummy IDF project
# in this directory - including resolving paths, etc.
#
# Then emits the new 'project-build-info' event which has information read from IDF
# build system, that other extensions can use to generate relevant data.
import json
import os.path
import shutil
import subprocess
import sys

# this directory also contains the dummy IDF project
project_path = os.path.abspath(os.path.dirname(__file__))

# Targets which needs --preview to build
PREVIEW_TARGETS = ['esp32p4']


def setup(app):
    # Setup some common paths

    try:
        build_dir = os.environ['BUILDDIR']  # TODO see if we can remove this
    except KeyError:
        build_dir = os.path.dirname(app.doctreedir.rstrip(os.sep))

    try:
        os.mkdir(build_dir)
    except OSError:
        pass

    try:
        os.mkdir(os.path.join(build_dir, 'inc'))
    except OSError:
        pass

    # Fill in a default IDF_PATH if it's missing (ie when Read The Docs is building the docs)
    try:
        idf_path = os.environ['IDF_PATH']
    except KeyError:
        idf_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

    app.add_config_value('docs_root', os.path.join(idf_path, 'docs'), 'env')
    app.add_config_value('idf_path', idf_path, 'env')
    app.add_event('project-build-info')

    # we want this to run early in the docs build but unclear exactly when
    app.connect('config-inited', generate_idf_info)

    return {'parallel_read_safe': True, 'parallel_write_safe': True, 'version': '0.1'}


def generate_idf_info(app, config):
    print('Running CMake on dummy project to get build info...')

    if not app.config.idf_target:
        raise RuntimeError('A valid target is needed to build docs for ESP-IDF. '
                           'Please re-run build-docs with a target specified, e.g: '
                           'build-docs -t esp32')

    build_dir = os.path.dirname(app.doctreedir.rstrip(os.sep))
    cmake_build_dir = os.path.join(build_dir, 'build_dummy_project')
    idf_py_path = os.path.join(app.config.project_path, 'tools', 'idf.py')
    print('Running idf.py...')
    idf_py = [sys.executable,
              idf_py_path,
              '-B',
              cmake_build_dir,
              '-C',
              project_path,
              '-D',
              'SDKCONFIG={}'.format(os.path.join(build_dir, 'dummy_project_sdkconfig'))
              ]

    # force a clean idf.py build w/ new sdkconfig each time
    # (not much slower than 'reconfigure', avoids any potential config & build versioning problems
    shutil.rmtree(cmake_build_dir, ignore_errors=True)
    print('Starting new dummy IDF project... ')

    if (app.config.idf_target in PREVIEW_TARGETS):
        subprocess.check_call(idf_py + ['--preview', 'set-target', app.config.idf_target])
    else:
        subprocess.check_call(idf_py + ['set-target', app.config.idf_target])

    print('Running CMake on dummy project...')
    subprocess.check_call(idf_py + ['reconfigure'])

    with open(os.path.join(cmake_build_dir, 'project_description.json')) as f:
        project_description = json.load(f)
    if project_description['target'] != app.config.idf_target:
        # this shouldn't really happen unless someone has been moving around directories inside _build, as
        # the cmake_build_dir path should be target-specific
        raise RuntimeError(('Error configuring the dummy IDF project for {}. ' +
                            'Target in project description is {}. ' +
                            'Is build directory contents corrupt?')
                           .format(app.config.idf_target, project_description['target']))

    app.emit('project-build-info', project_description)

    return []
