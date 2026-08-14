# Word Count Refactor

Progressive refactor of a word-frequency script, illustrating GenAI-assisted iteration:

- `word_count_v1.py` — baseline: download a single URL, count words.
- `word_count_v2_parallel.py` — adds multiprocessing across multiple URLs.
- `word_count_v3_robust.py` — adds URL validation, timeouts, and structured logging on top of v2.
