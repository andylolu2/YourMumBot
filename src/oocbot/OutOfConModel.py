import detoxify
import nltk

import helpers.methods as helpers


class OutOfConModel():
    model = None

    def toxic_score(self, texts, key):
        model = self.get_model()
        scores = model.predict(texts)[key]
        # scores = [p + 0.003 * (len(s) ** 0.5) for s, p in zip(texts, scores)]
        return scores

    def get_toxic_sublists(self, text, key="obscene", threshhold=0.4):
        # split text to individual setences
        sents = nltk.tokenize.sent_tokenize(text)

        outputs = []
        for sent in sents:
            sublists = helpers.sublists(sent.split(" "))
            substrings = [" ".join(sublist) for sublist in sublists]
            scores = self.toxic_score(substrings, key)
            for score, substring in zip(scores, substrings):
                if score > threshhold:
                    outputs.append((score, substring))
        return outputs

    @classmethod
    def get_model(cls):
        if cls.model is None:
            cls.model = detoxify.Detoxify()
        return cls.model
