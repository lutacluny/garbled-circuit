# Using Yao's Protocol to Calculate Common Elements of two Sets

I used garbled circuits to calculate the common elements for two parties, Alice and Bob, such that neither Alice nor Bob reveal elements they don't share.

Each set is read from a text-file that contains 32-bit floating point numbers which are separated by a comma. See the [documentation.pdf](./documentation/documentation.pdf) for further details. 

## Setting up the Environment

To get the scripts running, simply create a conda environment via executing `conda env create -f condaEnv.yaml` from the project's root directory.

Afterwards, activate the environment with `conda activate garbled-circuit`.

The environment can be deactivated using `conda deactivate` 

## Running the protocol

1. Enter the [./set_intersection/](set_intersection/) directory from the root directory.

2. Open a second terminal.

3. Activate the conda environment on both shells.

4. Execute `python bob.py` to run bob in one terminal and `python alice.py` to run alice in the other terminal.

5. After the protocol has finished, the common elements are displayed together with a boolean that indicates whether the calculation was successful. 

## Changing the input

In case you want to change the inputs, alter the values in [set_intersection/input_alice.txt](./set_intersection/input_alice.txt) and [set_intersection/input_bob.txt](./set_intersection/input_bob.txt), respectively.

TEST
