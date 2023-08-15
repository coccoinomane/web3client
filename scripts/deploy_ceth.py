from ape import accounts, project


def main() -> None:
    """Deploy Compound cETH money market.  Refer to deploy_ctst
    for more detailed comments."""
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
    ceth.mint(sender=alice, value=100 * 10**18)
    oracle = project.FixedPriceOracle.deploy(10**18, sender=alice)
    comptroller._setPriceOracle(oracle, sender=alice)
    comptroller._setCollateralFactor(ceth, 9 * 10**17, sender=alice)
    comptroller.enterMarkets([ceth], sender=alice)
    ceth.borrow(10 * 10**18, sender=alice)
