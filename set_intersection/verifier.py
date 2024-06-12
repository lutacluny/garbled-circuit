from util import INPUT_ALICE, INPUT_BOB, read_to_set

def ground_truth():
    set_a = read_to_set(INPUT_ALICE)
    set_b = read_to_set(INPUT_BOB)
    
    return set_a.intersection(set_b)