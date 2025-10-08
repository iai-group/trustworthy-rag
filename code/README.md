# Code

This directory contains all the scripts used for data preparation, response generation, explanation generation, and analysis in the user trust study on explainable conversational responses.  Each submodule corresponds to a key stage of the study pipeline.

## `response_generation/`

Scripts responsible for generating and annotating system responses used in the study.

- [`generate_ginger_responses.py`](response_generation/generate_ginger_responses.py)  
  Generates candidate responses for each query using the [GINGER](https://github.com/iai-group/ginger-response-generation) nugget-based response generation pipeline.
- [`detect_response_aspects.py`](response_generation/detect_response_aspects.py)  
  Automatically detects and labels response aspects used for qualification task and quality check question in the actual user study.

## `qualification_task/`

Scripts related to the MTurk qualification phase used to select reliable and engaged crowd workers.

- [`process_mturk_output.py`](qualification_task/process_mturk_output.py)  
  Processes and scores worker submissions from the qualification task, determining which participants qualified (≥4/5 correct answers).

## `user_study/`

Scripts used for preparing and processing the main user study on MTurk.

- [`prepare_mturk_input.py`](user_study/prepare_mturk_input.py)  
  Formats the selected responses and explanations into MTurk HITs for data collection.  
- [`generate_explanations.py`](user_study/generate_explanations.py)  
  Generates three types of explanations — source attribution, factual grounding, and information coverage — for system responses.  
- [`process_mturk_output.py`](user_study/process_mturk_output.py)  
  Processes and cleans the MTurk study results, merging user judgments and metadata for further statistical analysis.

## `analysis/`

Scripts for analyzing the user study results.

- [`trust_scores_distribution.py`](analysis/trust_scores_distribution.py)  
  Generates visualizations and summary statistics of trust preferences across explanation types and conditions (e.g., trust score distribution plots).