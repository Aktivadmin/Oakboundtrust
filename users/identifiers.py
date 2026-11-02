"""Generators for the account, routing and card numbers shown to customers.

All numbers are fictional demo values. Each follows the real-world format:
  * routing number: 9 digits with the ABA checksum (3-7-1 weights, sum divisible by 10). Prefix 80 is
    reserved for traveller's cheques, so it never collides with a real bank.
  * account number: 12 digits, no leading zero.
  * card number: 16 digits that pass the Luhn check, using only the digits 1 to 5.
"""
import secrets

CARD_DIGITS = "12345"


def _digits(n, alphabet="0123456789"):
    return [int(secrets.choice(alphabet)) for _ in range(n)]


def routing_number():
    d = [8, 0] + _digits(6)
    weights = [3, 7, 1, 3, 7, 1, 3, 7]
    total = sum(a * b for a, b in zip(d, weights))
    d.append((10 - total % 10) % 10)
    return "".join(map(str, d))


def routing_is_valid(value):
    if len(value) != 9 or not value.isdigit():
        return False
    weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
    return sum(int(c) * w for c, w in zip(value, weights)) % 10 == 0


def account_number():
    return str(secrets.choice("123456789")) + "".join(map(str, _digits(11)))


def luhn_is_valid(value):
    total = 0
    for i, ch in enumerate(reversed(value)):
        n = int(ch)
        if i % 2 == 1:
            n = n * 2 - 9 if n * 2 > 9 else n * 2
        total += n
    return total % 10 == 0


def card_number():
    """16 digits from 1-5 only, ending in a valid Luhn check digit."""
    while True:
        body = "".join(map(str, _digits(15, CARD_DIGITS)))
        for check in CARD_DIGITS:
            if luhn_is_valid(body + check):
                return body + check


def unique(generator, model, field):
    while True:
        value = generator()
        if not model.objects.filter(**{field: value}).exists():
            return value
