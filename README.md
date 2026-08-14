# Generative AI for Software Development

Hands-on portfolio for the [Generative AI for Software Development](https://www.deeplearning.ai/) specialization (DeepLearning.AI / Coursera).

Lectures run on a hosted JupyterLab environment on the Coursera platform, where graded assignments must ultimately be submitted for automated grading. To avoid redoing work and to keep a demonstrable record of progress, this repository mirrors that work: labs and exercises are developed and version-controlled locally, then copied into the platform's notebook only for final submission and grading.

## Structure

```
labs/                              ungraded lecture code examples
  data-structures/                 binary tree, linked list, AVL tree, graph implementations
  word-count-refactor/             progressive refactor of a word-counting script (v1 -> v3)
assignments/                       graded labs (baseline copy from the Lab, worked locally)
  c1m3-travel-flight-optimization/ Dijkstra + TSP on graphs (Course 1, Module 3)
resources/
  lab-environment-guide.md         notes on the platform's hosted lab environment
```

## Environment

Recommended: Python 3.11/3.12 in a dedicated virtual environment (`venv` or `conda`), since some deep learning libraries lag behind the latest Python releases.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Workflow for graded labs

1. Download or write the lab notebook/script locally.
2. Develop and test it in this repository (with local Jupyter or scripts).
3. Commit and push to GitHub as a portfolio record.
4. Copy the finished solution into the platform's hosted notebook and submit there for grading.
