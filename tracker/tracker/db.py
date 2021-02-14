from influxdb import InfluxDBClient

from . import config

client = InfluxDBClient(
    host=config.INFLUXDB_HOST,
    port=config.INFLUXDB_PORT,
    username=config.INFLUXDB_USERNAME,
    password=config.INFLUXDB_PASSWORD,
    database=config.INFLUXDB_DATABASE
)
