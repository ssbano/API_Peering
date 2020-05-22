# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
import os
import sys
import click
import settings
import datetime
import ipaddress
import requests
import re


class BGP:

    '''
    Classe que cria de forma automatizada configuracoes BGPs
    para se comunicar com a Internet na G.com
    
    '''
    
    def __init__(self):
        self._variables = {
        'asn': None,
        'company': None,
        'local': None,
        'ipv4': list(),
        'ipv6': list(),
    }
    
    def get_conf(self, **kwargs):
        
        """

       inserir comentario
            
        """
        try:
            for i in kwargs.keys():
                self._variables[i] = kwargs.get(i)

            if len(self._variables.get('ipv4')) < len(self._variables.get('ipv6')):
                print('nao suportamos esse tipo de configuracao.\n')
                sys.exit(1)

        except Exception as err:
            raise err

    def ptt_conf(self):
        
        """
        
        Cria a configuracao BGP para fechar a sessao via ptt
        
        """
        #interfaces ve so existem no rj

        if self._variables.get('interface_ve'):
            if self._variables.get('local') != 'rj':
                print('Nao ha interfaces virtuais na configuracao BGP desse local')
                sys.exit(1)
            if len(self._variables.get('interface_ve')) != len(self._variables.get('ipv4')):
                print('O numero de interfaces virtuais fornecidas nao e compativel com a quantidade de sessoes BGP a serem fechadas\n')
                sys.exit(1)
        
        if len(self._variables.get('desc_vlan')) != len(self._variables.get('vlan')):
            print('O numero de descricoes de vlans e menor do que a quantidade de vlans a serem configuradas.'
                 'Informar a descricao para todas as vlans informadas')
            sys.exit(1)
        
        elif len(self._variables.get('vlan')) != len(self._variables.get('ipv4')):
            print('O numero de vlans informadas nao e compativel com a quantidade de sessoes BGP a serem configuradas.'
                  'Favor informar todas as vlans que serao usadas.')
            sys.exit(1)


    def _validarepIp(self):

        """
        Verifica se nao ha ips repetidos passados pelo usuario nos campos de host
        
        """

        rep_v4 = [x for x in self._variables.get('host_v4') if x.split('/')[0] in self._variables.get('ipv4')]
        if len(rep_v4) > 0:
            print(f"Os ips {rep_v4} estao repetidos na configuracao. Favor verificar o que esta sendo pedindo")
            sys.exit(1)

        if self._variables.get('ipv6'):
            rep_v6 = [x for x in self._variables.get('host_v6') if x.split('/')[0] in self._variables.get('ipv6')]
            if len(rep_v6) > 0:
                print(f"Os ips {rep_v6} estao repetidos na configuracao. Favor verificar o que esta sendo pedindo")
                sys.exit(1)


    def checa_ASN(ctx, param, value):
        '''
        Valida se o ASN passado pelo usuario esta dentro do range permitido

        ctx: contexto do click
        param: nao e usado
        value: valor passado pelo usuario via cli
        
        '''
        try:
            value = int(value)

            if (value <= 0) or (value in range(56320,64511)) or (value == 65535):
                print(f"ASN {value} invalido. Esse ASN faz parte de um range reservado pelo IANA."
                    " Favor verificar junto ao provedor o ASN correto.")
                ctx.abort()
            elif value in range(64512,65534):
                print("ASN {value} invalido. Esse ASN faz parte de um range que foi definido para fins privados"
                    "e nao roteaveis pela internet. Favor verificar com o provedor o ASN correto.")
                ctx.abort()
            else:
                return value
        except ValueError:
            print(f'Valor {value} invalido.')
            ctx.abort()

    @staticmethod
    def validateIpv4(ctx, param, value):
        '''
        Validar se os enderecos utilizados para
        o peering sao enderecos publicos.

        ctx: contexto do click
        param: nao e usado
        value: valor passado pelo usuario via cli

        '''
        valid_ips = list()

        try:
            for ip in value:
                try:
                    ip = ip.split('/')[0]
                    public = ipaddress.ip_address(ip).is_global
                    multicast = ipaddress.ip_address(ip).is_multicast
                    if public and not multicast:
                        valid_ips.append(ip)
                    else:
                        print(f'O endereço {ip} informado nao e um endereco valido. A Globo.com'
                                    ' nao estabelece peerings com ips que nao sao publicos. \n'
                                    'Favor entrar em contato com a operadora.')
                        ctx.abort()
                except ValueError as err:
                        print(f"O endereco {ip} nao e um endereco valido! "
                                "Validar com a operadora o endereco correto")
                        ctx.abort()
            same_ip = set(valid_ips)
            # verifica se o usuario passou o mesmo ip na cli
            if len(same_ip) < len(valid_ips):
                print('Ha ips duplicados nessa configuracao. Por favor, verificar os valores corretos.')
                sys.exit(1)
            return valid_ips
        except Exception as err:
            print(err)
            ctx.abort()
            

    def _validaAddressv4Ptt(self, settings_local=None, local=None):
        '''
        
        Valida se o endereco passado esta dentro do range 
        definido pelo PTT da localidade
        
        '''
        for address in self._variables.get('ipv4'):
            if not ipaddress.ip_address(address) in ipaddress.IPv4Network(settings_local):
                print(f'O {address} nao faz parte do range de enderecos do PTT-{local.upper()}.\n'
                      f'O range atual e {settings_local}. Validar o local e o endereco ipv4.')
                sys.exit(1)
            
    

    def _validaAddressv6Ptt(self, settings_local=None, local=None):
        '''
        
        Valida se o endereco ipv6 passado esta dentro do range 
            definido pelo PTT da localidade
            
        '''    
        for address in self._variables.get('ipv6'):
            if not ipaddress.ip_address(address) in ipaddress.IPv6Network(settings_local):
                print(f'O {address} nao faz parte do range de enderecos do PTT-{local.upper()}.\n'
                      f'O range atual e {settings_local}. Validar o local e o endereco ipv6.')
                sys.exit(1)

   
    @staticmethod
    def valida_ipv6(ctx, param, value):
        
        '''
        Verifica se o ipv6 informado via cli e valido

        ctx: contexto do click
        param: nao e usado
        value: valor passado pelo usuario via cli

        '''

        valid_ipv6 = list()

        for ipv6 in value:
            try:
                valor = ipv6.split('/')[0]
                result = ipaddress.IPv6Address(valor)
                valid_ipv6.append(valor)
            except Exception:
                print(f"O {ipv6} nao e um endereco ipv6 valido."
                        " Validar com a operadora o endereco ipv6 correto.")
                ctx.abort()    
        # verifica se o usuario passou o mesmo ip na cli
        same_ipv6 = set(valid_ipv6)
        if len(same_ipv6) < len(valid_ipv6):
            print('Foram passados ipv6s duplicados. Por favor, verificar os valores corretos.')
            sys.exit(1)
        return valid_ipv6

    @staticmethod

    def generate_config(self, localidade=None):
        
        """Gera a configuracao usando so templates jinja e as variaveis"""

        date = datetime.date.today()

        #formatando a saida de acordo com o tipo de arquivo a ser salvo
        arq_saida = f"{settings.SAIDA}{localidade.upper()}/{self._variables['tipo'].upper()}/"

        try:
            #caso nao exista o diretorio, tentar cria-lo
            try:
                os.makedirs(arq_saida)
            except FileExistsError:
                pass

            output_file = f"{self._variables['asn']}_{self._variables['nome']}_{localidade.upper()}_{self._variables['tipo'].upper()}_{date}"
            file_loader = FileSystemLoader(settings.TEMPLATES)
            env = Environment(loader=file_loader)

            template = env.get_template(f"{localidade.upper()}.j2")

            output = template.render(conf=self._variables)

            with open(f"{arq_saida}{output_file}.txt", "w") as outfile:
                    outfile.write(output)
            
            print(f"Arquivo de configuracao salvo em {arq_saida}{output_file}.txt")

        except Exception as err:
            raise err

    def validaASN(self, asn, nome):
        '''
            Funcao que valida informacoes para o usuario usando a api do peeringdb

            asn: asn informado pelo usuario
            nome: nome da operadora
        '''
        peeringdb = 'https://peeringdb.com/api/'
        route_api = 'netixlan.json?asn='
        
        uri = f'{peeringdb}{route_api}{asn}'
        try:
            response = requests.get(uri, timeout=3)
            if response.status_code == 200:
                r = response.json()

                print(f'Abaixo estao todos os locais em que {nome} pode fechar uma sessao BGP\n')

                try:
                    for ix in r['data']:
                        print(ix['name'], end='\n')
                        print(ix['ipaddr4'], end='\n')
                        if ix['ipaddr6']:
                            print(ix['ipaddr6'], end='\n\n')
                        else:
                            print('Nao ha enderecos ipv6 cadastrado', end='\n\n')
                except KeyError:
                    print('Houve alguma alteracao na API do peeringdb. '
                        'Validar o json da rota usada\n')
                    sys.exit(1)
            else:
                print('A consulta ao peeringdb falhou. Validar se a API esta funcionando corretamente.')
                sys.exit(1)
        
        except requests.ConnectionError:
            print(f'A rota para acessar a api do peeringdb {peeringdb}{route_api} esta incorreta. Favor validar\n')
            sys.exit(1)
        except Exception:
            raise
    
    def __repr__(self):
        return(f'\nAutomacao de Peering BGP.\nAs variaveis usadas estao abaixo:\n{str(self._variables)}')
        