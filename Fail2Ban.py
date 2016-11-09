#!/usr/bin/env python

import commands

#jail_count = 0
#jail_count = int(commands.getoutput('fail2ban-client status|grep "Number" |cut -f 2'))

jail_list = commands.getoutput('fail2ban-client status|grep "list" |cut -f 3')
jail_list = jail_list.split(', ')

for jail in jail_list:
  ip_string = commands.getoutput('fail2ban-client status '+ jail +'|grep "IP list" |cut -f 2')

  if ip_string != '':
    ip_list = ip_string.split(' ')
    temp_bans = len(ip_list)

# Count blacklist bans

bl_bans = commands.getoutput('cat /etc/fail2ban/ip.blacklist | sed \'/^\s*$/d\' | wc -l')

class Fail2Ban (object):
  def __init__(self, agentConfig, checksLogger, rawConfig):
    self.agentConfig = agentConfig
    self.checksLogger = checksLogger
    self.rawConfig = rawConfig

  def run(self):
    data = {}
    data['TemporaryBans'] = temp_bans
    data['PersistentBans'] = bl_bans
    return data
