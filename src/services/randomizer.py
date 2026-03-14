import string
from random import choice

nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

def generate_random_number_str(n: int) -> str:
    number = ""
    for i in range(n):
        number += choice(nums)
    return number