from paramiko import SSHClient
from
import paramiko

class SSH:
 def __init__(self):
 self.ssh = SSHClient()
 self.ssh.load_system_host_keys()
 self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 self.ssh.connect(hostname='ip',username='username',password='MinhaSenhaSegura')

 def exec_cmd(self,cmd):
 stdin,stdout,stderr = self.ssh.exec_command(cmd)
 if stderr.channel.recv_exit_status() != 0:
 print (stderr.read())
 else:
 result_string = stdout.read()
 return result_string

if __name__ == '__main__':
 ssh = SSH()
 missing_packages = 0
 result = ssh.exec_cmd("echo sucesso")