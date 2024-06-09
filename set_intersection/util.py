import struct

BIT_LENGTH = 32
INPUT_BOB = "input_bob.txt"
INPUT_ALICE = "input_alice.txt"


def read_to_set(file_path: str) -> set[str]:
    with open(file_path, "r") as file:
        content = file.read()
        floats_set = set(map(float, content.split(",")))
        return convert_to_binary(floats_set)


def convert_to_binary(floats_set: set[float]) -> set[str]:
    return set(map(float_to_binary, floats_set))


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


def resv_length_of_bobs_set():
    with open(INPUT_BOB, "r") as file:
        content = file.read()
        return len(content.split(","))


def resv_length_of_alice_set():
    with open(INPUT_ALICE, "r") as file:
        content = file.read()
        return len(content.split(","))
