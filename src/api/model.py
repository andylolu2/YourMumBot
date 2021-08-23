from __future__ import annotations
from typing import List, Awaitable
import functools
import logging
import re
import asyncio

import detoxify
import nltk
import numpy as np
from stanza.server.client import logger as stanza_logger
from stanza.server import CoreNLPClient
from stanza.server import StartServer

from api import CORENLP_ENDPOINT, CORENLP_TIMEOUT, WARM_UP_TEXT, MAX_SUB_SAMPLES
from api.corrector import LanguageToolCorrector
from api.logger import logger

stanza_logger.setLevel(logging.ERROR)


class YourMumModel():
    _your_mum_node = nltk.tree.Tree('NP', ['your mum'])

    def __init__(self) -> None:
        self._corrector = LanguageToolCorrector()

        self._model = detoxify.Detoxify('original-small')
        self._corenlp_client = CoreNLPClient(
            start_server=StartServer.DONT_START,
            endpoint=CORENLP_ENDPOINT,
            annotators=['parse'],
            timeout=CORENLP_TIMEOUT,
            output_format='json',
            be_quiet=True
        )

    def __enter__(self) -> YourMumModel:
        return self

    def __exit__(self, *args) -> None:
        self._corenlp_client.__exit__(*args)

    # public methods
    def yourmumify(self, text: str, log: bool = True) -> List[str]:
        '''
        Creates your mum jokes from given text.
        :param text: Text to yourmumify.
        :param log: Default True. Whether or not to log.
        :return: List of yourmumified strings. Each string in the list corresponds to a sentence in the input text. If the input contains 2 sentences, then the output will be a list of 2 strings.
        '''
        bests, best_scores = [], []
        if log:
            logger.debug(f'Input: {text}')

        ann = self._corenlp_client.annotate(text)
        for sent in ann["sentences"]:
            tree = nltk.tree.Tree.fromstring(sent["parse"])
            if log:
                logger.debug(
                    'Tree: \n'
                    f'{tree.pformat()}'
                )

            # replace NP with 'your mum'
            yourmumified = self._replace_np_with_ym(tree)

            if len(yourmumified) == 0:
                continue

            # check if list is non-empty
            for i, yourmum_sent in enumerate(yourmumified):
                # correct grammatical mistakes
                yourmumified[i] = self._correct_grammar(yourmum_sent)

            # evaluate toxicity of augmented setence,
            # find the most toxic one
            scores = self._toxic_score(yourmumified, key="toxic")
            if log:
                logger.debug(
                    f'Detoxify scores: {list(zip(yourmumified, scores))}'
                )
            best = yourmumified[np.argmax(scores)]
            best_score = max(scores)

            # apply grammar corrector on final output to catch more errors
            best = self._correct_grammar(best)
            bests.append(best)
            best_scores.append(best_score)
        return bests, best_scores

    def warm_up(self) -> None:
        '''
        Warms up the model by calling with a sample text.
        '''
        self.yourmumify(WARM_UP_TEXT, log=False)

    async def async_yourmumify(self, text: str, log: bool = True) -> Awaitable[List[str]]:
        '''
        Executes yourmumify asynchronously.
        '''
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, functools.partial(
            self.yourmumify,
            text,
            log=log
        ))

    # private methods
    @staticmethod
    def _is_np(tree: nltk.tree.Tree) -> bool:
        '''
        Checks if a Tree is a noun phrase (NP).
        '''
        return isinstance(tree, nltk.tree.Tree) and tree.label() == "NP"

    @staticmethod
    def _is_basic_response(text: str) -> bool:
        '''
        Checks if the text is a basic reponse.
        '''
        pattern = re.compile(r'[^a-zA-Z0-9]*your mum[^a-zA-Z0-9]*')
        return pattern.fullmatch(text.lower()) is not None

    @classmethod
    def _replace_np_with_ym(cls, tree: nltk.tree.Tree) -> List[str]:
        '''
        Generates all possible yourmum-substitutions given a tree by replacing noun phrases (NP).
        :param tree: The nltk tree to process.
        :return: List of yourmumified strings.
        '''
        positions = tree.treepositions()
        positions = sorted(positions, key=len, reverse=True)

        # select all NP node positions
        np_positions = filter(lambda p: cls._is_np(tree[p]), positions)

        res = []  # list of all possible replacements
        for np_pos in np_positions:
            copy = tree.copy(deep=True)

            # replace np with 'your mum'
            copy[np_pos] = cls._your_mum_node

            # transform tree to string
            aug_phrase = " ".join(copy.leaves())

            # ignore basic response
            if not cls._is_basic_response(aug_phrase):
                res.append(aug_phrase)
        if len(res) > MAX_SUB_SAMPLES:
            res = sorted(res, key=len)[:MAX_SUB_SAMPLES]
        return res

    def _toxic_score(self, texts: List[str], key: str) -> List[float]:
        '''
        Computes the toxicity scores for each input in text.
        :param texts: List of texts to compute scores for.
        :param str: One of {toxic, severe_toxic, obscene, threat, insult, identity_hate}.
        :return: List of toxicity scores. Higher is more toxic.
        '''
        scores = self._model.predict(texts)[key]
        return scores

    def _correct_grammar(self, text: str) -> str:
        '''
        Corrects the grammar of a string.
        :param text: Text to correct grammar.
        :return: String with corrected grammar.
        '''
        return self._corrector.correct(text)
