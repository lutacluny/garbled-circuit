# from util import BIT_LENGTH
from math import log2
import json
from util import BIT_LENGTH

BIT_LENGTH = 4
def gen_gates(a_wires, b_wires):
    gates = []
    gate_ids = []
    gate_id = 2 * BIT_LENGTH + 1

    for i in range(0, BIT_LENGTH):
        gate = {"id": gate_id, "type": "XNOR", "in": [a_wires[i], b_wires[i]]}
        gates.append(gate)
        gate_ids.append(gate_id)
        gate_id += 1

    current_level = int(log2(BIT_LENGTH))

    while current_level > 1:
        mid = int(2 ** (current_level - 1))
        first_half = gate_ids[:mid]
        second_half = gate_ids[mid:]

        gate_ids = []
        for i in range(0, mid):
            gate = {"id": gate_id, "type": "AND", "in": [first_half[i], second_half[i]]}
            gates.append(gate)
            gate_ids.append(gate_id)
            gate_id += 1

        current_level -= 1

    if current_level == 1:
        gate = {"id": gate_id, "type": "AND", "in": [gate_ids[0], gate_ids[1]]}
        gates.append(gate)

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

    with open(f'garbled_circuit/circuits/{name}.json', 'w') as json_file:
        json.dump(circuit, json_file, indent=2)


if __name__ == "__main__":
    main()
