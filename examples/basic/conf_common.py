from esp_docs.conf_docs import *  # noqa: F403,F401

languages = ['en', 'zh_CN']
idf_targets = ['esp8266', 'esp32', 'esp32s2', 'esp32s3', 'esp32c3', 'esp32h2', 'esp32c2', 'esp32c6', 'esp32p4']

extensions += ['sphinx_copybutton',
               'sphinxcontrib.wavedrom',
               ]

# link roles config
github_repo = 'espressif/esp-idf'

# context used by sphinx_idf_theme
html_context['github_user'] = 'espressif'
html_context['github_repo'] = 'esp-docs'

html_static_path = ['../_static']

# Extra options required by sphinx_idf_theme
project_slug = 'esp-docs'

# Contains info used for constructing target and version selector
# Can also be hosted externally, see esp-idf for example
versions_url = './_static/docs_version.js'

# Final PDF filename will contains target and version
pdf_file_prefix = u'esp-docs'
