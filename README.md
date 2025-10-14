# Trust Me on This: A User Study of Explainability for AI-Generated Responses

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Summary

The integration of generative AI into information access systems often presents users with synthesized answers that lack transparency. This study investigates how different types of explanations can influence user trust in responses from retrieval-augmented generation systems. We conducted a controlled, two-stage user study where participants chose the more trustworthy response from a pair—one objectively more reliable than the other—both with and without one of three explanation types: (1) source attribution, (2) factual grounding, and (3) information coverage. Our results show that while explanations significantly guide users toward selecting more reliable information, trust is not dictated by objective quality alone: Users’ judgments are also heavily influenced by response clarity, actionability, and their own prior knowledge.

## Explainable Response Generation
The response generation and explanation modules extend the [**GINGER**](https://github.com/iai-group/ginger-response-generation) pipeline.  
A new **nugget-based explanation generator** produces post-hoc explanations targeting three response dimensions:
- **Source Attribution**
- **Factual Grounding**
- **Information Coverage**

All related scripts are located in [`code/`](code/), with modifications described in its [README](code/README.md).  
The only modified file from the original GINGER pipeline is the `summarizer.py`.

---

## Data
All input data, generated responses, annotations, and user study results are available in the [`data/`](data/) directory (see [README](data/README.md) for details).  
The data include:
- 30 information-seeking queries from **TREC CAsT '22** with automatically generated responses and explanations produced with the GINGER response generation pipeline
- Data from the qualification task used to recruit and screen crowd workers
- Data collected in the main user study, where participants compared system-generated responses of various quality, with and without explanations

## User Study Design

The user study was conducted on **Amazon Mechanical Turk (MTurk)** and consisted of:
1. A **qualification task** assessing participants’ comprehension.
2. The **main user trust study** comparing reliable vs. unreliable responses across explanation types.

Screenshots of both interfaces are available in [`user_study_design/`](user_study_design/) (see [README](user_study_design/README.md)).

## Results
The processed outputs and aggregated statistics for the data collected in the user study can be found in:
- [`data/user_study/output_processed.csv`](data/user_study/output_processed.csv)
- [`data/user_study/trust_scores_distribution.pdf`](data/user_study/trust_scores_distribution.pdf)

Key findings:
- User trust does not always align with objective quality of the response.
- Source attribution most strongly boosts trust, especially for factual queries.
- Clarity, detail, and user expertise play major roles in shaping trust.

**All collected data, generated responses, and annotations are publicly available in this repository.**

## Citation

TODO

## Contact

TODO
