from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class TerminationState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """

    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        return len(char) == 1


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        if not (symbol.isascii() and (symbol.isalpha() or symbol.isdigit())):
            raise AttributeError("There can only be letters nad digits")
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym


class StarState(State):

    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state
        self.next_states.append(checking_state)

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True
        return False


class PlusState(State):
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class RegexFSM:
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        self.regex_states = []

        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)

            if char in "*+":
                if not self.regex_states:
                    raise ValueError("Operator cannot be first")

                self.regex_states[-1] = tmp_next_state
                prev_state = tmp_next_state
            else:
                prev_state.next_states.append(tmp_next_state)
                self.regex_states.append(tmp_next_state)
                prev_state = tmp_next_state

        self.termination_state = TerminationState()
        prev_state.next_states.append(self.termination_state)

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()

            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)

            case next_token if next_token.isascii() and (next_token.isalpha() or next_token.isdigit()):
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, string: str):
        possible_places = [(0, 0)]

        while possible_places:
            state_index, string_index = possible_places.pop()

            if state_index == len(self.regex_states):
                if string_index == len(string):
                    return True
                continue

            state = self.regex_states[state_index]

            if isinstance(state, StarState):
                possible_places.append((state_index + 1, string_index))

                next_index = string_index
                while next_index < len(string) and state.check_self(string[next_index]):
                    next_index += 1
                    possible_places.append((state_index + 1, next_index))

            elif isinstance(state, PlusState):
                next_index = string_index

                if next_index < len(string) and state.check_self(string[next_index]):
                    next_index += 1
                    possible_places.append((state_index + 1, next_index))

                    while next_index < len(string) and state.check_self(string[next_index]):
                        next_index += 1
                        possible_places.append((state_index + 1, next_index))

            else:
                if string_index < len(string) and state.check_self(string[string_index]):
                    possible_places.append((state_index + 1, string_index + 1))

        return False

if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
