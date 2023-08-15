from ape import accounts, project


def main() -> None:
    """Deploy Compound cTST money market, where TST
    is a test token"""
    alice = accounts.test_accounts[0]

    # Deploy underlying token, comptroller, interest rate model, and cTST
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

    # List cTST market in the comptroller
    comptroller._supportMarket(ctst, sender=alice)

    # Alice supplies 100 TST to the Compound cTST market
    tst.approve(ctst, 100 * 10**18, sender=alice)
    ctst.mint(100 * 10**18, sender=alice)

    # All assets will have price of 1 ETH
    oracle = project.FixedPriceOracle.deploy(10**18, sender=alice)
    comptroller._setPriceOracle(oracle, sender=alice)

    # Set colletaral factor to 90%
    comptroller._setCollateralFactor(ctst, 9 * 10**17, sender=alice)

    # Alice borrows 10 TST from the Compound cTST market
    comptroller.enterMarkets([ctst], sender=alice)
    ctst.borrow(10 * 10**18, sender=alice)
