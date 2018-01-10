"""Application configuration file."""
import os
from configparser import SafeConfigParser


class AppConf(SafeConfigParser):
    """App configuration object.

    Make app configuration filenames absolute paths and relative to app
    config dir. Then configure the conf object with data.

    The local app conf file is optional and in values in it will overwrite
    those set in the main app conf file
    """

    def __init__(self):
        """
        Initialise instance of AppConf class.
        """
        SafeConfigParser.__init__(self)

        self.appDir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   os.path.pardir))
        confNames = ('app.conf', 'app.local.conf')
        confPaths = [os.path.join(self.appDir, 'etc', c) for c in confNames]

        self.read(confPaths)
