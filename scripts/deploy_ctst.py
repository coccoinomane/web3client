from ape import accounts, project


def main() -> None:
    """Deploy Compound cTST money market, where TST
    is a test token"""
    alice = accounts.test_accounts[0]

    tst = project.Token.deploy(
        "Test token", "TST", 18, 10**9 * 10**18, sender=alice
    )

    comptroller = project.Comptroller.deploy(sender=alice)

    ir_model = project.WhitePaperInterestRateModel.deploy(
        0, 200000000000000000, sender=alice
    )

    ctst = project.CErc20Immutable.deploy(
        tst,
        comptroller,
        ir_model,
        200000000000000000000000000,
        "CompoundTST",
        "cTST",
        8,
        alice,
        sender=alice,
    )

    comptroller._supportMarket(ctst, sender=alice)
