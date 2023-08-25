from rest_framework import serializers

from models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('image_path', 'file_path', 'type', 'src_id', 'dst_id', 'chat_id', 'timestamp')