from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
<<<<<<< HEAD
from django.core.exceptions import ValidationError

=======
import copy
>>>>>>> central/integracion-votaciones

from base import mods
from base.models import Auth, Key

<<<<<<< HEAD
class Question(models.Model):
    desc = models.TextField()
    optionSiNo = models.BooleanField(default=False, help_text="Marca esta casilla si quieres limitar las opciones a 'Sí' o 'No'. No podrás añadir más opciones si esta casilla está marcada.")
    third_option = models.BooleanField(default=False, help_text="Marca esta casilla para añadir una tercera opción con el valor 'Depende'")

    def __str__(self):
        return self.desc    

    def clean(self):
        if self.pk is not None: 
            max_options = float('inf')  
            if self.optionSiNo and not self.third_option:
                max_options = 2  
            elif self.optionSiNo and self.third_option:
                max_options = 3  
            if self.options.count() > max_options:
                raise ValidationError('Tienes demasiadas opciones para la configuración actual.')

            old = Question.objects.get(pk=self.pk)
            if self.optionSiNo and not old.optionSiNo and old.third_option:
                raise ValidationError('No puede seleccionar la opciónSiNo si previamente se seleccionó la tercera opción.')

        super().clean()


    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

@receiver(post_save, sender=Question)
def post_SiNo_Option(sender, instance,created, **kwargs):
    if created:
        options = instance.options.all() 
        if options.count() == 0:
            if instance.optionSiNo:
                op1 = QuestionOption(question=instance, number=1, option="Sí")
                op1.save()
                op2 = QuestionOption(question=instance, number=2, option="No")
                op2.save()
            if instance.third_option:
                op3 = QuestionOption(question=instance, number=3, option="Depende")
                op3.save()

@receiver(post_save, sender=Question)
def update_SiNo_Option(sender, instance, created, **kwargs):
    if not created:  
        if instance.third_option:
            options = instance.options.all()
            if not any(option.option == "Depende" for option in options):
                op3 = QuestionOption(question=instance, number=3, option="Depende")
                op3.save()

                
class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self, *args, **kwargs):
        max_options = float('inf')
        if self.question.optionSiNo and self.question.third_option:
            max_options = 3  
        elif self.question.optionSiNo:
            max_options = 2 
        elif self.question.third_option:
            max_options = 3  

        if self.question.options.count() >= max_options and not (self.question.third_option and self.number == 3):
            raise ValidationError({
                'options': [
                    f'No puedes añadir más opciones, ni editar los valores ya predefinidos. El número máximo de opciones permitidas es {max_options}.'
                ]
            }) 

        if self.question.optionSiNo and self.option not in ["Sí", "No"] and self.number in [1, 2]:
            raise ValidationError("Debes rellenar el campo 1 Option con 'Sí' o 'No'.")

        super().save(*args, **kwargs)        

    def delete(self, *args, **kwargs):
        if self.question.optionSiNo and self.option in ["Sí", "No"]:
            raise ValidationError("No puedes eliminar las opciones predefinidas.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)
    
        
VOTING_TYPES = [
    ('S', 'Single Choice'),
    ('M', 'Multiple Choice'),
    ('H', 'Hierarchy'),
    ('Q', 'Many Questions'),
]

class Voting(models.Model):
    voting_type = models.CharField(max_length=1, choices=VOTING_TYPES, default='S')
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)

    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)
=======

class Question(models.Model):
    desc = models.TextField()

    def __str__(self):
        return self.desc


class QuestionOption(models.Model):
    question = models.ForeignKey(
        Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(
        Question, related_name='voting', on_delete=models.CASCADE)
>>>>>>> central/integracion-votaciones

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

<<<<<<< HEAD
    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
=======
    pub_key = models.OneToOneField(
        Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
>>>>>>> central/integracion-votaciones
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

<<<<<<< HEAD
=======
    seats = models.PositiveIntegerField(blank=True, null=True, default=10)

>>>>>>> central/integracion-votaciones
    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
<<<<<<< HEAD
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
=======
            "auths": [{"name": a.name, "url": a.url} for a in self.auths.all()],
>>>>>>> central/integracion-votaciones
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
<<<<<<< HEAD
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
=======
        votes = mods.get('store', params={
                         'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
>>>>>>> central/integracion-votaciones
        # anon votes
        votes_format = []
        vote_list = []
        for vote in votes:
            for info in vote:
                if info == 'a':
                    votes_format.append(vote[info])
                if info == 'b':
                    votes_format.append(vote[info])
            vote_list.append(votes_format)
            votes_format = []
        return vote_list

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
<<<<<<< HEAD
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
=======
        data = {"msgs": votes}
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                             response=True)
>>>>>>> central/integracion-votaciones
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
<<<<<<< HEAD
                response=True)
=======
                             response=True)
>>>>>>> central/integracion-votaciones

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()

        opts = []
        for opt in options:
            if isinstance(tally, list):
                votes = tally.count(opt.number)
            else:
                votes = 0
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': votes
            })

<<<<<<< HEAD
        data = { 'type': 'IDENTITY', 'options': opts }
=======
        total_seats = self.seats

        self.do_dhont(opts, total_seats)
        self.do_saintLague(opts, total_seats)
        data = {'type': 'IDENTITY', 'options': opts}
>>>>>>> central/integracion-votaciones
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

<<<<<<< HEAD
=======
    def do_dhont(self, opts, total_seats):
        for option in opts:
            votes = option["votes"]
            dhont_values = []
            for seat in range(1, total_seats + 1):
                dhont = round(votes / seat, 4)
                dhont_values.append({
                    "seat": seat,
                    "percentaje": dhont
                })

            option["dhont"] = dhont_values
            
    def do_saintLague(self, opts, total_seats):
        opts_aux = copy.deepcopy(opts)
        
        for option in opts:
            option["saintLague"] = 0
        
        for i in range (1, total_seats + 1):
            quotients = {option["option"]: option["votes"] / (2 * i - 1) for option in opts_aux}
            best_option = max(quotients, key=quotients.get)
            for option in opts_aux:
                if option['option'] == best_option:
                    option['votes'] /= (2 * i + 1)
                    break
            for option in opts:
                if option['option'] == best_option:
                    option['saintLague'] += 1
                    break

    def do_borda(self, opts):
        n = len(opts)
        for option in opts:
            votes = option["votes"]
            borda = 0
            for i in range(n):
                borda += (n - i) * votes[i]
            option["borda"] = borda


>>>>>>> central/integracion-votaciones
    def __str__(self):
        return self.name
    
    
