# Support for the MimasV2

from fractions import Fraction

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer


class _CRG(Module):
    def __init__(self, platform, clk_freq):
        # Clock domains for the system (soft CPU and related components run at).
        self.clock_domains.cd_sys = ClockDomain()
        # Clock domain for peripherals (such as HDMI output).
        # self.clock_domains.cd_base50 = ClockDomain()

        self.reset = Signal()

        # Input 100MHz clock
        f0 = 100*1000000
        clk100 = platform.request("clk100")
        clk100a = Signal()
        # Input 100MHz clock (buffered)
        self.specials += Instance("IBUFG", i_I=clk100, o_O=clk100a)
        clk100b = Signal()
        self.specials += Instance(
            "BUFIO2", p_DIVIDE=1,
            p_DIVIDE_BYPASS="TRUE", p_I_INVERT="FALSE",
            i_I=clk100a, o_DIVCLK=clk100b)

        p = 8
        f = Fraction(clk_freq*p, f0)
        n, d = f.numerator, f.denominator
        assert 19e6 <= f0/d <= 500e6  # pfd
        assert 400e6 <= f0*n/d <= 1080e6  # vco

        # Unbuffered output signals from the PLL. They need to be buffered
        # before feeding into the fabric.
        unbuf_sdram_full = Signal()
        unbuf_sdram_half_a = Signal()
        unbuf_sdram_half_b = Signal()
        unbuf_unused = Signal()
        unbuf_sys = Signal()
        unbuf_periph = Signal()

        # PLL signals
        """pll_lckd = Signal()
        pll_fb = Signal()
        self.specials.pll = Instance(
            "PLL_BASE",
            name="crg_pll_base",
            p_SIM_DEVICE="SPARTAN6", p_BANDWIDTH="OPTIMIZED", p_COMPENSATION="INTERNAL",
            p_REF_JITTER=.01,
            i_RST=0,
            p_DIVCLK_DIVIDE=d,
            # Input Clocks (100MHz)
            i_CLKIN=clk100b,
            # Feedback
            i_CLKFBIN=pll_fb,
            o_LOCKED=pll_lckd,
            p_CLK_FEEDBACK="CLKFBOUT",
            p_CLKFBOUT_MULT=n, p_CLKFBOUT_PHASE=0.,
            # ( 50MHz) periph
            o_CLKOUT4=unbuf_periph, p_CLKOUT4_DUTY_CYCLE=.5,
            p_CLKOUT4_PHASE=0., p_CLKOUT4_DIVIDE=p//1,
            # ( ??MHz) sysclk
            o_CLKOUT5=unbuf_sys, p_CLKOUT5_DUTY_CYCLE=.5,
            p_CLKOUT5_PHASE=0., p_CLKOUT5_DIVIDE=p//1,
        )"""


        # power on reset?
        led0 = platform.request("user_led", 0)
        led1 = platform.request("user_led", 1)
        led2 = platform.request("user_led", 2)
        led3 = platform.request("user_led", 3)
        btn0 = platform.request("user_btn", 0)
        btn1 = platform.request("user_btn", 1)
        btn2 = platform.request("user_btn", 2)
        btn3 = platform.request("user_btn", 3)
        self.comb += [
            led0.eq(btn0),
            led1.eq(btn1),
            led2.eq(btn2),
            led3.eq(btn3)
        ]

        reset = ~btn0 | ~btn1 | ~btn2 | ~btn3 | self.reset
        self.clock_domains.cd_por = ClockDomain()
        por = Signal(max=1 << 11, reset=(1 << 11) - 1)
        self.sync.por += If(por != 0, por.eq(por - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, reset)

        # System clock - ??MHz
        self.specials += Instance("BUFG", name="sys_bufg", i_I=unbuf_sys, o_O=self.cd_sys.clk)
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        # self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll_lckd | (por > 0))
        self.specials += AsyncResetSynchronizer(self.cd_sys, (por > 0))

