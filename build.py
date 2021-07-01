import stanza
import detoxify
import language_tool_python as ltp

import constants as cst

# this will log a warning to console if corenlp folder already exists
stanza.install_corenlp(dir=cst.CORENLP_HOME)
ltp.LanguageTool("en-US")
detoxify.Detoxify('original-small')
