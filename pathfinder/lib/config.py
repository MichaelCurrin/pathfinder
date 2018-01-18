"""Application configuration file."""
import os
from configparser import SafeConfigParser


class AppConf(SafeConfigParser):
    """App configuration object.

    Make app configuration filenames absolute paths and relative to app
    config dir. Then configure the conf object with data.

    The local app conf file is optional and in values in it will overwrite
    those set in the main app conf file.
    """

    def __init__(self):
        """Initialise instance of AppConf class.

        Read config files in three locations, expecting the first versioned
        file to always be present and the two optional files to either override
        the default values or be ignored silently if they are missing.
        """
        SafeConfigParser.__init__(self)

        # Path to the top-level pathfinder directory in the repo.
        self.appDir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   os.path.pardir))

        etcConfNames = ('app.conf', 'app.local.conf')
        confPaths = [os.path.join(self.appDir, 'etc', c) for c in etcConfNames]

        userConfigPath = os.path.join(
            os.path.expanduser('~'),
            '.config',
            'pathfinder.conf'
        )
        confPaths.append(userConfigPath)

        self.read(confPaths)
