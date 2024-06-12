import struct
import random

BIT_LENGTH = 32
INPUT_BOB = "input_bob.txt"
INPUT_ALICE = "input_alice.txt"


def read_to_binary_representation(file_path: str) -> set[str]:
    s = read_to_set(file_path)

    return set(map(float_to_binary, s))

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


def convert_to_float(bin_set: set[str]) -> set[float]:
    return set(map(binary_to_float, bin_set))


def binary_to_float(b: str) -> float:
    if len(b) != BIT_LENGTH:
        raise Exception(f"Binary string length has to be {BIT_LENGTH}.")

    integer_representation = int(b, 2)
    packed = struct.pack("!I", integer_representation)
    unpacked = struct.unpack("!f", packed)[0]

    return unpacked


def resv_length_of_bobs_set() -> int:
    with open(INPUT_BOB, "r") as file:
        content = file.read()
        return len(content.split(","))


def resv_length_of_alice_set() -> int:
    with open(INPUT_ALICE, "r") as file:
        content = file.read()
        return len(content.split(","))

