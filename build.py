import stanza

import constants as cst

# this will log a warning to console if corenlp folder already exists
stanza.install_corenlp(dir=cst.CORENLP_HOME)
