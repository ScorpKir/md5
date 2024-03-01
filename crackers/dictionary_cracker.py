"""
    Взлом хеш-функии MD-5 перебором по словарю.
"""

import os
import json
import hashlib
from typing import Optional


class MD5DictionaryCracker():
    """
        Восстановление исходного значения по хешу с помощью метода
        перебора по словарю.
    """

    @classmethod
    def crack(cls, hash__: str) -> Optional[str]:
        """
            Восстановление исходного значения из хеша перебором по словарю

            :param hash: Хешированное значение
            :type hash: str

            :return: Исходное значение
            :rtype: Optional[str]
        """
        directory = './wordset-dictionary/data/'
        for filename in os.listdir(directory):
            filename = directory + filename
            with open(file=filename, mode='r', encoding='utf-8') as file_:
                dictionary = json.load(file_)
                for word in dictionary:
                    if hashlib.md5(word.encode()).hexdigest() == hash__:
                        return word
        return None
