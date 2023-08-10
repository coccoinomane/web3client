#!/usr/bin/python3

from sys import argv

from ape import accounts, project


def main() -> None:
    """Deploy Compound cETH money market"""
    alice = accounts.test_accounts[0]
    comptroller = project.Comptroller.deploy(sender=alice)
    ir_model = project.WhitePaperInterestRateModel.deploy(
        0, 200000000000000000, sender=alice
    )
    ceth = project.CEther.deploy(
        comptroller,
        ir_model,
        200000000000000000000000000,
        "CompoundEther",
        "cETH",
        8,
        alice,
        sender=alice,
    )
    # If everything went fine, we need to raise an exception to allow
    # the user to interact with the contracts in interactive mode
    if "-I" in argv or "--interactive" in argv:
        raise Exception(
            "Script completed successfully, now allowing you to use interactive mode"
        )
