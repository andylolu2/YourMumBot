from pathlib import Path

import pandas as pd

import constants as cst


class DiscordChat():
    def __init__(self) -> None:
        csvs = list(
            Path(cst.PROJECT_ROOT + "/data/raw/ext/discord/").rglob("*.csv"))
        self._df = pd.read_csv(csvs[0])["Content"]
        self._df = self._df.loc[~self._df.str.startswith('-', na=True)]

    def __getitem__(self, indices):
        return self._df.iloc[indices]

    def __len__(self):
        return len(self._df)

    def sample(self, n):
        return self._df.sample(n)
