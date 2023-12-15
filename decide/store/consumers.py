from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from census.models import Census
from store.models import Vote
from voting.models import Voting
from voting.admin import stop

class VoteConsumer(AsyncWebsocketConsumer):

    async def receive(self, text_data):
        content = json.loads(text_data)
        if content['type'] == 'voting.closed':
            await self.voting_closed(content)

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

    async def voting_closed(self, event):
        voting_id = event['voting_id']

        # Cierra la votación obteniendo un queryset en vez de una votacion
        voting = await sync_to_async(Voting.objects.filter)(id=voting_id)
        await sync_to_async(stop)(None, None, voting)
        first_voting = await sync_to_async(voting.first)()
        start = (first_voting.start_date)
        end = (first_voting.end_date)

        await self.send(text_data=json.dumps({
            'message': 'Voting closed',
            'voting_id': voting_id,  # Envía el ID de la votación al cliente
            'end_date': end.strftime("%Y-%m-%d %H:%M:%S"),  # Envía la fecha de finalización al cliente

        }))