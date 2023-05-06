import random
from typing import List, Optional, Tuple, Set, Iterator
from board import Board
from click_filter import ClickFilter
from computer_player import ComputerPlayer
from display_handler import DisplayHandler
from enums import DiceEvent, EventCardType, Resource
from card_data import CardData
from human_player import HumanPlayer
import config
from player import Player
from util import DiceEvents, Pos, MouseClick, MILLS_EFFECTS, Cost
from card import Card, Event, Landscape, Village, Town, Path, MetaCard, Playable, Building, Buildable, SettlementSlot, \
    Knight, Fleet, Settlement

Pile = List[Playable]

class Game:
    def __init__(self):
        # prepare all boards
        self.mainBoard: Board = Board(Pos(*config.MAIN_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.player1Board = Board(Pos(*config.PLAYER_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.player2Board = Board(Pos(*config.PLAYER_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.choiceBoard = Board(Pos(*config.CHOICE_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.bigCard = Board(Pos(1, 1), Pos(*config.CARD_IMG_SIZE_BIG))
        self.buttons = Board(Pos(*config.BUTTON_BOARD_SQUARES), Pos(*config.BUTTON_SIZE))

        # setup players
        self.player1: Player = HumanPlayer(self, self.player1Board, 1, Pos(6, 8))
        self.player2: Player = ComputerPlayer(self, self.player2Board, 2, Pos(6, 2))
        self.player1.opponent, self.player2.opponent = self.player2, self.player1
        self.currentPlayer: Player = self.player1

        # setup display handler
        self.display = DisplayHandler()
        for board in [self.mainBoard, self.player1Board, self.player2Board,self.choiceBoard, self.bigCard,self.buttons]:
            self.display.add_board(board)

        # setup cards
        self.cardPiles: List[Pile] = CardData.prepare_piles()
        self.eventCards: List[Event] = CardData.create_event_cards()
        self.infraCardsLeft = {
            Village: config.VILLAGES_COUNT,
            Path: config.PATHS_COUNT,
            Town: config.TOWNS_COUNT
        }

        # init boards and setup their cards
        self.boards_arrange()
        self.init_main_board_starting_cards()

        self.bigCard.fill_board(MetaCard('empty'))
        self.buttons.fill_board(MetaCard('empty'))

        self.landscapeCards: List[Landscape] = self.prepare_landscape_cards()

        self.roundNo: int = 1

    ####################################################################################################################
    #################   INITIALIZATION   ###############################################################################
    ####################################################################################################################

    def boards_arrange(self) -> None:
        smallSpace, bigSpace = config.CARD_IMG_SPACING, config.BIG_SPACE
        cardSize = self.mainBoard.squareSize

        self.mainBoard.set_top_left(Pos(0, 0))
        self.player1Board.set_top_left(Pos(self.mainBoard.size.x * (cardSize.x + 2 * smallSpace) + bigSpace,
                                           (self.mainBoard.size.y - self.player1Board.size.y) * (
                                                   cardSize.y + 2 * smallSpace)))

        self.player2Board.set_top_left(
            Pos(self.mainBoard.size.x * (cardSize.x + 2 * smallSpace) + smallSpace + bigSpace, 0))

        self.choiceBoard.set_top_left(Pos(self.mainBoard.size.x * (cardSize.x + 2 * smallSpace) + smallSpace + bigSpace,
                                          self.player2Board.bottomRight.y + 2 * bigSpace))

        self.bigCard.set_top_left(Pos(self.mainBoard.size.x * (cardSize.x + 2 * smallSpace) + smallSpace + bigSpace,
                                      (
                                              self.player1Board.topLeft.y + self.choiceBoard.bottomRight.y) // 2 - self.bigCard.squareSize.y // 2))
        self.buttons.set_top_left(Pos(self.bigCard.bottomRight.x + bigSpace, self.bigCard.topLeft.y))
        self.display.textTopLeft = Pos(self.choiceBoard.topLeft.x, self.choiceBoard.bottomRight.y + 2 * smallSpace)


    def init_main_board_starting_cards(self):
        for pos in (Pos(x, y) for x in range(self.mainBoard.size.x) for y in range(self.mainBoard.size.y)):
            self.mainBoard.set_square(pos, MetaCard('empty'))

        for player in [self.player1, self.player2]:
            self.mainBoard.set_square(player.midPos, Path(player.midPos, player))
            for pos in [player.midPos.right(), player.midPos.left()]:
                player.place_village_to_board(pos)

        self.mainBoard.set_square(Pos(0, 5), MetaCard('back_event'))
        self.mainBoard.set_square(Pos(1, 5), MetaCard('back_land'))
        self.mainBoard.set_square(Pos(2, 5), MetaCard('back_path'))
        self.mainBoard.set_square(Pos(3, 5), MetaCard('back_village'))
        self.mainBoard.set_square(Pos(4, 5), MetaCard('back_town'))

        for x in range(self.mainBoard.size.x - len(self.cardPiles), self.mainBoard.size.x):
            self.mainBoard.set_square(Pos(x, 5), MetaCard('back'))


    def prepare_landscape_cards(self) -> List[Landscape]:
        landCards: List[Landscape] = []
        for card in CardData.create_landscape_cards(self.player1, self.player2):
            if card.player is not None:
                card.player.setup_land_card(card)
            else:
                landCards.append(card)
        return landCards

    ####################################################################################################################
    #################   CARD EVENTS      ###############################################################################
    ####################################################################################################################

    def card_event_builder(self) -> None:
        pile: Optional[Pile] = None
        for player in [self.currentPlayer, self.currentPlayer.opponent]:
            pile = player.opponent.select_pile(pile)
            player.opponent.get_card_from_choice(pile)
            cardIdx = player.select_card_to_throw_away()
            card = player.cardsInHand.pop(cardIdx)
            pile.append(card)
            player.refresh_hand_board()


    def card_event_civil_war(self) -> None:
        for player in [self.currentPlayer, self.currentPlayer.opponent]:
            if self.can_remove_unit_civil_war(player.opponent):
                print(f'player {player.opponent} has something to be removed')
                cardToRemove: Buildable = player.select_opponents_unit_to_remove()
                print(f'selected card: {cardToRemove.name}, pos: {cardToRemove.pos}')

                player.take_back_to_hand(cardToRemove)
                # TODO - refill hand (remove excess card)
            else:
                print(f'player {player.opponent} has nothing to be removed')

    def card_event_rich_year(self) -> None:
        for player in [self.currentPlayer, self.currentPlayer.opponent]:
            for land in player.landscapeCards:
                land.resourcesHeld = min(self.get_neighboring_warehouse_cnt(land) + land.resourcesHeld,
                                         config.MAX_LAND_RESOURCES)

    def card_event_advance(self) -> None:
        for player in [self.currentPlayer, self.currentPlayer.opponent]:
            player.get_advance_resource_cnt()

    def card_event_new_year(self) -> None:
        random.shuffle(self.eventCards)


    def card_event_conflict(self) -> None:
        player1Strength = self.player1.get_battle_strength()
        player2Strength = self.player2.get_battle_strength()

        print(f'player 1 strength: {player1Strength}')
        print(f'player 2 strength: {player2Strength}')

        if player1Strength > player2Strength:
            print('battle winner is player1')
            winner = self.player1
        elif player1Strength < player2Strength:
            print('battle winner is player2')
            winner = self.player2
        else:
            print('battle has no winner')
            return

        pile = winner.select_pile()
        for _ in range(2):
            self.display_cards_for_choice(winner.opponent.cardsInHand)
            card: Playable = winner.select_opponents_card_to_discard()
            winner.opponent.cardsInHand.remove(card)
            pile.append(card)


    def get_land_settlements(self, land: Landscape) -> Iterator[Settlement]:
        assert land.pos is not None and land.player is not None
        for x in [land.pos.x + 1, land.pos.x - 1]:
            if 0 < x < self.mainBoard.size.x - 1:
                card = self.mainBoard.get_square(Pos(x, land.player.midPos.y))
                if isinstance(card, Settlement):
                    yield card

    def is_land_protected_from_plaque(self, land: Landscape) -> bool:
        for settlement in land.settlements:
            if 'church' in map(lambda x: x.name, settlement.cards):
                return True
        return False

    def card_event_plaque(self) -> None:
        print('event card: plaque')
        for player in [self.currentPlayer, self.currentPlayer.opponent]:
            if player.has_global_plaque_protection():
                continue

            for land in player.landscapeCards:
                assert land.pos is not None
                if not self.is_land_protected_from_plaque(land):
                    land.resourcesHeld = max(0, land.resourcesHeld - 1)
                    self.mainBoard.refresh_square(land.pos)


    def card_event(self):
        event: Event = self.eventCards.pop(0)
        self.eventCards.append(event)
        print(f'card event: {event.name}')

        if event.eventType == EventCardType.BUILDER:
            self.card_event_builder()
        elif event.eventType == EventCardType.CIVIL_WAR:
            self.card_event_civil_war()
        elif event.eventType == EventCardType.RICH_YEAR:
            self.card_event_rich_year()
        elif event.eventType == EventCardType.ADVANCE:
            self.card_event_advance()
        elif event.eventType == EventCardType.NEW_YEAR:
            self.card_event_new_year()
        elif event.eventType == EventCardType.CONFLICT:
            self.card_event_conflict()
        elif event.eventType == EventCardType.PLAQUE:
            self.card_event_plaque()
        else:
            assert False, f'unknown card event: {event}'

    ####################################################################################################################
    #################   DICE EVENTS      ###############################################################################
    ####################################################################################################################

    def handle_dice_events(self, event: DiceEvent):
        if event == DiceEvent.TOURNAMENT:
            self.event_tournament()
        elif event == DiceEvent.TRADE_PROFIT:
            self.event_trade_profit()
        elif event == DiceEvent.AMBUSH:
            self.event_ambush()
        elif event == DiceEvent.GOOD_HARVEST:
            self.event_good_harvest()
        elif event == DiceEvent.CARD_EVENT:
            self.card_event()
        else:
            raise ValueError(f'unknown dice event: {event}')


    def event_tournament(self) -> None:
        player1Strength = self.player1.get_tournament_strength()
        player2Strength = self.player2.get_tournament_strength()

        print(f'player 1 strength: {player1Strength}')
        print(f'player 2 strength: {player2Strength}')

        if player1Strength > player2Strength:
            print('tournament winner is player1')
            self.player1.pick_any_resource()
        elif player1Strength < player2Strength:
            print('tournament winner is player2')
            self.player2.pick_any_resource()
        else:
            print('tournament has no winner')


    def event_trade_profit(self) -> None:
        player1Profit = self.player1.get_trade_strength()
        player2Profit = self.player2.get_trade_strength()

        print(f'player 1 strength: {player1Profit}')
        print(f'player 2 strength: {player2Profit}')

        if player1Profit > player2Profit:
            print('trade profit for player 1')
            winner = self.player1
        elif player1Profit < player2Profit:
            print('trade profit for player 2')
            winner = self.player2
        else:
            print('no trade profit')
            return

        winner.grab_any_resource_if_possible()


    def event_good_harvest(self) -> None:
        self.player1.pick_any_resource()
        self.player2.pick_any_resource()


    def event_ambush(self) -> None:
        for player in [self.player1, self.player2]:
            if player.get_unprotected_resources_cnt() > config.AMBUSH_MAX_RESOURCES:
                player.lose_ambush_resources()

    ####################################################################################################################
    #################                    ###############################################################################
    ####################################################################################################################

    def get_filtered_click(self, clickFilters: Tuple[ClickFilter, ...] = ()) -> MouseClick:
        while True:
            click: MouseClick = self.display.get_mouse_click()
            if click.board.get_square(click.pos) is None:
                continue
            if not clickFilters:
                return click
            for clickFilter in clickFilters:
                if clickFilter.accepts(click):
                    return click


    def is_victory(self) -> bool:
        return self.player1.victoryPoints >= config.VICTORY_POINTS or self.player2.victoryPoints >= config.VICTORY_POINTS


    def is_protected_from_civil_war(self, card: Knight | Fleet) -> bool:
        for protection in config.CIVIL_WAR_PROTECTION:
            assert card.settlement is not None
            if protection in map(lambda c: c.name, card.settlement.cards):
                return True
        return False

    def can_remove_unit_civil_war(self, player: Player) -> bool:
        for knight in player.knightsPlayed:
            if not self.is_protected_from_civil_war(knight):
                return True
        for fleet in player.fleetPlayed:
            if not self.is_protected_from_civil_war(fleet):
                return True
        return False

    def remove_card_from_board(self, card: Buildable) -> None:
        assert card.pos is not None and card.settlement is not None
        slot = SettlementSlot(card.pos)
        self.mainBoard.set_square(card.pos, slot)
        slot.settlement = card.settlement
        card.settlement.cards.remove(card)
        card.settlement.cards.append(slot)


    def select_card(self, card: Card):
        self.bigCard.set_square(Pos(0, 0), card)

    def display_cards_for_choice(self, pile: Pile) -> None:
        self.choiceBoard.clear()
        for card in pile:
            self.choiceBoard.set_next_square(card)

    def throw_yield_dice(self) -> int:
        return random.randint(1, 6)

    def get_neighboring_warehouse_cnt(self, land: Landscape) -> int:
        cnt = 0
        for b in self.get_land_neighbors(land):
            if b.name == 'warehouse':
                cnt += 1
        return cnt

    def is_protected_by_warehouse(self, land: Landscape) -> bool:
        return 'warehouse' in map(lambda b: b.name, self.get_land_neighbors(land))

    def get_land_neighbors(self, card: Landscape) -> List[Buildable]:
        assert card.pos is not None and card.player is not None
        posLst: List[Pos] = []
        if card.pos.x > 0:
            posLst.append(card.pos.left())
            posLst.append(card.pos.left().down() if card.pos.y > card.player.midPos.y else card.pos.left().up())
        if card.pos.x < self.mainBoard.size.x - 1:
            posLst.append(card.pos.right())
            posLst.append(card.pos.right().down() if card.pos.y > card.player.midPos.y else card.pos.right().up())

        retLst: List[Buildable] = []
        for pos in posLst:
            square = self.mainBoard.get_square(pos)
            if isinstance(square, Buildable):
                retLst.append(square)
        return retLst

    # TODO - refactor
    def get_land_yield(self, card: Landscape) -> int:
        if card.resource == Resource.GOLD:
            return 1
        buildingNeeded = MILLS_EFFECTS[card.resource]
        # TODO this double isinstance is ugly - improve it somehow
        buildingsAvailable = filter(lambda b: isinstance(b, Building), self.get_land_neighbors(card))
        return 2 if buildingNeeded in map(lambda b: isinstance(b, Building) and b.buildingType,
                                          buildingsAvailable) else 1

    def land_yield(self, number: int):
        for player in [self.player1, self.player2]:
            for land in player.landscapeCards:
                if land.diceNumber == number and land.resourcesHeld < config.MAX_LAND_RESOURCES:
                    land.resourcesHeld = min(land.resourcesHeld + self.get_land_yield(land), config.MAX_LAND_RESOURCES)
                    assert land.pos is not None
                    self.mainBoard.refresh_square(land.pos)

    def throw_event_dice(self) -> DiceEvent:
        return DiceEvents[random.randint(1, 6)]

    def debug_give_resource(self, player: Player, cost: Cost):
        for card in player.landscapeCards:
            assert card.pos is not None
            card.resourcesHeld = cost.get(card.resource)
            self.mainBoard.refresh_square(card.pos)

    def play(self):
        for player in [self.player1, self.player2]:
            player.initial_land_setup()

        for player in [self.player1, self.player2]:
            player.pick_starting_cards()

        self.debug_give_resource(self.currentPlayer, Cost(sheep=2, wood=2, rock=3, grain=2))

        while not self.is_victory():
            print(f'\n========  round {self.roundNo} ========')
            self.currentPlayer.throw_dice()
            self.currentPlayer.do_actions()
            self.currentPlayer.refill_hand(True)
            self.currentPlayer.opponent.refill_hand(False)
            self.currentPlayer = self.currentPlayer.opponent
            self.roundNo += 1
