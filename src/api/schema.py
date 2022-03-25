from pydantic import BaseModel, Field, validator

from api import INPUT_MAX_CHAR, INPUT_MAX_WORDS


class RequestBody(BaseModel):
    msg: str = Field(..., max_length=INPUT_MAX_CHAR, strip_whitespace=True)

    @validator('msg')
    def msg_max_words(cls, v: str):
        words = v.split(' ')
        assert len(words) <= INPUT_MAX_WORDS, \
            f'ensure this value has at most {INPUT_MAX_WORDS} words'
        return v

    @validator('msg')
    def msg_is_ascii(cls, v: str):
        assert v.isascii(), \
            f'ensure this value only contains ascii characters'
        return v
