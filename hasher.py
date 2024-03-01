"""
    Реализация алгоритма хеширования MD-5
"""

import struct
from enum import Enum
from math import (
    floor,
    sin,
)

from bitarray import bitarray

# Убираем ограничения pylint, относящиеся к именованию переменных,
# поскольку специфические названия переменных обусловлены
# математическими формулами

# pylint: disable=C0103
# pylint: disable=C0321


class MD5Buffer(Enum):
    """Инициализация буфера для функции"""
    A = 0x67452301
    B = 0xEFCDAB89
    C = 0x98BADCFE
    D = 0x10325476


class MD5Hasher(object):
    """Реализация хеш-функции"""
    _string = None
    _buffers = {
        MD5Buffer.A: None,
        MD5Buffer.B: None,
        MD5Buffer.C: None,
        MD5Buffer.D: None,
    }

    @classmethod
    def hash(cls, string: str) -> str:
        """Сам метод хеширования"""
        cls._string = string

        preprocessed_bit_array = cls._step_2(cls._step_1())
        cls._step_3()
        cls._step_4(preprocessed_bit_array)
        return cls._step_5()

    @classmethod
    def _step_1(cls):
        """Первый шаг алгоритма"""
        # Конвертируем сообщение в последовательность бит
        bit_array = bitarray(endian="big")
        bit_array.frombytes(cls._string.encode("utf-8"))

        # Дополняем строку 1 битом и необходимым количеством нулевых битов
        # так, чтобы длина битового массива становится равной 448 по модулю 512.

        # Обратите внимание, что заполнение выполняется всегда,
        # даже если бит строки длина уже равна 448 по модулю 512, что приводит к
        # новому 512-битному блоку сообщения.
        bit_array.append(1)
        while len(bit_array) % 512 != 448:
            bit_array.append(0)

        # Для оставшейся части алгоритма MD5 все значения находятся в
        # с прямым порядком байтов, поэтому преобразуем битовый массив
        # в прямой порядок байтов.
        return bitarray(bit_array, endian="little")

    @classmethod
    def _step_2(cls, step_1_result):
        """Второй шаг алгоритма"""
        # Расширяем результат шага 1 его длиной
        length = (len(cls._string) * 8) % pow(2, 64)
        length_bit_array = bitarray(endian="little")
        length_bit_array.frombytes(struct.pack("<Q", length))

        result = step_1_result.copy()
        result.extend(length_bit_array)
        return result

    @classmethod
    def _step_3(cls):
        """Третий шаг алгоритма"""
        # Инициализируем буфер для алгоритма хеширования
        for buffer_type in cls._buffers:
            cls._buffers[buffer_type] = buffer_type.value

    @classmethod
    def _step_4(cls, step_2_result):
        """Четвертый шаг алгоритма"""
        # Определим четыре вспомогательные функции,
        # которые производят одно 32-битное слово.
        def F(x, y, z): return (x & y) | (~x & z)
        def G(x, y, z): return (x & z) | (y & ~z)
        def H(x, y, z): return x ^ y ^ z
        def I(x, y, z): return y ^ (x | ~z)

        # Определяем функцию левого вращения,
        # которая поворачивает `x` влево на `n` бит.
        def rotate_left(x, n): return (x << n) | (x >> (32 - n))

        # Определим функцию для модульного сложения
        def modular_add(a, b): return (a + b) % pow(2, 32)

        # Вычислите таблицу T по функции синуса.
        # Обратите внимание, что RFC начинается с индекса 1,
        # а мы начинаем с индекса 0.
        T = [floor(pow(2, 32) * abs(sin(i + 1))) for i in range(64)]

        # Общее количество 32-битных слов для обработки, N, всегда кратно 16.
        N = len(step_2_result) // 32

        # Обрабатываем фрагменты по 512 бит
        for chunk_index in range(N // 16):
            # Разобъем фрагмент на 16 слов по 32 бита
            start = chunk_index * 512
            X = [step_2_result[start + (x * 32): start + (x * 32) + 32]
                 for x in range(16)]

            # Конвертируем битовый массив в число
            X = [int.from_bytes(word.tobytes(), byteorder="little")
                 for word in X]

            # Сократим значения переменных буфера
            A = cls._buffers[MD5Buffer.A]
            B = cls._buffers[MD5Buffer.B]
            C = cls._buffers[MD5Buffer.C]
            D = cls._buffers[MD5Buffer.D]

            # Выполним 4 поворота по 16 операций в каждом
            for i in range(4 * 16):
                if 0 <= i <= 15:
                    k = i
                    s = [7, 12, 17, 22]
                    temp = F(B, C, D)
                elif 16 <= i <= 31:
                    k = ((5 * i) + 1) % 16
                    s = [5, 9, 14, 20]
                    temp = G(B, C, D)
                elif 32 <= i <= 47:
                    k = ((3 * i) + 5) % 16
                    s = [4, 11, 16, 23]
                    temp = H(B, C, D)
                elif 48 <= i <= 63:
                    k = (7 * i) % 16
                    s = [6, 10, 15, 21]
                    temp = I(B, C, D)

                # Алгоритм MD5 использует модульное сложение.
                # Обратите внимание, что нам нужна временная переменная.
                # Если бы мы поместили результат в `A`,
                # то выражение `A = D` ниже перезаписало бы его.
                # Мы также не можем переместить `A = D` ниже,
                # потому что исходное `D` уже было бы было бы перезаписано
                # выражением `D = C`.
                temp = modular_add(temp, X[k])
                temp = modular_add(temp, T[i])
                temp = modular_add(temp, A)
                temp = rotate_left(temp, s[i % 4])
                temp = modular_add(temp, B)

                # Поменяем местами регистры для следующей операции
                A = D
                D = C
                C = B
                B = temp

            # Обновим буферные значения с помощью результатов,
            # полученных в этом фрагменте
            cls._buffers[MD5Buffer.A] = modular_add(
                cls._buffers[MD5Buffer.A], A)
            cls._buffers[MD5Buffer.B] = modular_add(
                cls._buffers[MD5Buffer.B], B)
            cls._buffers[MD5Buffer.C] = modular_add(
                cls._buffers[MD5Buffer.C], C)
            cls._buffers[MD5Buffer.D] = modular_add(
                cls._buffers[MD5Buffer.D], D)

    @classmethod
    def _step_5(cls):
        """Последний шаг алгоритма"""
        # Преобразуем буферы в little-endian.
        A = struct.unpack("<I", struct.pack(
            ">I", cls._buffers[MD5Buffer.A]))[0]
        B = struct.unpack("<I", struct.pack(
            ">I", cls._buffers[MD5Buffer.B]))[0]
        C = struct.unpack("<I", struct.pack(
            ">I", cls._buffers[MD5Buffer.C]))[0]
        D = struct.unpack("<I", struct.pack(
            ">I", cls._buffers[MD5Buffer.D]))[0]

        # Вывод буферов в шестнадцатеричном формате в нижнем регистре.
        return (
            f"{format(A, '08x')}"
            f"{format(B, '08x')}"
            f"{format(C, '08x')}"
            f"{format(D, '08x')}"
        )
