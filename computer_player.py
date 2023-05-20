from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Optional, Type
from card import Town, Path, Village, Playable, Action, Landscape, Buildable, Building, Knight, Fleet
from config import MAX_LAND_RESOURCES, RESOURCE_LIST
from custom_types import Pile
from enums import Resource
from player import Player
from time import sleep

if TYPE_CHECKING:
    from game import Game
    from util import Pos, Cost
    from board import Board

class ComputerPlayer(Player):
    def __init__(self, game: Game, handBoard: Board, number: int, midPos: Pos):
        super().__init__(game, handBoard, number, False, midPos)

        self.hasEmptyPath = False

    def __str__(self) -> str:
        return 'computer'

    __repr__ = __str__


    def initial_land_setup(self) -> None:
        # TODO - move gold to the middle
        pass

    def select_pile(self, unavailablePile: Optional[Pile]=None) -> Pile:
        # TODO
        # always selects the pile with most cards, that is suitable for first select but needs to improve
        # for subsequent selections - at least pick those that haven't been picked (longest), or those we know/think
        # have card(s) we want
        resIdx, maxLen = 0, 0
        for idx, pile in enumerate(self.game.cardPiles):
            if len(pile) > maxLen and pile is not unavailablePile:
                maxLen, resIdx = len(pile), idx
        print('')
        return self.game.cardPiles[resIdx]

    def pick_starting_cards(self) -> None:
        # TODO - setup card priority
        pile = self.select_pile()
        while len(self.cardsInHand) < self.cardsInHandDefaultCnt:
            self.cardsInHand.append(pile.pop())
        self.refresh_hand_board()

    def throw_dice(self) -> None:
        print('opponent throwing dice')
        event = self.game.throw_event_dice()
        print(f'event: {event}')
        self.game.handle_dice_events(event)
        diceNumber = self.game.throw_yield_dice()
        print(f'yield: {diceNumber}')
        self.game.land_yield(diceNumber)

    def pay(self, cost: Cost | int) -> None:
        pass

    def wait_for_ok(self) -> None:
        sleep(1)

    def grab_any_resource_if_possible(self) -> None:
        if not self.can_grab_resource_from_opponent():
            return

        # TODO - improve, currently it gets anything available
        assert self.opponent is not None
        for opponentLand in self.opponent.landscapeCards:
            if opponentLand.resourcesHeld > 0:
                for myLand in self.landscapeCards:
                    if myLand.resource == opponentLand.resource and myLand.resourcesHeld < MAX_LAND_RESOURCES:
                        opponentLand.resourcesHeld -= 1
                        myLand.resourcesHeld += 1
                        assert myLand.pos is not None and opponentLand.pos is not None
                        self.game.mainBoard.refresh_square(myLand.pos)
                        self.game.mainBoard.refresh_square(opponentLand.pos)
                        return

    def give_any_resource(self) -> None:
        # TODO - improve, currently it gives anything available
        assert self.opponent is not None
        for opponentLand in self.opponent.landscapeCards:
            if opponentLand.resourcesHeld < MAX_LAND_RESOURCES:
                for myLand in self.landscapeCards:
                    if myLand.resource == opponentLand.resource and myLand.resourcesHeld > 0:
                        opponentLand.resourcesHeld += 1
                        myLand.resourcesHeld -= 1
                        assert myLand.pos is not None and opponentLand.pos is not None
                        self.game.mainBoard.refresh_square(myLand.pos)
                        self.game.mainBoard.refresh_square(opponentLand.pos)
                        return

    def pick_any_resource(self) -> None:
        # TODO - improve
        for land in self.landscapeCards:
            if land.resourcesHeld < MAX_LAND_RESOURCES:
                land.resourcesHeld += 1
                assert land.pos is not None
                self.game.mainBoard.refresh_square(land.pos)
                return

    def decide_browse_pile(self) -> bool:
        return False

    def select_new_card_position(self, infraType: Type[Village | Path | Town | Playable], townOnly=False) -> Optional[Pos]:
        if infraType == Village:
            return self._find_place_for_village()
        if infraType == Town:
            return self._find_place_for_town()
        if infraType == Path:
            return self._find_place_for_path()

    def select_card_to_pay(self, resource: Optional[Cost]=None) -> Landscape:
        pass

    def decide_swap_one_card(self) -> bool:
        return False

    def select_card_to_throw_away(self) -> Playable:
        return self.cardsInHand[0]

    def select_card_from_choice(self, pile: Pile) -> Playable:
        pass

    def select_opponents_unit_to_remove(self) -> Buildable:
        for knight in self.opponent.knightsPlayed:
            if not self.game.is_protected_from_civil_war(knight):
                return knight

        for fleet in self.opponent.fleetPlayed:
            if not self.game.is_protected_from_civil_war(fleet):
                return fleet

        assert False, 'opponent has no knight or fleet to remove'

    def decide_use_defence(self, againstCard: str) -> bool:
        return True

    def select_building_to_burn(self) -> Building:
        assert self.opponent.buildingsPlayed, f"cannot burn anything"
        return self.opponent.buildingsPlayed[0]

    def select_knight_to_kill(self) -> Knight:
        assert self.opponent.knightsPlayed, f"cannot kill anyone"
        return self.opponent.knightsPlayed[0]

    def select_opponents_card_to_discard(self) -> Playable:
        card = self.game.choiceBoard.get_square(Pos(0, 0))
        assert isinstance(card, Playable), f'choice board has invalid content'
        return card

    def trade_with_caravan(self) -> None:
        pass

    def select_resource_to_trade_for(self) -> Optional[Resource]:
        pass

    def select_resource_to_purchase(self) -> Landscape:
        pass

    def select_card_to_steal_by_spy(self) -> Knight | Fleet | Action:
        pass

    def decide_use_scout(self) -> bool:
        return True

    def select_new_land(self) -> Landscape:
        pass

    def do_actions(self) -> None:
        while True:
            if self.can_cover_cost(Town.cost) and self._find_place_for_town() is not None:
                self.build_infrastructure(Town)
                continue

            if not self.hasEmptyPath and self.can_cover_cost(Path.cost) and self._find_place_for_path() is not None:
                self.build_infrastructure(Path)
                self.hasEmptyPath = True
                continue

            if self.hasEmptyPath and self.can_cover_cost(Village.cost) and self._find_place_for_village() is not None:
                self.build_infrastructure(Village)
                self.hasEmptyPath = False
                continue

            cardToBuild = self._find_something_to_build()
            if cardToBuild is not None:
                pos = self._find_pos_for_building(cardToBuild)
                if pos is not None:
                    self.play_card_from_hand(cardToBuild, pos)
                    continue

            actionCardToPlay = self._find_action_card_to_play()
            if actionCardToPlay is not None:
                self.play_card_from_hand(actionCardToPlay)
                continue

            if self._can_cover_cost_with_trade(Town.cost) and self._find_place_for_town() is not None:
                self.trade_to_cover_cost(Town.cost)
                self.build_infrastructure(Town)
                continue

            if not self.hasEmptyPath and self._can_cover_cost_with_trade(Path.cost) and self._find_place_for_path() is not None:
                self.trade_to_cover_cost(Path.cost)
                self.build_infrastructure(Path)
                self.hasEmptyPath = True
                continue

            if self.hasEmptyPath and self._can_cover_cost_with_trade(Village.cost) and self._find_place_for_village() is not None:
                self.trade_to_cover_cost(Village.cost)
                self.build_infrastructure(Village)
                self.hasEmptyPath = False
                continue

            cardToBuild = self._find_something_to_build_with_trade()
            if cardToBuild is not None:
                pos = self._find_pos_for_building(cardToBuild)
                if pos is not None:
                    self.trade_to_cover_cost(cardToBuild)
                    self.play_card_from_hand(cardToBuild, pos)
                    continue

            return

    ####################################################################################################################
    #################   PRIVATE FUNCTIONS   ############################################################################
    ####################################################################################################################

    def _can_trade_resources_with_opponent(self, cost: Cost) -> Cost:
        opponentResources = self.opponent.get_resources_available()
        resCost = Cost()
        for resource in RESOURCE_LIST:
            resCost.set(resource, min(cost.get(resource), opponentResources.get(resource) > 0))
        return resCost

    def _choose_what_to_pay_trader(self) -> Resource:
        pass

    def _choose_what_to_pay_caravan(self) -> Resource:
        pass

    def _can_cover_cost_with_trade(self, cost: Cost) -> bool:
        if self.can_cover_cost(cost):
            return True

        # step 1 - what can cover by myself
        resourcesAvail: Cost = self.get_resources_available()
        missing: int = 0
        for resource in RESOURCE_LIST:
            diff = resourcesAvail.get(resource) - cost.get(resource)
            if diff >= 0:
                resourcesAvail.take(resource, diff)
                cost.take(resource, diff)
            else:
                resourcesAvail.set(resource, 0)
                missing -= diff
                cost.take(resource, -diff)

        # step 2 - what can I cover with trader
        if self.card_in_hand('trader') and resourcesAvail.total() > 0:
            tradable = self._can_trade_resources_with_opponent(deepcopy(cost))
            if tradable.total() > 0:
                cost.take_any(max(tradable.total(), 2, cost.total()))
                resourcesAvail.take(self._choose_what_to_pay_trader())

        if cost.is_zero():
            return True

        wildcardResources = 0
        # step 3 - what can I cover with mint
        if 'mint' in map(lambda x: x.name, self.buildingsPlayed):
            wildcardResources += resourcesAvail.get(Resource.GOLD)
            resourcesAvail.set(Resource.GOLD, 0)

        # step 4 - what can I cover with caravan
        if self.card_in_hand('caravan') and resourcesAvail.total() > 0:
            cost.take_any(max(2, cost.total()))
            resourcesAvail.take(self._choose_what_to_pay_caravan())

        if cost.is_zero():
            return True

        # step 5 - what can I cover with fleets
        for fleet in self.fleetPlayed:
            r = resourcesAvail.get(fleet.affectedResource)
            if r >= 2 and cost.get(fleet.affectedResource) > 0:
                costToTake = max(r // 2, cost.get(fleet.affectedResource))
                cost.take(fleet.affectedResource, costToTake)
                resourcesAvail.take(fleet.affectedResource, costToTake * 2)

        if cost.is_zero():
            return True

        # step 6 - what can I cover with basic trade 3:1



    def _find_something_to_build(self) -> Optional[Buildable]:
        for card in self.cardsInHand:
            if isinstance(card, Buildable) and self.can_cover_cost(card.cost):
                return card
        return None

    def _find_action_card_to_play(self) -> Optional[Action]:
        for card in self.cardsInHand:
            if isinstance(card, Action):
                if card.name == 'arson' and self.opponent.buildingsPlayed:
                    return card
                elif card.name == 'ambush' and self._can_grab_resources(2):
                    return card
                elif card.name == 'black_knight' and self.opponent.knightsPlayed:
                    return card
                elif card.name == 'spy':
                    return card
        return None

    def _can_grab_resources(self, n: int) -> bool:
        pass

    def _find_place_for_village(self) -> Optional[Pos]:
        for path in self.paths:
            if path.pos.x in [0, self.game.mainBoard.size.x - 1]:
                continue
            for pos in [path.pos.left(), path.pos.right()]:
                card = self.game.mainBoard.get_square(pos)
                if card is not None and card.name == 'empty':
                    return pos
        return None

    def _find_place_for_town(self) -> Optional[Pos]:
        for settlement in self.settlements:
            if isinstance(settlement, Village):
                return settlement.pos
        return None

    def _find_place_for_path(self) -> Optional[Pos]:
        for settlement in self.settlements:
            if settlement.pos.x in [0, self.game.mainBoard.size.x - 1]:
                continue
            for pos in [settlement.pos.left(), settlement.pos.right()]:
                card = self.game.mainBoard.get_square(pos)
                if card is not None and card.name == 'empty':
                    return pos
        return None

