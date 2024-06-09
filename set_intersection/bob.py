import subprocess
from util import read_to_set, convert_to_float, resv_length_of_alice_set, INPUT_BOB


def eq_with_alice(i: str) -> bool:
    proc = subprocess.Popen(
        ["python", "../garbled_circuit/main.py", "bob", "-i", i],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out = proc.stdout.readline().decode().strip()
    # print(out)
    proc.terminate()

    if out[-1] == "1":
        return True
    else:
        return False


def main():
    set_b = read_to_set(INPUT_BOB)
    length_set_alice = resv_length_of_alice_set()

    common_elements = set()
    for _ in range(0, length_set_alice):
        for i in set_b:
            if eq_with_alice(i):
                common_elements.add(i)

    print(convert_to_float(common_elements))


if __name__ == "__main__":
    main()
