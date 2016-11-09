#!/usr/bin/env python

from xmlrpclib import ServerProxy

import sys
sys.path.append('/usr/lib/python2.7/dist-packages/')
import ESL
import psycopg2

import os
import re

# Connectiong settings for FreeSWITCH XML RPC
FS_HOST = os.getenv('FS_HOST', 'localhost')
FS_PORT = os.getenv('FS_PORT', 8080)
FS_USERNAME = os.getenv('FS_USERNAME', 'freeswitch')
FS_PASSWORD = os.getenv('FS_PASSWORD', 'works')

server = ServerProxy("http://%s:%s@%s:%s" % (FS_USERNAME,
                                             FS_PASSWORD,
                                             FS_HOST,
                                             FS_PORT))


def getCdr():
  try:
    conn = psycopg2.connect("dbname='fusionpbx' user='serverdensity' host='localhost' password='n9TNBK9vpY8wgKwD'")
  except:
    print "I am unable to connect to the database"

  cur = conn.cursor()
  cur.execute("""SELECT MIN(rtp_audio_in_mos) as min, MAX(rtp_audio_in_mos) as max, AVG(rtp_audio_in_mos) as avg FROM v_xml_cdr WHERE rtp_audio_in_mos IS NOT NULL AND answer_stamp > NOW() - INTERVAL '5 minutes'""")
  rows = cur.fetchall()
  result = {'mosmin': rows[0][0], 'mosmax': rows[0][1], 'mosavg': rows[0][2]}
  cur.execute("""SELECT AVG((cdr.msec::float + cdr.psec::float) / 1000) as pdd_avg, MAX((cdr.msec::float + cdr.psec::float) / 1000) as pdd_max FROM (
    SELECT json->'variables'->>'progress_mediamsec' as msec, json->'variables'->>'progressmsec' as psec 
    FROM v_xml_cdr WHERE answer_stamp > NOW() - INTERVAL '5 minutes' AND direction = 'outbound') AS cdr WHERE cdr.msec::float > 0 AND cdr.psec::float > 0""")
  rows = cur.fetchall()
  result['pddavg'] = rows[0][0]
  result['pddmax'] = rows[0][1]
  conn.close()
  return result

def getStat(scope):
  con = ESL.ESLconnection('127.0.0.1', '8021', 'ClueCon')
  if con.connected:
    if scope is 'calls':
      callsesl = con.sendRecv('api show calls count')
      return int(re.search('([0-9]+)', callsesl.getBody()).group(0))
    if scope is 'channels':
      chanesl = con.sendRecv('api show channels count')
      return int(re.search('([0-9]+)', chanesl.getBody()).group(0))
    if scope is 'registrations':
      regesl = con.sendRecv('api sofia status profile internal')
      return int(re.search('REGISTRATIONS\s+([0-9]+)', regesl.getBody()).group(1))
    #if scope is 'registrations':
    #  regesl = con.sendRecv('api sofia status profile internal')
    #  return int(re.search('REGISTRATIONS\s+([0-9]+)', regesl.getBody()).group(1))
    #if scope is 'registrations':
    #  regesl = con.sendRecv('api sofia status profile internal')
    #  return int(re.search('REGISTRATIONS\s+([0-9]+)', regesl.getBody()).group(1))

    con.disconnect()


class Freeswitch (object):
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig

    def run(self):
	data = {}
        data['calls'] = getStat('calls')
	data['channels'] = getStat('channels')
	data['registrations'] = getStat('registrations')
	cdr = getCdr()
	data['mos_min'] = cdr['mosmin']
	data['mos_max'] = cdr['mosmax']
	data['mos_avg'] = cdr['mosavg']
	data['pdd_avg'] = cdr['pddavg']
	data['pdd_max'] = cdr['pddmax']
        return data
