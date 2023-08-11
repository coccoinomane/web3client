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

    comptroller._supportMarket(ceth, sender=alice)
