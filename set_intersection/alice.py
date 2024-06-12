import subprocess
from util import (
    read_to_binary_representation,
    convert_to_float,
    resv_length_of_bobs_set,
    BIT_LENGTH,
    INPUT_ALICE,
)
from verifier import ground_truth


def eq_with_bob(i: str) -> bool:
    proc = subprocess.Popen(
        [
            "python",
            "../garbled_circuit/main.py",
            "alice",
            "-c",
            f"../garbled_circuit/circuits/eq_{BIT_LENGTH}.json",
            "-i",
            i,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = proc.communicate()

    if err:
        print(err)

    out = out.decode().strip()

    if out[-1] == "1":
        return True
    else:
        return False

def common_elements_with_bob() -> set[float]:
    set_a = read_to_binary_representation(INPUT_ALICE)
    length_set_bob = resv_length_of_bobs_set()

    common_elements = set()
    for i in set_a:
        for _ in range(0, length_set_bob):
            if eq_with_bob(i):
                common_elements.add(i)
                break

    return convert_to_float(common_elements)

def main():
    common_elements = common_elements_with_bob()
    
    print(common_elements)
    print(common_elements == ground_truth())


if __name__ == "__main__":
    main()
