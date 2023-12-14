from django.utils import timezone
from rest_framework.test import APIClient
from base.tests import BaseTestCase
from django.core.exceptions import ValidationError

from base import mods
from django.contrib.auth.models import User
from voting.models import Question, QuestionOption, Voting
from .models import PostProcessing
from census.models import Census
from mixnet.mixcrypt import ElGamal, MixCrypt
from mixnet.models import Auth
from django.conf import settings


class PostProcTestCase(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        super().setUp()

    def tearDown(self):
        self.client = None
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self, postproc, type):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 2
            )
            opt.save()
        v = Voting(
            name="test voting", question=q, postproc_type=postproc, voting_type=type
        )
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username="testvoter{}".format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(5):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    "voting": v.id,
                    "voter": voter.voter_id,
                    "vote": {"a": a, "b": b},
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post("store", json=data)
        return clear

    def test_correct_postproc(self):
        v = self.create_voting("DHO", "S")
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        postproc = PostProcessing.objects.get(voting=v)
        postproc.do(v.postproc, v.seats)

        dhont = postproc.results

        expected = [
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
            {
                "dhont": [
                    {"seat": 1, "percentaje": 5.0},
                    {"seat": 2, "percentaje": 2.5},
                    {"seat": 3, "percentaje": 1.6667},
                    {"seat": 4, "percentaje": 1.25},
                    {"seat": 5, "percentaje": 1.0},
                    {"seat": 6, "percentaje": 0.8333},
                    {"seat": 7, "percentaje": 0.7143},
                    {"seat": 8, "percentaje": 0.625},
                    {"seat": 9, "percentaje": 0.5556},
                    {"seat": 10, "percentaje": 0.5},
                ]
            },
        ]

        for i in range(len(dhont)):
            for j in range(len(dhont[i]["dhont"])):
                self.assertEquals(
                    dhont[i]["dhont"][j],
                    expected[i]["dhont"][j],
                    "Métricas no coinciden",
                )

    def test_invalid_config_voting(self):
        try:
            self.create_voting("DHO", "M")
        except ValidationError as e:
            self.assertEqual(
                e.message,
                "Las técnicas de postprocesado no se pueden aplicar a votaciones no Simples",
            )
        else:
            self.fail("Se esperaba una excepción ValidationError, pero no se lanzó")

    def test_droop_wikipedia_example(self):
        # validating the functionality of the function using the wikipedia example
        test = [
            {"option": "Partido A", "number": 1, "votes": 391000},
            {"option": "Partido B", "number": 2, "votes": 311000},
            {"option": "Partido C", "number": 3, "votes": 184000},
            {"option": "Partido D", "number": 4, "votes": 73000},
            {"option": "Partido E", "number": 5, "votes": 27000},
            {"option": "Partido F", "number": 6, "votes": 12000},
            {"option": "Partido G", "number": 7, "votes": 2000},
        ]
        expected_result = [
            {"option": "Partido A", "number": 1, "votes": 391000, "droop": 8},
            {"option": "Partido B", "number": 2, "votes": 311000, "droop": 7},
            {"option": "Partido C", "number": 3, "votes": 184000, "droop": 4},
            {"option": "Partido D", "number": 4, "votes": 73000, "droop": 2},
            {"option": "Partido E", "number": 5, "votes": 27000, "droop": 0},
            {"option": "Partido F", "number": 6, "votes": 12000, "droop": 0},
            {"option": "Partido G", "number": 7, "votes": 2000, "droop": 0},
        ]
        seats = 21
        droop = PostProcessing.droop(None, opts=test, total_seats=seats)
        self.assertEquals(droop, expected_result)

    def test_correct_droop_postproc(self):
        v = self.create_voting("DRO", "S")
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()
        v.tally_votes(self.token)
        postproc = PostProcessing.objects.get(voting=v)

        droop = postproc.results

        expected_result = [
            {"option": "option 1", "number": 2, "votes": 5, "droop": 2},
            {"option": "option 2", "number": 3, "votes": 5, "droop": 2},
            {"option": "option 3", "number": 4, "votes": 5, "droop": 2},
            {"option": "option 4", "number": 5, "votes": 5, "droop": 2},
            {"option": "option 5", "number": 6, "votes": 5, "droop": 2},
        ]

        self.assertEqual(droop, expected_result)

    def test_invalid_droop_postproc(self):
        invalid_voting_types = ["M", "H", "Q"]
        for voting_type in invalid_voting_types:
            try:
                self.create_voting("DRO", voting_type)
            except ValidationError as e:
                self.assertEqual(
                    e.message,
                    "Las técnicas de postprocesado no se pueden aplicar a votaciones no Simples",
                )
            else:
                self.fail("Se esperaba una excepción ValidationError, pero no se lanzó")


class PostProcTestsSaintLague(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        super().setUp()

    def tearDown(self):
        self.client = None
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self, postproc, type):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 2
            )
            opt.save()
        v = Voting(
            name="test voting", question=q, postproc_type=postproc, voting_type=type
        )
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username="testvoter{}".format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for _ in range(5):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    "voting": v.id,
                    "voter": voter.voter_id,
                    "vote": {"a": a, "b": b},
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post("store", json=data)
        return clear

    def test_saint_function(self):
        opts = [
            {"option": "A", "votes": 100},
            {"option": "B", "votes": 80},
        ]
        total_seats = 5

        instance = PostProcessing()
        instance.saint(opts, total_seats)

        self.assertEqual(len(opts), len(instance.results))

        total_seats_assigned = sum(option["saintLague"] for option in instance.results)
        self.assertEqual(total_seats, total_seats_assigned)

        for option in instance.results:
            expected_seats = round(
                (option["votes"] / sum(o["votes"] for o in opts)) * total_seats
            )
            self.assertEqual(option["saintLague"], expected_seats)

    def test_correct_postproc_saint_lague(self):
        v = self.create_voting("PAR", "S")
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.store_votes(v)

        self.login()
        v.tally_votes(self.token)

        postproc = PostProcessing.objects.get(voting=v)

        saint_lague = postproc.results
        results_expected = [
            {"option": "option 1", "number": 2, "votes": 5, "saintLague": 2},
            {"option": "option 2", "number": 3, "votes": 5, "saintLague": 2},
            {"option": "option 3", "number": 4, "votes": 5, "saintLague": 2},
            {"option": "option 4", "number": 5, "votes": 5, "saintLague": 2},
            {"option": "option 5", "number": 6, "votes": 5, "saintLague": 2},
        ]

        self.assertEqual(saint_lague, results_expected)

    def test_invalid_config_voting(self):
        try:
            self.create_voting("PAR", "M")
        except ValidationError as e:
            self.assertEqual(
                e.message,
                "Las técnicas de postprocesado no se pueden aplicar a votaciones no Simples",
            )
        else:
            self.fail("Se esperaba una excepción ValidationError, pero no se lanzó")
