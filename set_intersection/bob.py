import subprocess
from util import (
    read_to_binary_representation,
    resv_length_of_alice_set,
    get_floats,
    INPUT_BOB,
)
from verifier import ground_truth


def eq_with_alice(i: str) -> bool:
    proc = subprocess.Popen(
        ["python", "../garbled_circuit/main.py", "bob", "-i", i],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out = proc.stdout.readline().decode().strip()
    proc.terminate()

    if out[-1] == "1":
        return True
    else:
        return False


def common_elements_with_alice() -> set[float]:
    bin_repr_maps_to_float = read_to_binary_representation(INPUT_BOB)
    length_set_alice = resv_length_of_alice_set()

    common_elements = set()
    for _ in range(0, length_set_alice):
        for i in bin_repr_maps_to_float:
            if eq_with_alice(i):
                common_elements.add(i)
                break

    return get_floats(common_elements, bin_repr_maps_to_float)


def main():
    common_elements = common_elements_with_alice()

    print(f"Common elements with alice: {common_elements}")
    print(f"Calculation was successful: {common_elements == ground_truth()}")


if __name__ == "__main__":
    main()
