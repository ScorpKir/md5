"""
    Взлом хеш-функции MD-5 полным перебором.
    
    Для ускорения вычислений перебор происходит в многопоточном режиме.
"""

import hashlib
import itertools
import threading
from typing import Optional


class MD5BruteForceCracker():
    """Взлом хеш-функции MD-5 полным перебором."""

    @classmethod
    def _brute_force_crack(cls, hash__: str, charset: str,
                           start: int, end: int, result: list[str]) -> None:
        """
            Восстановление исходного значения из хеша методом полного перебора
            для запуска в несколько потоков

            :param hash: Хешированное значение
            :type hash: str

            :param charset: Алфавит символов, из которых состоит 
                            исходное сообщение
            :type charset: str

            :param start: Минимальная длина исходного сообщения
            :type start: int

            :param end: Минимальная длина исходного сообщения
            :type end: int

            :param result: Аргумент для записи результата
            :type result: list[str]

            :return: Исходное значение
            :rtype: Optional[str]
        """
        for length in range(start, end + 1):
            for combination in itertools.product(charset, repeat=length):
                word = ''.join(combination)
                hashed_word = hashlib.md5(word.encode()).hexdigest()
                if hashed_word == hash__:
                    result.append(word)
                    return None
        return None

    @classmethod
    def crack(cls, hash__: str, charset: str,
              max_length: int, num_threads: int = 4) -> Optional[str]:
        """
            Восстановление исходного значения из хеша методом полного перебора
            в несколько потоков

            :param hash: Хешированное значение
            :type hash: str

            :param charset: Алфавит символов, из которых состоит 
                            исходное сообщение
            :type charset: str

            :param max_length: Максимальная длина исходного сообщения
            :type max_length: int

            :param num_threads: Количество потоков,  

            :return: Исходное значение
            :rtype: Optional[str]
        """
        result = []
        threads = []
        chunk_size = max_length // num_threads

        for i in range(num_threads):
            start = i * chunk_size + 1
            end = start + chunk_size - 1 if i < num_threads - 1 else max_length
            thread = threading.Thread(
                target=cls._brute_force_crack,
                args=(hash__, charset, start, end, result)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return result[0] if result else None
