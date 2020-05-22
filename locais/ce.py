from bgp import BGP
import settings

class CE(BGP):


        def _validaAddressv4Ptt(self, local='sp'):
            return super()._validaAddressv4Ptt( local='ce')

        def _validaAddressv6Ptt(self, local='sp'):
            return super()._validaAddressv6Ptt( local='ce')

        def generate_config(self, localidade='sp'):
            return super().generate_config(localidade='ce')