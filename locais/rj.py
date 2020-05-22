from bgp import BGP
import settings


class RJ(BGP):

    def generate_config(self, localidade='rj'):
        return super().generate_config(localidade='rj')

    def _validaAddressv4Ptt(self, settings_local=settings.RANGE_PTT_RJ, local='rj'):
        return super()._validaAddressv4Ptt(settings_local=settings.RANGE_PTT_RJ, local='rj')

    def _validaAddressv6Ptt(self, settings_local=settings.RANGE_PTT_RJ_V6, local='rj'):
        return super()._validaAddressv6Ptt(settings_local=settings.RANGE_PTT_RJ_V6, local='rj')