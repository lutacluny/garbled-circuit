# from util import BIT_LENGTH
from math import log2
import json
from util import BIT_LENGTH


def gen_gates_to_test_bitwise_eq(
    a_wires: list[int], b_wires: list[int]
) -> tuple[list[dict], list[int], int]:
    gates = []
    gate_ids = []
    next_gate_id = 2 * BIT_LENGTH + 1

    for i in range(0, BIT_LENGTH):
        gate = {"id": next_gate_id, "type": "XNOR", "in": [a_wires[i], b_wires[i]]}
        gates.append(gate)
        gate_ids.append(next_gate_id)
        next_gate_id += 1

    return gates, gate_ids, next_gate_id


def gen_AND_gates_to_assure_that_all_positions_are_eq(
    bitwise_eq_gates: list[dict], gate_ids: list[int], next_gate_id: int
) -> list[dict]:
    gates = bitwise_eq_gates
    current_level = int(log2(BIT_LENGTH))

    while current_level > 1:
        mid = int(2 ** (current_level - 1))
        first_half = gate_ids[:mid]
        second_half = gate_ids[mid:]

        gate_ids = []
        for i in range(0, mid):
            gate = {
                "id": next_gate_id,
                "type": "AND",
                "in": [first_half[i], second_half[i]],
            }
            gates.append(gate)
            gate_ids.append(next_gate_id)
            next_gate_id += 1

        current_level -= 1

    if current_level == 1:
        gate = {"id": next_gate_id, "type": "AND", "in": [gate_ids[0], gate_ids[1]]}
        gates.append(gate)

    return gates


def gen_gates(a_wires: list[int], b_wires: list[int]) -> list[dict]:
    bitwise_eq_gates, gate_ids, next_gate_id = gen_gates_to_test_bitwise_eq(
        a_wires, b_wires
    )
    gates = gen_AND_gates_to_assure_that_all_positions_are_eq(
        bitwise_eq_gates, gate_ids, next_gate_id
    )
    return gates


def main():
    a_wires = list(range(1, BIT_LENGTH + 1))
    b_wires = list(range(BIT_LENGTH + 1, 2 * BIT_LENGTH + 1))
    gates = gen_gates(a_wires, b_wires)
    out_wire = gates[-1].get("id")

    name = f"eq_{BIT_LENGTH}"
    circuit = {
        "name": name,
        "circuits": [
            {
                "id": f"{BIT_LENGTH}-bit EQ",
                "alice": a_wires,
                "bob": b_wires,
                "out": [out_wire],
                "gates": gates,
            }
        ],
    }

    with open(f"../garbled_circuit/circuits/{name}.json", "w") as json_file:
        json.dump(circuit, json_file, indent=2)


if __name__ == "__main__":
    main()
