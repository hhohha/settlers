import unittest
from enums import Resource
from util import Cost

class TestStack(unittest.TestCase):
    def test_init(self):
        cost = Cost()
        self.assertEqual(cost.grain, 0)
        self.assertEqual(cost.sheep, 0)
        self.assertEqual(cost.rock, 0)
        self.assertEqual(cost.brick, 0)
        self.assertEqual(cost.wood, 0)
        self.assertEqual(cost.gold, 0)

        cost = Cost(brick=1, rock=2)
        self.assertEqual(cost.grain, 0)
        self.assertEqual(cost.sheep, 0)
        self.assertEqual(cost.rock, 2)
        self.assertEqual(cost.brick, 1)
        self.assertEqual(cost.wood, 0)
        self.assertEqual(cost.gold, 0)

    def test_get_set(self):
        cost = Cost()
        cost.set(Resource.GRAIN, 1)
        cost.set(Resource.SHEEP, 2)
        cost.set(Resource.ROCK, 3)
        cost.set(Resource.BRICK, 1)
        cost.set(Resource.WOOD, 2)
        cost.set(Resource.GOLD, 3)

        self.assertEqual(cost.grain, 1)
        self.assertEqual(cost.get(Resource.GRAIN), 1)
        self.assertEqual(cost.sheep, 2)
        self.assertEqual(cost.get(Resource.SHEEP), 2)
        self.assertEqual(cost.rock, 3)
        self.assertEqual(cost.get(Resource.ROCK), 3)
        self.assertEqual(cost.brick, 1)
        self.assertEqual(cost.get(Resource.BRICK), 1)
        self.assertEqual(cost.wood, 2)
        self.assertEqual(cost.get(Resource.WOOD), 2)
        self.assertEqual(cost.gold, 3)
        self.assertEqual(cost.get(Resource.GOLD), 3)

    def test_take(self):
        cost = Cost(rock=2, grain=3)
        cost.take(Resource.ROCK)
        self.assertEqual(cost, Cost(rock=1, grain=3))

        cost.take(Resource.GRAIN, 3)
        cost.take(Resource.ROCK, 1)
        self.assertEqual(cost, Cost())

        with self.assertRaises(AssertionError):
            cost.take(Resource.ROCK)

    def test_ge_comparison(self):
        self.assertTrue(Cost() >= Cost())
        self.assertTrue(Cost(wood=1) >= Cost())
        self.assertTrue(Cost(wood=1) >= Cost(wood=1))
        self.assertTrue(Cost(wood=2) >= Cost(wood=1))
        self.assertFalse(Cost() >= Cost(wood=1))

        self.assertTrue(Cost(wood=2, gold=1) >= Cost())
        self.assertTrue(Cost(wood=2, gold=1) >= Cost(wood=2))
        self.assertTrue(Cost(wood=2, gold=1) >= Cost(wood=1, gold=1))
        self.assertTrue(Cost(wood=2, gold=1) >= Cost(wood=2, gold=1))

        self.assertFalse(Cost(wood=2, gold=1) >= Cost(rock=1))
        self.assertFalse(Cost(wood=2, gold=1) >= Cost(wood=1, rock=1))
        self.assertFalse(Cost(wood=2, gold=1) >= Cost(wood=3))
        self.assertFalse(Cost(wood=2, gold=1) >= Cost(wood=2, gold=2))

    def test_is_zero(self):
        self.assertTrue(Cost().is_zero())
        self.assertFalse(Cost(brick=1).is_zero())

    def test_total(self):
        self.assertEqual(Cost().total(), 0)
        self.assertEqual(Cost(rock=1).total(), 1)
        self.assertEqual(Cost(rock=3, grain=2, gold=2).total(), 7)
        self.assertEqual(Cost(rock=3, grain=3, gold=3, sheep=3).total(), 12)
