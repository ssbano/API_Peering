from bgp import BGP
import settings


class SP(BGP):

    def _validaAddressv4Ptt(self, settings_local=settings.RANGE_PTT_SP, local='sp'):
        return super()._validaAddressv4Ptt(settings_local=settings.RANGE_PTT_SP, local='sp')

    def _validaAddressv6Ptt(self, settings_local=settings.RANGE_PTT_SP_V6, local='sp'):
        return super()._validaAddressv6Ptt(settings_local=settings.RANGE_PTT_SP_V6, local='sp')

    def generate_config(self, localidade='sp'):
        return super().generate_config(localidade='sp')