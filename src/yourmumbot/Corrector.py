from abc import ABC, abstractmethod

import language_tool_python as ltp


class Corrector(ABC):
    @abstractmethod
    def correct(self, text: str, details=False):
        pass


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
