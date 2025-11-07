from sat1_control.utils.i2c_interface import I2cInterface
from sat1_control.tas2780.consts import *

def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))

class Tas2780:
    vol_range_min = 0
    vol_range_max = 1.0

    def __init__(self):
        self.i2c = I2cInterface(AMP_I2C_ADDRESS)
        self.volume = 0.8
        self.amp_level = 8
        self.power_mode = 0
 
    def init(self):
        self.i2c.write(TAS2780_PAGE_SELECT, 0x00) 
            
        # software reset
        self.i2c.write(0x01, 0x01)

        self.i2c.write(TAS2780_PAGE_SELECT, 0x00)
        self.i2c.write(TAS2780_TDM_CFG5, 0x44)
        self.i2c.write(TAS2780_TDM_CFG6, 0x40)

        self.i2c.write(TAS2780_PAGE_SELECT, 0x01)
        self.i2c.write(TAS2780_LSR, 0x00)
        self.i2c.write(TAS2780_INIT_0, 0xC8)
        self.i2c.write(TAS2780_INIT_1, 0x00)
        self.i2c.write(TAS2780_INIT_2, 0x74)

        self.i2c.write(TAS2780_PAGE_SELECT, 0xFD)
        self.i2c.write(0x0D, 0x0D)
        self.i2c.write(TAS2780_INIT_3, 0x4a)
        self.i2c.write(0x0D, 0x00)

        self.i2c.write(TAS2780_PAGE_SELECT, 0x00)

        self.set_power_mode_()

        self.i2c.write(TAS2780_PVDD_UVLO, 0x03)

        self.i2c.write(TAS2780_PAGE_SELECT, 0x00)

        self.i2c.write(TAS2780_INT_MASK4, 0xFF)

        self.i2c.write(TAS2780_INT_MASK2, 0xFF)
        self.i2c.write(TAS2780_INT_MASK3, 0xFF)
        self.i2c.write(TAS2780_INT_MASK1, 0xFF)

        reg_0x5c = self.i2c.read(TAS2780_INT_CLK_CFG)

        self.i2c.write(TAS2780_INT_CLK_CFG, (reg_0x5c & ~0x03) | 0x00)

        self.update_register()

    def setup(self):
        self.init()
        # set to software shutdown
        self.i2c.write(TAS2780_MODE_CTRL, (TAS2780_MODE_CTRL_BOP_SRC__PVDD_UVLO & ~TAS2780_MODE_CTRL_MODE_MASK) | TAS2780_MODE_CTRL_MODE__SFTW_SHTDWN)

    def activate(self):
        self.i2c.write(TAS2780_INT_CLK_CFG, 0x19 | (1 << 2))
        self.write_volume()
        self.init()
        self.i2c.write(TAS2780_MODE_CTRL, (TAS2780_MODE_CTRL_BOP_SRC__PVDD_UVLO & ~TAS2780_MODE_CTRL_MODE_MASK) | TAS2780_MODE_CTRL_MODE__ACTIVE)

    def deactivate(self):
        # set to software shutdown
        self.i2c.write(TAS2780_MODE_CTRL, (TAS2780_MODE_CTRL_BOP_SRC__PVDD_UVLO & ~TAS2780_MODE_CTRL_MODE_MASK) | TAS2780_MODE_CTRL_MODE__SFTW_SHTDWN)

    def set_power_mode_(self):
        chnl_0 = self.i2c.read(TAS2780_CHNL_0)
        self.i2c.write(TAS2780_CHNL_0, (chnl_0 & ~TAS2780_CHNL_0_CDS_MODE_MASK) | (POWER_MODES[self.power_mode][0] << TAS2780_CHNL_0_CDS_MODE_SHIFT))

        dc_blk0 = self.i2c.read(TAS2780_DC_BLK0)
        self.i2c.write(TAS2780_DC_BLK0, (dc_blk0 & ~(1 << TAS2780_DC_BLK0_VBAT1S_MODE_SHIFT)) | (POWER_MODES[self.power_mode][1] << TAS2780_DC_BLK0_VBAT1S_MODE_SHIFT))

    def write_volume(self):
        """
        V_{AMP} = INPUT + A_{DVC} + A_{AMP}
        
        V_{AMP} is the amplifier output voltage in dBV ()
        INPUT: digital input amplitude as a number of dB with respect to 0 dBFS
        A_{DVC}: is the digital volume control setting as a number of dB (default 0 dB)
        A_{AMP}: the amplifier output level setting as a number of dBV

        DVC_LVL[7:0] :            0dB to -100dB [0x00, 0xC8] c8 = 200
        AMP_LEVEL[4:0] : @48ksps 11dBV - 21dBV  [0x00, 0x14]
        """ 
        range_len = self.vol_range_max - self.vol_range_min
        volume = self.volume * range_len + self.vol_range_min

        attenuation = (1.0 - volume) * 100.0
        dvc = clamp(int(round(attenuation)), 0, 0xC8)        
        self.i2c.write(TAS2780_DVC, dvc)

    def update_register(self):
        #// AMP_LEVEL
        reg_val = self.i2c.read(TAS2780_CHNL_0)
        reg_val &= ~TAS2780_CHNL_0_AMP_LEVEL_MASK
        reg_val |= self.amp_level << TAS2780_CHNL_0_AMP_LEVEL_SHIFT

        self.i2c.write(TAS2780_CHNL_0, reg_val) 

        #// CHANNEL_SELECT
        self.i2c.write(TAS2780_TDM_CFG2, (
            TAS2780_TDM_CFG2_RX_SCFG__STEREO_DWN_MIX |
            TAS2780_TDM_CFG2_RX_WLEN__32BIT |
            TAS2780_TDM_CFG2_RX_SLEN__32BIT
        ))  

    @property
    def is_active(self):
        res = self.i2c.read(TAS2780_MODE_CTRL)
        if res & 7 == 2:
            return True
        return False

    @property
    def is_muted(self):
        res = self.i2c.read(TAS2780_DVC)
        if res == 201:
            return True
        return False

    def mute_on(self):
        self.i2c.write(TAS2780_DVC, 0xC9)
    
    def mute_off(self):
        self.write_volume()