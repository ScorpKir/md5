"""
    Точка входа программы
"""

import argparse
import hashlib

from hasher import MD5Hasher
from crackers.dictionary_cracker import MD5DictionaryCracker
from crackers.bruteforce_cracker import MD5BruteForceCracker
from crackers.rainbow_cracker import MD5RainbowCracker


ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def hash_message_builtin(message: str) -> str:
    """Хеширование сообщения встроенными средствами языка python"""
    return hashlib.md5(message.encode()).hexdigest()


def main() -> None:
    """Точка входа приложения"""
    parser = argparse.ArgumentParser(
        description="Программа для хеширования сообщений и взлома хешей."
    )
    parser.add_argument(
        "--hash_builtin",
        action="store",
        nargs=1,
        metavar=("MESSAGE"),
        help="Хешировать сообщение встроенными средствами языка"
    )
    parser.add_argument(
        "--hash_custom",
        action="store",
        nargs=1,
        metavar=("MESSAGE"),
        help="Хешировать сообщение самописной функцией"
    )
    parser.add_argument(
        "--dictionary_attack",
        action="store",
        nargs=1,
        metavar=("HASH"),
        help="Взлом хеша перебором по словарю"
    )
    parser.add_argument(
        "--bruteforce_attack",
        action="store",
        nargs=1,
        metavar=("HASH"),
        help="Взлом хеша брутфорсом"
    )
    parser.add_argument(
        "--rainbow_attack",
        action="store",
        nargs=1,
        metavar=("HASH"),
        help="Взлом хеша методом Rainbow Crack"
    )

    args = parser.parse_args()

    if args.hash_builtin:
        argument = args.hash_builtin[0]
        result = hash_message_builtin(argument)
        print(f'Исходное слово: {argument}. \n\nРезультат: {result}.')
    elif args.hash_custom:
        argument = args.hash_custom[0]
        result = MD5Hasher.hash(argument)
        print(f'Исходное слово: {argument}. \n\nРезультат: {result}.')
    elif args.dictionary_attack:
        argument = args.dictionary_attack[0]
        result = MD5DictionaryCracker.crack(argument)
        print(f'Исходный хеш: {argument}. \n\n'
              f'Восстановленное сообщение: {result}.')
    elif args.bruteforce_attack:
        argument = args.bruteforce_attack[0]
        result = MD5BruteForceCracker.crack(
            argument,
            ALPHABET,
            4
        )
        print(f'Исходный хеш: {argument}. \n\n'
              f'Восстановленное сообщение: {result}.')
    elif args.rainbow_attack:
        argument = args.rainbow_attack[0]
        result = MD5RainbowCracker().crack(argument, 3, 4)
        print(f'Исходный хеш: {argument}. \n\n'
              f'Восстановленное сообщение: {result}.')
    else:
        print("Необходимо указать хотя бы одну из доступных функций.")


if __name__ == '__main__':
    main()
