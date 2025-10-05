# Data

This folder contains all data collected and generated for the user study on **user trust in system-generated responses**.  
It includes the input materials, qualification task data, and user study results.


## Folder Structure

### [`generated_responses/`](generated_responses/)
Contains system-generated responses and source passages used in the user study.

- [`input_queries.csv`](generated_responses/input_queries.csv) – 30 information-seeking queries from TREC CAsT '22 dataset, each with the top 3 relevant passages according to human relevance judgments.  
- [`generated_responses_all_variants.csv`](generated_responses/generated_responses_all_variants.csv) – All response variants generated for the 30 queries (considering two reliability levels and three different response dimensions: source attribution, factual grounding, and information coverage).


### [`qualification_task/`](qualification_task/)
Contains the data used to screen participants before the main study.

- [`input_queries.csv`](qualification_task/input_queries.csv) – 5 qualification queries with 4 key aspects per query.  
- [`input_mturk_format.csv`](qualification_task/input_mturk_format.csv) – Task formatted for Amazon Mechanical Turk (MTurk).  
- [`output.csv`](qualification_task/output.csv) – Raw results from all MTurk participants.  
- [`output_processed.csv`](qualification_task/output_processed.csv) – Processed qualification results with participant accuracy scores.  
  - Participants who answered ≥4/5 correctly were qualified for the main study.


### [`user_study/`](user_study/)
Contains the main user study inputs and outputs.

- [`input_responses.csv`](user_study/input_responses.csv) – 30 queries, each paired with one *reliable* and one *unreliable* response, selected from the generated variants.  
- [`input_responses_w_explanations.csv`](user_study/input_responses_w_explanations.csv) – Same responses, enriched with automatically generated explanations and annotated response aspects.  
- [`mturk_input.csv`](user_study/mturk_input.csv) – MTurk-ready input for the main user study.  
- [`mturk_output.csv`](user_study/mturk_output.csv) – Raw participant data collected from MTurk.  
- [`output_processed.csv`](user_study/output_processed.csv) – Cleaned and structured study results including trust judgments,  explanation types, and scores for the quality check question about response aspects.  
- [`trust_scores_distribution.pdf`](user_study/trust_scores_distribution.pdf) – Distribution plot of trust scores across conditions.


## Notes

- Explanations were generated automatically (post-hoc) using a nugget-based approach supporting three response dimensions:  
  **source attribution**, **factual grounding**, and **information coverage**. The explanation generator was built on top of GINGER code.  
- The data in this folder include all user annotations, response variants, and processed evaluation results used in the analysis presented in the paper. MTurk crowd workers IDs are anonymized.