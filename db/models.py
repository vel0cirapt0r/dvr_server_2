from tortoise import fields
from tortoise.models import Model

class Device(Model):
    id = fields.IntField(pk=True)
    serial_number = fields.CharField(max_length=255, unique=True)
    area = fields.CharField(max_length=255, null=True)
    auth_code = fields.CharField(max_length=255, null=True)
    enable = fields.CharField(max_length=10, null=True)
    stream_level = fields.TextField(null=True)
    stream_server_ips = fields.JSONField(null=True)
    user_info = fields.JSONField(null=True)
    live_status = fields.JSONField(null=True)
    rewrite_oem_id = fields.CharField(max_length=255, null=True)
    last_seen = fields.DatetimeField(null=True)
    disconnected_at = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)
    json_raw = fields.JSONField()

    class Meta:
        table = "devices"

class DeviceLog(Model):
    id = fields.IntField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="logs")
    event_type = fields.CharField(max_length=32)  # e.g., 'register', 'disconnect', 'heartbeat', etc.
    details = fields.TextField(null=True)  # Optional human-readable summary
    json_raw = fields.JSONField(null=True)  # Full raw payload (structured & searchable)
    ip_address = fields.CharField(max_length=45, null=True)  # IPv6-compatible
    extra_info = fields.JSONField(null=True)  # Flexible optional metadata (e.g., error messages, parsed stats)
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "device_logs"
