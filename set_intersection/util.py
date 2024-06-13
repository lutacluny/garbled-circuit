import struct
import random

BIT_LENGTH = 32
INPUT_BOB = "input_bob.txt"
INPUT_ALICE = "input_alice.txt"


def read_to_binary_representation(file_path: str) -> dict[str:float]:
    floats = read_to_set(file_path)
    repr = {}

    for f in floats:
        repr[float_to_binary(f)] = f

    return repr


def read_to_set(file_path: str) -> set[float]:
    with open(file_path, "r") as file:
        content = file.read()
        floats = list(map(float, content.split(",")))
        random.shuffle(floats)

        return set(floats)


def float_to_binary(f: float) -> str:
    packed = struct.pack("!f", f)
    unpacked = struct.unpack("!I", packed)[0]

    if BIT_LENGTH != 32:
        raise Exception("BIT_LENGTH constant has to be 32.")

    return f"{unpacked:032b}"


def get_floats(
    bit_strings: set[str], bin_representations: dict[str:float]
) -> set[float]:
    floats = set()

    for bit_string in bit_strings:
        floats.add(bin_representations[bit_string])

    return floats


def resv_length_of_bobs_set() -> int:
    with open(INPUT_BOB, "r") as file:
        content = file.read()
        return len(content.split(","))


def resv_length_of_alice_set() -> int:
    with open(INPUT_ALICE, "r") as file:
        content = file.read()
        return len(content.split(","))
