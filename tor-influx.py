import re
import platform
from influxdb import InfluxDBClient
from stem.control import EventType, Controller

INFLUXDB_HOST = "influxdb1"
INFLUXDB_PORT = 8086
INFLUXDB_USER = "user"
INFLUXDB_PASSWORD = "password"
INFLUXDB_DATABASE = "tor"

with Controller.from_socket_file() as controller:
  controller.authenticate()
  
  p = re.compile('(?P<read>\d+)\,(?P<write>\d+)$')
  
  bytes_read = controller.get_info("traffic/read")
  bytes_written = controller.get_info("traffic/written")
  bandwidth = controller.get_info("bw-event-cache")
  m = p.search(bandwidth)
  print("%s read, %s written" % (bytes_read, bytes_written))
  print("%s read, %s written" % (m.group('read'), m.group('write')))
  tags = {
    'hostname': platform.node()
  }
  points = [
    {
      'measurement': 'total_bytes_read',
      'fields': { 
        'value': int(bytes_read)
      }
    },
    {
      'measurement': 'total_bytes_written',
      'fields': {
        'value': int(bytes_written)
      }
    },
    {
      'measurement': 'bytes_read_1s',
      'fields': {
        'value': int(m.group('read'))
      }
    },
    {
      'measurement': 'bytes_written_1s',
      'fields': {
        'value': int(m.group('write'))
      }
    }
    ]


  client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PASSWORD, INFLUXDB_DATABASE)
  client.write_points(points, tags=tags)
