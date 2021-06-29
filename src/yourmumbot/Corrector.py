from abc import ABC, abstractmethod

from gingerit.gingerit import GingerIt
import language_tool_python as ltp


class Corrector(ABC):
    @abstractmethod
    def correct(self, text: str, details=False):
        pass


class GingerItCorrector(Corrector):
    _parser = GingerIt()

    def correct(self, text: str, details=False):
        if details:
            return self._parser.parse(text)
        else:
            return self._parser.parse(text)['result']


class LanguageToolCorrector(Corrector):
    _parser = ltp.LanguageTool("en-US")

    def ignore_match(self, match: ltp.Match) -> bool:
        return not match.ruleId == 'MORFOLOGIK_RULE_EN_US'

    def correct(self, text: str, details=False):
        matches = self._parser.check(text)
        matches = list(filter(self.ignore_match, matches))
        if details:
            return matches
        else:
            return ltp.utils.correct(text, matches)
