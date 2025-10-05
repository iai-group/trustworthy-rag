import ast
import re
import numpy as np
import pandas as pd
import random

from aspects_detection import GTPAspectsDetector

def main():
    data = pd.read_csv("data/user_study/input_responses_w_explanations.csv")

    data_grounding = data[data["explanation_type"] == "grounding"]
    data_source_attribution = data[data["explanation_type"] == "source_attribution"]
    data_information_coverage = data[data["explanation_type"] == "information_coverage"]

    queries = []
    responses = []
    sources = []
    explanations = []
    aspects = []

    task_types = ["grounding", "source_attribution", "information_coverage"]
    dataframes =  {
        "grounding": data_grounding,
        "source_attribution": data_source_attribution,
        "information_coverage": data_information_coverage
    }

    for i in range(0, 5):
        random.shuffle(task_types)
        task_queries = []
        task_responses = []
        task_sources = []
        task_explanations = []
        task_aspects = []

        for j in [i, i+5]:
            for task_type in task_types:
                dataframe = dataframes[task_type]
                task_queries.append(str(list(dataframe["query"])[j]))
                task_responses.append(
                    [
                        re.sub(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", str(list(dataframe["response_1"])[j])), 
                        re.sub(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", str(list(dataframe["response_2"])[j]))
                    ]
                )
                task_sources.append(["", ""])
                task_explanations.append(["", ""])
                task_aspects.append(
                    [
                        ast.literal_eval(list(dataframe["response_1_aspects"])[j]),
                        ast.literal_eval(list(dataframe["response_2_aspects"])[j])
                    ]
                )

                task_queries.append(str(list(dataframe["query"])[j]))
                task_responses.append(
                    [
                        str(list(dataframe["response_1"])[j]), 
                        str(list(dataframe["response_2"])[j])
                    ]
                )
                task_sources.append(
                    [
                        ast.literal_eval(list(dataframe["response_1_sources"])[j]) if str(list(dataframe["response_1_sources"])[j]) != 'nan' else "", 
                        ast.literal_eval(list(dataframe["response_2_sources"])[j]) if str(list(dataframe["response_2_sources"])[j]) != 'nan' else ""
                    ]
                )
                task_explanations.append(
                    [
                        str(list(dataframe["response_1_explanations"])[j]) if str(list(dataframe["response_1_explanations"])[j]) != 'nan' else "", 
                        str(list(dataframe["response_2_explanations"])[j]) if str(list(dataframe["response_2_explanations"])[j]) != 'nan' else ""
                    ]
                )
                task_aspects.append(["", ""])
        
        queries.append(task_queries)
        responses.append(task_responses)
        sources.append(task_sources)
        explanations.append(task_explanations)
        aspects.append(task_aspects)
    
    new_data = pd.DataFrame({
        "question": queries,
        "answers": responses,
        "sources": sources,
        "limitations": explanations,
        "aspects": aspects,
    })

    # new_data['question'].str.replace("’", "'")
    # new_data['answers'].str.replace("’", "'")
    # new_data['sources'].str.replace("’", "'")
    # new_data['limitations'].str.replace("’", "'")
    # new_data['aspects'].str.replace("’", "'")

    # new_data = new_data.replace(np.nan, '', regex=True)

    new_data.to_csv("data/user_study/mturk_input.csv", sep = "#", index=False)

if __name__ == "__main__":
    main()