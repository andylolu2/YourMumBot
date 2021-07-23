from abc import ABC, abstractmethod
import time

import language_tool_python as ltp

import constants as cst


class Corrector(ABC):
    @abstractmethod
    def correct(self, text: str, details=False):
        pass


class LanguageToolCorrector(Corrector):
    _parser = None
    while _parser is None:
        try:
            _parser = ltp.LanguageTool(cst.LANG_NAME,
                                       remote_server=cst.LANGTOOL_ENDPOINT)
            print('Connected!')
        except ltp.utils.LanguageToolError as e:
            print('Failed to connect to language tools. Reconnecting...')
            time.sleep(1)

    def ignore_match(self, match: ltp.Match) -> bool:
        return not match.ruleId == 'MORFOLOGIK_RULE_EN_US'

    def correct(self, text: str, details=False):
        matches = self._parser.check(text)
        matches = list(filter(self.ignore_match, matches))
        if details:
            return matches
        else:
            return ltp.utils.correct(text, matches)
