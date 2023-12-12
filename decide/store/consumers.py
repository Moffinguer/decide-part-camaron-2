from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from voting.models import Voting
from census.models import Census
from store.models import Vote

class VoteConsumer(AsyncWebsocketConsumer):
    events = {
        'vote.added': 'vote_added',
    }

    async def receive_json(self, content):
        # Este método se llama cuando se recibe un mensaje del WebSocket.

        # Obtiene el tipo de evento del mensaje.
        event_type = content.get('type')

        # Si el evento está en el diccionario de eventos, llama a la función correspondiente.
        if event_type in self.events:
            event_handler = getattr(self, self.events[event_type])
            await event_handler(content)

    async def connect(self):
        # Cuando el WebSocket se conecta, añádelo al grupo 'votes'.
        await self.channel_layer.group_add('votes', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def vote_added(self, event):
        vote_id = event['vote_id']

        # Cuenta los votos para esta votación
        vote_count = await sync_to_async(Vote.objects.filter(voting_id=vote_id).count)()

        # Cuenta el número total de votantes elegibles
        total_voters = await sync_to_async(Census.objects.filter(voting_id=vote_id).count)()

        # Calcula el porcentaje de votos
        vote_percentage = (vote_count / total_voters) * 100 if total_voters else 0

        await self.send(text_data=json.dumps({
            'message': 'Vote received',
            'vote_id': vote_id,  # Envía el ID de la votación al cliente
            'vote_count': vote_count,  # Envía el recuento de votos al cliente
            'vote_percentage': vote_percentage,  # Envía el porcentaje de votos al cliente
        }))