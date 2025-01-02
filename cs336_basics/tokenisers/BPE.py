from collections import Counter, defaultdict
from typing import Iterable, Sequence, TypedDict
import regex as re  # type: ignore [import-untyped]
import logging


class PairIndex(TypedDict):
    count: int
    occurances: set[int]    # word index


class BPETokeniser:
    PRE_TOKE_PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    def __init__(self, special_tokens: Sequence[str]=("<|endoftext|>",)) -> None:
        # Initialise vocab
        self.vocab = [toke.encode("utf-8") for toke in special_tokens] + list(map(lambda ind: bytes([ind]), range(256)))
        self.initial_size = len(self.vocab)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Initialised Vocab: %s", self.vocab)

    def train(self, corpus: str, vocab_size: int) -> list[tuple[bytes, bytes]]: # type: ignore
        def find_pair_in_word(pair: tuple[bytes, bytes], word: tuple[bytes, ...], allow_overlap: bool) -> Iterable[int]:
            i = 0
            while i < len(word)-1:
                if word[i] == pair[0] and word[i+1] == pair[1]:
                    yield i
                    if not allow_overlap:
                        i += 1
                i += 1

        all_tokenised_words = [
            tuple(map(lambda ind: bytes([ind]), tok.encode("utf-8")))
            for tok in re.findall(BPETokeniser.PRE_TOKE_PAT, corpus)
        ]
        tokenised_words = sorted(set(all_tokenised_words))
        word_counts = {tokenised_words.index(word): freq for word, freq in Counter(all_tokenised_words).items()}
        self._logger.debug("WORD COUNTS (%s): %s", len(word_counts), word_counts)
        pair_index: defaultdict[tuple[bytes, bytes], PairIndex] = defaultdict(lambda: {"count": 0, "occurances": set()})
        for wi, tokens in enumerate(tokenised_words):
            freq = word_counts[wi]
            for i in range(len(tokens)-1):
                pair = (tokens[i], tokens[i+1])
                pair_index[pair]["count"] += freq
                pair_index[pair]["occurances"].add(wi)
        self._logger.debug("INITIALISED %s pair counts", len(pair_index))
        merges: list[tuple[bytes, bytes]] = []
        iterations = 0
        while len(self.vocab) < vocab_size:
            iterations += 1
            self._logger.debug(f"ITERATION: {iterations}")
            max_pair_count = max(pair["count"] for pair in pair_index.values())
            self._logger.debug("PAIR COUNTS: %s", dict(sorted(pair_index.items(), key=lambda item: item[1]["count"], reverse=True)))
            max_pair = max([pair for pair, index in pair_index.items() if index["count"] == max_pair_count])
            self._logger.debug("MAX PAIR: %s (%s)", max_pair, max_pair_count)
            merges.append(max_pair)
            merged_pair = b"".join(max_pair)
            self.vocab.append(merged_pair)
            self._logger.debug("ADDING: %s", merged_pair)
            index = pair_index.pop(max_pair)
            ## Adjust surrounding counts
            ##  - any other pairs which end with first part of the new merge or start with the second part of the new merge
            for wi in index["occurances"]:
                word = tokenised_words[wi]
                word_freq = word_counts[wi]
                self._logger.debug("Adjusting pair occurance for word: %s (%s)", word, word_freq)
                updated_word: list[bytes] = []
                prev_idx = -2
                for i in find_pair_in_word(max_pair, word, allow_overlap=False):
                    updated_word += word[prev_idx+2:i]
                    updated_word.append(merged_pair)
                    if i > 0:
                        # There is a preceeding character
                        prefix_pair = (word[i-1], max_pair[0])
                        if prefix_pair != max_pair:
                            pair_index[prefix_pair]["count"] -= word_freq
                            assert pair_index[prefix_pair]["count"] >= 0
                            if wi in pair_index[prefix_pair]["occurances"] and not any(
                                (
                                    j + 2 >= len(word) # No following character, so cannot overlap
                                    or word[j+2] != max_pair[1] # Following character is not the second part of the merged pair
                                ) and (j == 0 or word[j-1] != max_pair[0]) # Preceeding character is not the first part of the merged pair
                                for j in find_pair_in_word(prefix_pair, word, allow_overlap=True)
                            ):
                                # If there is no other occurance of this prefix-pair that does not overlap with the merged pair
                                # -> remove the word idx from occurances
                                pair_index[prefix_pair]["occurances"].remove(wi)
                            if pair_index[prefix_pair]["count"] == 0:
                                pair_index.pop(prefix_pair)
                        if i >= 2 and (word[i-2], word[i-1]) == max_pair:
                            new_pairing = (merged_pair, merged_pair)
                        else:
                            new_pairing = (word[i-1], merged_pair)
                        pair_index[new_pairing]["count"] += word_freq
                        pair_index[new_pairing]["occurances"].add(wi)
                    if i <= len(word) - 3:
                        # There is a following character
                        suffix_pair = (max_pair[1], word[i+2])
                        if suffix_pair != max_pair:
                            pair_index[suffix_pair]["count"] -= word_freq
                            assert pair_index[suffix_pair]["count"] >= 0
                            if wi in pair_index[suffix_pair]["occurances"] and not any(
                                (
                                    j == 0 or word[j-1] != max_pair[0]
                                ) and (j + 2 >= len(word) or word[j+2] != max_pair[1])
                                for j in find_pair_in_word(suffix_pair, word, allow_overlap=True)
                            ):
                                pair_index[suffix_pair]["occurances"].remove(wi)
                            if pair_index[suffix_pair]["count"] == 0:
                                pair_index.pop(suffix_pair)
                        if not (i <= len(word) - 4 and (word[i+2], word[i+3]) == max_pair):
                            new_pairing = (merged_pair, word[i+2])
                            pair_index[new_pairing]["count"] += word_freq
                            pair_index[new_pairing]["occurances"].add(wi)
                    prev_idx = i
                assert prev_idx >= 0
                updated_word += word[prev_idx+2:]
                self._logger.debug("Updated word: %s", tuple(updated_word))
                tokenised_words[wi] = tuple(updated_word)
        self._logger.debug("New Tokens: %s", self.vocab[self.initial_size:])
        return merges


if __name__ == "__main__":
    corpus = "\n".join([
        "low low low low low",
        "lower lower widest widest widest",
        "newest newest newest newest newest newest"
    ])
    print("CORPUS:", corpus)
    logging.basicConfig(level=logging.DEBUG, filename="BPETokeniser.log", filemode="w+")
    n_merges = 6
    target_size = 256 + 1 + n_merges
    tokeniser = BPETokeniser()
    print(tokeniser.train(corpus, vocab_size=target_size))
    print(tokeniser.vocab[tokeniser.initial_size - target_size:])