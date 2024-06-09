import subprocess
from util import (
    read_to_set,
    convert_to_float,
    resv_length_of_bobs_set,
    BIT_LENGTH,
    INPUT_ALICE,
)


def eq_with_bob(i: str) -> bool:
    proc = subprocess.Popen(
        [
            "python",
            "garbled_circuit/main.py",
            "alice",
            "-c",
            f"garbled_circuit/circuits/eq_{BIT_LENGTH}.json",
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
    #print(out)

    if out[-1] == "1":
        return True
    else:
        return False


def main():
    set_a = read_to_set(INPUT_ALICE)
    length_set_bob = resv_length_of_bobs_set()

    common_elements = set()
    for i in set_a:
        for _ in range(0, length_set_bob):
            if eq_with_bob(i):
                common_elements.add(i)

    print(convert_to_float(common_elements))


if __name__ == "__main__":
    main()
