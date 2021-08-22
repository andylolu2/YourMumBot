from abc import ABC, abstractmethod
import time

import language_tool_python as ltp

from api import LANG_NAME, LT_ENDPOINT, LT_MAX_RETRIES, LT_TIMEOUT


class Corrector(ABC):
    @abstractmethod
    def correct(self, text: str, details=False):
        pass


class LanguageToolCorrector(Corrector):
    def __init__(self) -> None:
        self._parser = None
        retries = LT_MAX_RETRIES
        while self._parser is None:
            try:
                self._parser = ltp.LanguageTool(LANG_NAME,
                                                remote_server=LT_ENDPOINT)
                print('Connected!')
            except ltp.utils.LanguageToolError as e:
                if retries <= 0:
                    raise e
                else:
                    print('Failed to connect to language tools. Reconnecting...')
                    print(f'{retries} retires left...')
                    time.sleep(LT_TIMEOUT)
                retries -= 1

    def ignore_match(self, match: ltp.Match) -> bool:
        return not match.ruleId == 'MORFOLOGIK_RULE_EN_US'

    def correct(self, text: str, details=False):
        matches = self._parser.check(text)
        matches = list(filter(self.ignore_match, matches))
        if details:
            return matches
        else:
            return ltp.utils.correct(text, matches)
