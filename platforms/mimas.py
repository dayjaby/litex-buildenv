from migen import *
from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

_io = [
    ("clk100", 0, Pins("P126"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("P44"), IOStandard("LVCMOS33"),
                  Misc("SLEW=FAST")),
        Subsignal("rx", Pins("P43"), IOStandard("LVCMOS33"),
                  Misc("SLEW=FAST"))),

    ("spiflash", 0,
        Subsignal("cs_n", Pins("P38"), IOStandard("LVCMOS33")), # SCS - IO_L65N_CSO_B_2
        Subsignal("clk",  Pins("P70"), IOStandard("LVCMOS33")), # SCK - IO_L1P_CCLK_2
        Subsignal("mosi", Pins("P64"), IOStandard("LVCMOS33")), # SDO - IO_L3N_MOSI_CSI_B_MISO0_2
        Subsignal("miso", Pins("P65"), IOStandard("LVCMOS33"))  # SDI - IO_L3P_D0_DIN_MISO_MISO1_2
    ),

    ("user_btn", 0, Pins("P124"), IOStandard("LVCMOS33"), Misc("PULLUP")),
    ("user_btn", 1, Pins("P123"), IOStandard("LVCMOS33"), Misc("PULLUP")),
    ("user_btn", 2, Pins("P121"), IOStandard("LVCMOS33"), Misc("PULLUP")),
    # use 4th button as reset
    ("user_btn", 3, Pins("P120"), IOStandard("LVCMOS33"), Misc("PULLUP")),

    ("user_led", 0, Pins("P119"), IOStandard("LVCMOS33"), Drive(8)),
    ("user_led", 1, Pins("P118"), IOStandard("LVCMOS33"), Drive(8)),
    ("user_led", 2, Pins("P117"), IOStandard("LVCMOS33"), Drive(8)),
    ("user_led", 3, Pins("P116"), IOStandard("LVCMOS33"), Drive(8)),
    ("user_led", 4, Pins("P115"), IOStandard("LVCMOS33"), Drive(8)),
    ("user_led", 5, Pins("P114"), IOStandard("LVCMOS33"), Drive(8)),
    ("user_led", 6, Pins("P112"), IOStandard("LVCMOS33"), Drive(8)),
    ("user_led", 7, Pins("P111"), IOStandard("LVCMOS33"), Drive(8)),

]

class Platform(XilinxPlatform):
    name = "mimas"
    default_clk_name = "clk100"
    default_clk_period = 10

    # The Mimas has a XC6SLX9 which bitstream takes up ~2.6Mbit (1484472 bytes)
    gateware_size = 0x80000

    # M25P16 - component U1
    # 16Mb - 75 MHz clock frequency
    spiflash_model = "m25p16"
    spiflash_read_dummy_bits = 8
    spiflash_clock_div = 4
    spiflash_total_size = int((16/8)*1024*1024) # 16Mbit
    spiflash_page_size = 256
    spiflash_sector_size = 0x10000

    def __init__(self):
        XilinxPlatform.__init__(self, "xc6slx9-tqg144", _io, toolchain="ise")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)

    def create_programmer(self):
        raise NotImplementedError
