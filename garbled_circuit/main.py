#!/usr/bin/env python3
import logging
import ot
import util
import yao
from abc import ABC, abstractmethod
import sys

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.WARNING)


class YaoGarbler(ABC):
    """An abstract class for Yao garblers (e.g. Alice)."""

    def __init__(self, circuits):
        circuits = util.parse_json(circuits)
        self.name = circuits["name"]
        self.circuits = []

        for circuit in circuits["circuits"]:
            garbled_circuit = yao.GarbledCircuit(circuit)
            pbits = garbled_circuit.get_pbits()
            entry = {
                "circuit": circuit,
                "garbled_circuit": garbled_circuit,
                "garbled_tables": garbled_circuit.get_garbled_tables(),
                "keys": garbled_circuit.get_keys(),
                "pbits": pbits,
                "pbits_out": {w: pbits[w] for w in circuit["out"]},
            }
            self.circuits.append(entry)

    @abstractmethod
    def start(self):
        pass


class Alice(YaoGarbler):
    """Alice is the creator of the Yao circuit.

    Alice creates a Yao circuit and sends it to the evaluator along with her
    encrypted inputs. Alice will finally print the truth table of the circuit
    for all combination of Alice-Bob inputs.

    Alice does not know Bob's inputs but for the purpose
    of printing the truth table only, Alice assumes that Bob's inputs follow
    a specific order.

    Attributes:
        circuits: the JSON file containing circuits
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """

    def __init__(self, circuits, oblivious_transfer=True, input=[True, True]):
        super().__init__(circuits)
        self.socket = util.GarblerSocket()
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)
        self.input = input

    def start(self):
        """Start Yao protocol."""
        for circuit in self.circuits:
            to_send = {
                "circuit": circuit["circuit"],
                "garbled_tables": circuit["garbled_tables"],
                "pbits_out": circuit["pbits_out"],
            }
            logging.debug(f"Sending {circuit['circuit']['id']}")
            self.socket.send_wait(to_send)
            self.print(circuit)

    def print(self, entry):
        """Print circuit evaluation for all Bob and Alice inputs.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        circuit, pbits, keys = entry["circuit"], entry["pbits"], entry["keys"]
        outputs = circuit["out"]
        a_wires = circuit.get("alice", [])  # Alice's wires
        a_inputs = {}  # map from Alice's wires to (key, encr_bit) inputs
        b_wires = circuit.get("bob", [])  # Bob's wires
        b_keys = {  # map from Bob's wires to a pair (key, encr_bit)
            w: self._get_encr_bits(pbits[w], key0, key1)
            for w, (key0, key1) in keys.items()
            if w in b_wires
        }
        bits_a = [int(b) for b in self.input]

        # Map Alice's wires to (key, encr_bit)
        for i in range(len(a_wires)):
            a_inputs[a_wires[i]] = (
                keys[a_wires[i]][bits_a[i]],
                pbits[a_wires[i]] ^ bits_a[i],
            )

        # Send Alice's encrypted inputs and keys to Bob
        result = self.ot.get_result(a_inputs, b_keys)

        # Format output
        str_bits_a = " ".join(str(b) for b in bits_a)
        str_result = " ".join([str(result[w]) for w in outputs])

        sys.stdout.write(
            f"Alice{a_wires} = {str_bits_a}, Outputs{outputs} = {str_result}\n"
        )
        sys.stdout.flush()

    def _get_encr_bits(self, pbit, key0, key1):
        return ((key0, 0 ^ pbit), (key1, 1 ^ pbit))


class Bob:
    """Bob is the receiver and evaluator of the Yao circuit.

    Bob receives the Yao circuit from Alice, computes the results and sends
    them back.

    Args:
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """

    def __init__(self, oblivious_transfer=True, input=[True, True]):
        self.socket = util.EvaluatorSocket()
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)
        self.input = input

    def listen(self):
        """Start listening for Alice messages."""
        logging.info("Start listening")
        try:
            for entry in self.socket.poll_socket():
                self.socket.send(True)
                self.send_evaluation(entry)
        except KeyboardInterrupt:
            logging.info("Stop listening")

    def send_evaluation(self, entry):
        """Evaluate yao circuit for all Bob and Alice's inputs and
        send back the results.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        circuit, pbits_out = entry["circuit"], entry["pbits_out"]
        garbled_tables = entry["garbled_tables"]
        outputs = circuit["out"]
        b_wires = circuit.get("bob", [])  # list of Bob's wires

        bits_b = [int(b) for b in self.input]  # Bob's inputs

        # Create dict mapping each wire of Bob to Bob's input
        b_inputs_clear = {b_wires[i]: bits_b[i] for i in range(len(b_wires))}

        # Evaluate and send result to Alice
        result = self.ot.send_result(circuit, garbled_tables, pbits_out, b_inputs_clear)

        # Format output
        str_input_b = " ".join(str(b) for b in bits_b)
        str_result = " ".join([str(result[w]) for w in outputs])

        sys.stdout.write(
            f"Bob{b_wires} = {str_input_b}, Outputs{outputs} = {str_result}\n"
        )
        sys.stdout.flush()


class LocalTest(YaoGarbler):
    """A class for local tests.

    Print a circuit evaluation or garbled tables.

    Args:
        circuits: the JSON file containing circuits
        print_mode: Print a clear version of the garbled tables or
            the circuit evaluation (the default).
    """

    def __init__(self, circuits, print_mode="circuit"):
        super().__init__(circuits)
        self._print_mode = print_mode
        self.modes = {
            "circuit": self._print_evaluation,
            "table": self._print_tables,
        }
        logging.info(f"Print mode: {print_mode}")

    def start(self):
        """Start local Yao protocol."""
        for circuit in self.circuits:
            self.modes[self.print_mode](circuit)

    def _print_tables(self, entry):
        """Print garbled tables."""
        entry["garbled_circuit"].print_garbled_tables()

    def _print_evaluation(self, entry):
        """Print circuit evaluation."""
        circuit, pbits, keys = entry["circuit"], entry["pbits"], entry["keys"]
        garbled_tables = entry["garbled_tables"]
        outputs = circuit["out"]
        a_wires = circuit.get("alice", [])  # Alice's wires
        a_inputs = {}  # map from Alice's wires to (key, encr_bit) inputs
        b_wires = circuit.get("bob", [])  # Bob's wires
        b_inputs = {}  # map from Bob's wires to (key, encr_bit) inputs
        pbits_out = {w: pbits[w] for w in outputs}  # p-bits of outputs
        N = len(a_wires) + len(b_wires)

        print(f"======== {circuit['id']} ========")

        # Generate all possible inputs for both Alice and Bob
        for bits in [format(n, "b").zfill(N) for n in range(2**N)]:
            bits_a = [int(b) for b in bits[: len(a_wires)]]  # Alice's inputs
            bits_b = [int(b) for b in bits[N - len(b_wires) :]]  # Bob's inputs

            # Map Alice's wires to (key, encr_bit)
            for i in range(len(a_wires)):
                a_inputs[a_wires[i]] = (
                    keys[a_wires[i]][bits_a[i]],
                    pbits[a_wires[i]] ^ bits_a[i],
                )

            # Map Bob's wires to (key, encr_bit)
            for i in range(len(b_wires)):
                b_inputs[b_wires[i]] = (
                    keys[b_wires[i]][bits_b[i]],
                    pbits[b_wires[i]] ^ bits_b[i],
                )

            result = yao.evaluate(
                circuit, garbled_tables, pbits_out, a_inputs, b_inputs
            )

            # Format output
            str_bits_a = " ".join(bits[: len(a_wires)])
            str_bits_b = " ".join(bits[len(a_wires) :])
            str_result = " ".join([str(result[w]) for w in outputs])

            print(
                f"  Alice{a_wires} = {str_bits_a} "
                f"Bob{b_wires} = {str_bits_b}  "
                f"Outputs{outputs} = {str_result}"
            )

        print()

    @property
    def print_mode(self):
        return self._print_mode

    @print_mode.setter
    def print_mode(self, print_mode):
        if print_mode not in self.modes:
            logging.error(
                f"Unknown print mode '{print_mode}', "
                f"must be in {list(self.modes.keys())}"
            )
            return
        self._print_mode = print_mode


def main(
    party,
    circuit_path="circuits/default.json",
    oblivious_transfer=True,
    print_mode="circuit",
    loglevel=logging.WARNING,
    input=[True, True],
):
    logging.getLogger().setLevel(loglevel)

    if party == "alice":
        alice = Alice(circuit_path, oblivious_transfer=oblivious_transfer, input=input)
        alice.start()
    elif party == "bob":
        bob = Bob(oblivious_transfer=oblivious_transfer, input=input)
        bob.listen()
    elif party == "local":
        local = LocalTest(circuit_path, print_mode=print_mode)
        local.start()
    else:
        logging.error(f"Unknown party '{party}'")


if __name__ == "__main__":
    import argparse

    def parse_input(string):
        bools = [b == "1" for b in string]
        return bools

    def init():
        loglevels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }

        parser = argparse.ArgumentParser(description="Run Yao protocol.")
        parser.add_argument(
            "party", choices=["alice", "bob", "local"], help="the yao party to run"
        )
        parser.add_argument(
            "-c",
            "--circuit",
            metavar="circuit.json",
            default="circuits/default.json",
            help=("the JSON circuit file for alice and local tests"),
        )
        parser.add_argument(
            "--no-oblivious-transfer",
            action="store_true",
            help="disable oblivious transfer",
        )
        parser.add_argument(
            "-m",
            metavar="mode",
            choices=["circuit", "table"],
            default="circuit",
            help="the print mode for local tests (default 'circuit')",
        )
        parser.add_argument(
            "-l",
            "--loglevel",
            metavar="level",
            choices=loglevels.keys(),
            default="warning",
            help="the log level (default 'warning')",
        )
        parser.add_argument(
            "-i",
            "--input",
            type=parse_input,
            help="input for the wires, e.g. 01 in case of 2 input wires",
        )

        args = parser.parse_args()

        main(
            party=args.party,
            circuit_path=args.circuit,
            oblivious_transfer=not args.no_oblivious_transfer,
            print_mode=args.m,
            loglevel=loglevels[args.loglevel],
            input=args.input,
        )

    init()