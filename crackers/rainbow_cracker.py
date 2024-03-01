"""
    Взлом хеш-функии MD-5 с помощью метода Rainbow Crack.
"""

import os
import json
import hashlib
import itertools

CHARSET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


class MD5RainbowCracker():
    """
        Взлом хеш-функии MD-5 с помощью метода Rainbow Crack.
    """

    @classmethod
    def _reduce_hash(cls, hash_value: str, position: int,
                     password_length: int) -> str:
        """
            Уменьшает хеш до определенной длины.

            :param hash_value: Хеш, который требуется уменьшить.
            :param position: Позиция в цепочке, используемая для уменьшения.
            :param password_length: Длина исходного пароля.

            :returns: Уменьшенный хеш.
        """
        hash_ = hashlib.md5(hash_value.encode('utf-8')).hexdigest()
        return hash_[position % password_length:]

    @classmethod
    def _build_rainbow_table(cls, start: int, end: int, chain_length: int,
                             password_length: int) -> dict:
        """
            Строит радужную таблицу для взлома хешей.


            :param start: Начальное значение для построения таблицы.
            :param end: Конечное значение для построения таблицы.
            :param chain_length: Длина цепочки хешей в радужной таблице.
            :param password_length: Длина исходного пароля.

            :return: Словарь, содержащий хеши и
                     соответствующие им исходные пароли.
        """
        rainbow_table = {}
        table_path = './rainbowtable.json'
        file_exists = os.path.exists(table_path)
        if file_exists:
            with open(table_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        for length in range(start, end + 1):
            for combination in itertools.product(CHARSET, repeat=length):
                word = ''.join(combination)
                print(word)
                plain_text = str(word)
                hash_value = hashlib.md5(plain_text.encode('utf-8')).hexdigest()
                for j in range(chain_length):
                    plain_text = cls._reduce_hash(
                        hash_value,
                        j,
                        password_length
                    )
                    hash_value = hashlib.md5(
                        plain_text.encode('utf-8')).hexdigest()
                rainbow_table[hash_value] = word
        with open('rainbowtable.json', 'w', encoding='utf-8') as file:
            json.dump(rainbow_table, file)
        return rainbow_table

    @classmethod
    def crack(cls, hash_value: str, chain_length: int,
              password_length: int) -> str:
        """
            Взламывает хеш, используя радужную таблицу.

            :param hash_value: Хеш, который требуется взломать.
            :param rainbow_table: Радужная таблица для поиска соответствия хешу.
            :param chain_length: Длина цепочки хешей в радужной таблице.
            :param password_length: Длина исходного пароля.

            :return: Исходный пароль, соответствующий взломанному хешу.
        """
        rainbow_table = cls._build_rainbow_table(
            1,
            4,
            chain_length,
            password_length
        )
        for i in range(chain_length):
            reduced_hash = cls._reduce_hash(hash_value, i, password_length)
            if reduced_hash in rainbow_table:
                plain_text = rainbow_table[reduced_hash]
                test_hash = hashlib.md5(plain_text.encode('utf-8')).hexdigest()
                if test_hash == hash_value:
                    return plain_text
        return "Password not found"
