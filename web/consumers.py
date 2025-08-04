# myapp/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import AnimalRecord
from datetime import datetime

class AnimalRecordConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # 发送初始的30条记录
        await self.channel_layer.group_add(
            "animal_records",
            self.channel_name
        )

        await self.send_initial_records()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "animal_records",
            self.channel_name
        )

    async def send_initial_records(self):
        records = await self.get_30_records()
        await self.send(text_data=json.dumps({
            'type': 'initial_records',
            'data': records
        }))

    async def get_30_records(self):
        # 注意：这里使用 sync_to_async 包装同步ORM操作
        from channels.db import database_sync_to_async

        @database_sync_to_async
        def _get_records():
            latest_records = AnimalRecord.objects.order_by('-Time')[:30]
            return {
                "time": [record.Time.isoformat() for record in latest_records],
                "record": [record.Record for record in latest_records]
            }

        return await _get_records()


    async def new_record(self, event):
        """处理新记录通知"""
        message = event['message']
        if message == "new":

            records = await self.get_30_records()
            await self.send(text_data=json.dumps({
                'type': 'new_records',
                'data': records
            }))