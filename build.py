import stanza

import constants as cst

try:
    stanza.install_corenlp(dir=cst.CORENLP_HOME)
except Exception as e:
    print(f"{cst.CORENLP_HOME} already exists, skipping...")
