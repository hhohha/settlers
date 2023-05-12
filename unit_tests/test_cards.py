import unittest
from unittest.mock import MagicMock

from card import Fleet, Buildable, Card, Playable, Knight, Building, Action, Event, Town, Settlement, Village, Path, \
    Landscape, SettlementSlot, MetaCard
from enums import Resource
from util import Cost, Pos


class TestStack(unittest.TestCase):
    def test_init(self):
        f = Fleet('my_fleet', Cost(), Resource.WOOD, 2)
        self.assertEqual(f.name, 'my_fleet')
        self.assertEqual(f.cost, Cost())
        self.assertEqual(f.affectedResource, Resource.WOOD)
        self.assertEqual(f.tradePoints, 2)
        self.assertIsNone(f.settlement)
        self.assertIsNone(f.pos)
        self.assertIsNone(f.player)
        self.assertTrue(isinstance(f, Fleet))
        self.assertTrue(isinstance(f, Buildable))
        self.assertTrue(isinstance(f, Playable))
        self.assertTrue(isinstance(f, Card))

        k = Knight('my_knight', Cost(wood=1), 3, 2)
        self.assertEqual(k.name, 'my_knight')
        self.assertEqual(k.cost, Cost(wood=1))
        self.assertEqual(k.tournamentStrength, 3)
        self.assertEqual(k.battleStrength, 2)
        self.assertIsNone(k.settlement)
        self.assertIsNone(k.pos)
        self.assertIsNone(k.player)
        self.assertTrue(isinstance(k, Knight))
        self.assertTrue(isinstance(k, Buildable))
        self.assertTrue(isinstance(k, Playable))
        self.assertTrue(isinstance(k, Card))

        b = Building('my_building', Cost(wood=2), True, 1, 0)
        self.assertEqual(b.name, 'my_building')
        self.assertEqual(b.cost, Cost(wood=2))
        self.assertEqual(b.townOnly, True)
        self.assertEqual(b.victoryPoints, 1)
        self.assertEqual(b.tradePoints, 0)
        self.assertIsNone(b.settlement)
        self.assertIsNone(b.pos)
        self.assertIsNone(b.player)
        self.assertTrue(isinstance(b, Building))
        self.assertTrue(isinstance(b, Buildable))
        self.assertTrue(isinstance(b, Playable))
        self.assertTrue(isinstance(b, Card))

        a = Action('my_action')
        self.assertEqual(a.name, 'my_action')
        self.assertIsNone(a.player)
        self.assertTrue(isinstance(a, Action))
        self.assertTrue(isinstance(a, Playable))
        self.assertTrue(isinstance(a, Card))

        e = Event('my_event')
        self.assertEqual(e.name, 'my_event')
        self.assertTrue(isinstance(e, Event))
        self.assertTrue(isinstance(e, Card))

        playerMock = MagicMock()

        t = Town(Pos(1, 1), playerMock)
        self.assertEqual(t.name, 'town')
        self.assertEqual(t.pos, Pos(1, 1))
        self.assertEqual(t.player, playerMock)
        self.assertEqual(t.cards, [])
        self.assertTrue(isinstance(t, Town))
        self.assertTrue(isinstance(t, Settlement))
        self.assertTrue(isinstance(t, Card))

        v = Village(Pos(2, 2), playerMock)
        self.assertEqual(v.name, 'village')
        self.assertEqual(v.pos, Pos(2, 2))
        self.assertEqual(v.player, playerMock)
        self.assertEqual(v.cards, [])
        self.assertTrue(isinstance(v, Village))
        self.assertTrue(isinstance(v, Settlement))
        self.assertTrue(isinstance(v, Card))

        p = Path(Pos(3, 3), playerMock)
        self.assertEqual(p.name, 'path')
        self.assertEqual(p.player, playerMock)
        self.assertEqual(p.pos, Pos(3, 3))
        self.assertTrue(isinstance(p, Path))
        self.assertTrue(isinstance(p, Card))

        l = Landscape('my_land', Resource.GOLD, 4)
        self.assertEqual(l.name, 'my_land')
        self.assertEqual(l.resource, Resource.GOLD)
        self.assertEqual(l.diceNumber, 4)
        self.assertEqual(l.resourcesHeld, 0)
        self.assertIsNone(l.pos)
        self.assertIsNone(l.player)
        self.assertEqual(l.settlements, [])
        self.assertTrue(isinstance(l, Landscape))
        self.assertTrue(isinstance(l, Card))

        s = SettlementSlot(Pos(4, 4), playerMock)
        self.assertEqual(s.name, 'highlighted')
        self.assertEqual(s.pos, Pos(4, 4))
        self.assertEqual(s.player, playerMock)
        self.assertIsNone(s.settlement)
        self.assertTrue(isinstance(s, SettlementSlot))
        self.assertTrue(isinstance(s, Card))

        m = MetaCard('my_meta')
        self.assertEqual(m.name, 'my_meta')
        self.assertTrue(isinstance(m, MetaCard))
        self.assertTrue(isinstance(m, Card))

