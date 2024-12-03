from collections import defaultdict
from typing import Sequence
import regex as re  # type: ignore [import-untyped]
import logging

class BPETokeniser:
    PRE_TOKE_PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    def __init__(self, special_tokens: Sequence[str]=("<|endoftext|>",)) -> None:
        # Initialise vocab
        self.vocab = [toke.encode("utf-8") for toke in special_tokens] + list(map(lambda ind: bytes([ind]), range(256)))
        self.initial_size = len(self.vocab)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(self.vocab)
    
    def train(self, corpus: str, vocab_size: int) -> list[tuple[bytes, bytes]]:
        pre_toke = [
            tuple(map(lambda ind: bytes([ind]), tok.encode("utf-8")))
            for tok in re.findall(BPETokeniser.PRE_TOKE_PAT, corpus)
            # if (cleaned_tok := tok.strip())
        ]
        pre_toke_counts = {
            tok: pre_toke.count(tok)    
            for tok in set(pre_toke)
        }
        self._logger.debug(pre_toke_counts)
        merges: list[tuple[bytes, bytes]] = []
        iterations = 1
        while len(self.vocab) < vocab_size:
            self._logger.debug(f"ITERATION: {iterations}")
            pairs: defaultdict[tuple[bytes, bytes], int] = defaultdict(int)
            for tokens, freq in pre_toke_counts.items():
                self._logger.debug(f"TOKENS: {tokens} | FREQ: {freq}")
                for i in range(1, len(tokens)):
                    pairs[(tokens[i-1], tokens[i])] += freq
            max_pair_count = max(pairs.values())
            self._logger.debug(f"PAIR COUNTS: {dict(sorted(pairs.items(), key=lambda item: item[1]))}")
            max_pair = max([pair for pair, count in pairs.items() if count == max_pair_count])
            merges.append(max_pair)
            self._logger.debug(f"MAX PAIR: {max_pair}")
            pre_toke_counts = {
                (
                    tuple(filter(None, (*tokens[:max(0, idxs[0]-1)], b"".join(max_pair), *tokens[idxs[0]+1:])))
                    if (idxs := [i for i in range(1, len(tokens)) if max_pair == tokens[i-1:i+1]])
                    else tokens
                ): count
                for tokens, count in pre_toke_counts.items()
            }
            self._logger.debug(f"UPDATED TOKEN COUNTS: {pre_toke_counts}")
            self.vocab.append(b"".join(max_pair))
            self._logger.debug("ADDING: %s", b"".join(max_pair))
            iterations += 1
        self._logger.debug("New Tokens: %s", self.vocab[self.initial_size:])
        return merges


if __name__ == "__main__":
    corpus = "\n".join([
        "low low low low low",
        "lower lower widest widest widest",
        "newest newest newest newest newest newest"
    ])
    logging.basicConfig(level=logging.DEBUG)
    print(BPETokeniser().train(corpus, vocab_size=263))