from typing import Any, final

__all__ = [
    "UTTER_REVISION",
    "KaldiRecognizer",
    "Model",
    "Recognizer",
    "SetLogLevel",
    "__version__",
]

__version__: str
UTTER_REVISION: str

@final
class Model:
    def __new__(cls, path: str) -> Model: ...
    def FindWord(self, word: str) -> int:
        """Word id for a word, -1 when the model does not know it (vosk's FindWord)."""

@final
class KaldiRecognizer:
    """vosk's KaldiRecognizer: a streaming recognizer over one model and one grammar."""

    def __new__(
        cls,
        model: Model,
        sample_rate: float,
        grammar: str,
        unknown_cost: float | None = None,
    ) -> KaldiRecognizer:
        """The grammar is a JSON array of strings as vosk takes it."""

    def SetWords(self, on: Any) -> None:
        """Any value Python considers truthy, as the vosk wheel accepts."""

    def SetPartialWords(self, on: Any) -> None: ...
    def SetEndpointBound(
        self,
        trailing_ms: float | None,
        extending_veto_nats: float | None = None,
    ) -> None:
        """A host endpoint bound: a final once the trailing silence reaches trailing_ms."""

    def SetPartialAlternatives(self, n: int) -> None: ...
    def SetMaxAlternatives(self, n: int) -> None: ...
    def AcceptWaveform(self, data: bytes) -> bool:
        """16-bit little-endian mono PCM. Returns True when an endpoint fired."""

    def DecodedSample(self) -> int:
        """The sample position of the last decoded frame after the last AcceptWaveform."""

    def PartialResult(self) -> str: ...
    def Result(self) -> str: ...
    def FinalResult(self) -> str: ...
    def Reset(self) -> None: ...

Recognizer = KaldiRecognizer

def SetLogLevel(_level: int) -> None:
    """vosk's SetLogLevel; utter logs nothing by default, so this only records the request."""
