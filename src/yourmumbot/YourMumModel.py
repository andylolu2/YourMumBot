import logging

import detoxify
import nltk
import numpy as np
from stanza.server.client import logger as stanza_logger
from stanza.server import CoreNLPClient

import constants as cst
import helpers.methods as helpers
from src.yourmumbot.Corrector import GingerItCorrector, LanguageToolCorrector

stanza_logger.setLevel(logging.ERROR)


class YourMumModel():
    _your_mum_node = nltk.tree.Tree('NP', ['your mum'])

    def __init__(self, corrector="language_tools", silent=False, logger=None):
        if corrector == "gingerit":
            self._corrector = GingerItCorrector()
        elif corrector == 'language_tools':
            self._corrector = LanguageToolCorrector()
        else:
            raise ValueError("corrector must be in {gingerit, language_tools}")

        if logger is None:
            self._logger = logging.getLogger(__name__)
            if silent:
                self._logger.setLevel(logging.ERROR)
            else:
                self._logger.setLevel(logging.DEBUG)
        else:
            assert isinstance(logger, logging.Logger)
            self._logger = logger

        self._model = detoxify.Detoxify('original-small')
        self._corenlp_client = CoreNLPClient(
            endpoint=cst.CORENLP_ENDPOINT,
            classpath=cst.CORENLP_HOME + "/*",
            annotators=['parse'],
            timeout=cst.CORENLP_TIMEOUT,
            output_format='json',
            memory=cst.CORENLP_MEMORY,
            threads=cst.CORENLP_THREADS,
            be_quiet=True)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._corenlp_client.__exit__(*args)

    @staticmethod
    def _is_np(tree: nltk.tree.Tree):
        return type(tree) == nltk.tree.Tree and tree.label() == "NP"

    def warm_up(self):
        list(self.yourmumify("warm the model up"))
        return

    def toxic_score(self, texts, key):
        model = self._model
        scores = model.predict(texts)[key]
        return scores

    def replace_np_with_ym(self, tree: nltk.tree.Tree):
        positions = tree.treepositions()
        positions = sorted(positions, key=len, reverse=True)

        # select all "NP" trees
        np_positions = filter(lambda p: self._is_np(tree[p]), positions)

        res = []  # list of all possible replacements
        for np_pos in np_positions:
            copy = tree.copy(deep=True)
            copy[np_pos] = self._your_mum_node
            aug_phrase = " ".join(copy.leaves())
            if aug_phrase != "your mum":
                res.append(aug_phrase)
        return res

    def correct_grammar(self, text):
        self._logger.info(
            f'grammar: {self._corrector.correct(text, True)}'
        )
        return self._corrector.correct(text)

    def yourmumify(self, text: str):
        # check if input is english
        if not text.isascii():
            return

        # annotate text to find noun phrases (NP) to replace
        ann = self._corenlp_client.annotate(text)
        for sent in ann["sentences"]:
            tree = nltk.tree.Tree.fromstring(sent["parse"])
            self._logger.info(
                'tree: \n'
                f'{tree.pformat()}'
            )

            # replace NP with 'your mum'
            yourmumified = self.replace_np_with_ym(tree)

            # check if list is non-empty
            if yourmumified:
                for i, yourmum_sent in enumerate(yourmumified):
                    # correct grammatical mistakes
                    yourmumified[i] = self.correct_grammar(yourmum_sent)

                # evaluate toxicity of augmented setence,
                # find the most toxic one
                scores = self.toxic_score(yourmumified, key="toxic")
                self._logger.info(
                    f'yourmumify scores: {list(zip(yourmumified, scores))}'
                )
                best = yourmumified[np.argmax(scores)]

                # apply grammar corrector on final output to catch more errors
                best = helpers.apply_n(2, self.correct_grammar, best)
                yield best
