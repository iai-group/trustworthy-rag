import ast
import pandas as pd
import random

from response_generation.detect_response_aspects import GTPAspectsDetector

def main():
    data = pd.read_csv("data/user_study/input_responses.csv")

    response_1_correct_aspects = []
    response_1_incorrect_aspects = []
    response_2_correct_aspects = []
    response_2_incorrect_aspects = []
    response_1_selected_aspects = []
    response_1_selected_aspects_scores = []
    response_2_selected_aspects = []
    response_2_selected_aspects_scores = []
    responses_1 = []
    responses_2 = []
    response_1_types = []
    response_2_types = []
    response_1_sources = []
    response_2_sources = []
    response_1_explanations = []
    response_2_explanations = []

    aspects_detector = GTPAspectsDetector()

    for _, row in data.iterrows():
        if row["explanation_type"] == "grounding":
            order = ["ginger_response_support", "llm_zero_shot_response"]
        elif row["explanation_type"] == "source_attribution":
            order = ["ginger_response", "llm_zero_shot_response"]
        else:
            order = ["ginger_response", "single_aspect_response"]
 
        random.shuffle(order)
        response_1 = row[order[0]]
        response_2 = row[order[1]]
        responses_1.append(response_1)
        responses_2.append(response_2)
        response_1_types.append(order[0])
        response_2_types.append(order[1])


        if row["explanation_type"] == "source_attribution":
            if order[0] == "ginger_response_support":
                response_1_sources.append(row["source"])
                response_1_explanations.append("")
                response_2_sources.append("")
                response_2_explanations.append("This response is based only on the model's internal memory and is not grounded in verifiable sources.")
            else:
                response_2_sources.append(row["source"])
                response_2_explanations.append("")
                response_1_sources.append("")
                response_1_explanations.append("This response is based only on the model's internal memory and is not grounded in verifiable sources.")
        elif row["explanation_type"] == "grounding":
            if order[0] == "ginger_response":
                response_1_sources.append(row["source"])
                response_1_explanations.append("")
                response_2_sources.append("")
                response_2_explanations.append("The response has no traceable origin, so it's not possible to verify each claim against a reliable source.")
            else:
                response_2_sources.append(row["source"])
                response_2_explanations.append("")
                response_1_sources.append("")
                response_1_explanations.append("The response has no traceable origin, so it's not possible to verify each claim against a reliable source.")
        else:
            response_1_sources.append("")
            response_2_sources.append("")
            if order[0] == "ginger_response":
                response_1_explanations.append("The response covers multiple aspects of the topic, providing a broad view.")
                response_2_explanations.append("The response focuses on just one aspect and may miss important points related to: " + row["additional_aspects"])
            else:
                response_2_explanations.append("The response covers multiple aspects of the topic, providing a broad view.")
                response_1_explanations.append("The response focuses on just one aspect and may miss important points related to: " + row["additional_aspects"])
            


        aspects_response_1 = aspects_detector.detect_aspects(response_1)
        response_1_correct_aspects.append(
            [k for k in aspects_response_1 if aspects_response_1[k] == 1]
        )
        response_1_incorrect_aspects.append(
            [k for k in aspects_response_1 if aspects_response_1[k] == 0]
        )

        aspects_response_2 = aspects_detector.detect_aspects(response_2)
        response_2_correct_aspects.append(
            [k for k in aspects_response_2 if aspects_response_2[k] == 1]
        )
        response_2_incorrect_aspects.append(
            [k for k in aspects_response_2 if aspects_response_2[k] == 0]
        )

        keys_1 = random.sample(list(aspects_response_1), 4)
        while sum([aspects_response_1[k] for k in keys_1]) == 0:
            keys_1 = random.sample(list(aspects_response_1), 4)
        response_1_selected_aspects.append(keys_1)
        response_1_selected_aspects_scores.append(
            [aspects_response_1[k] for k in keys_1]
        )

        keys_2 = random.sample(list(aspects_response_2), 4)
        while sum([aspects_response_2[k] for k in keys_2]) == 0:
            keys_2 = random.sample(list(aspects_response_2), 4)
        response_2_selected_aspects.append(keys_2)
        response_2_selected_aspects_scores.append(
            [aspects_response_2[k] for k in keys_2]
        )

    data["response_1"] = responses_1
    data["response_2"] = responses_2
    data["response_1_type"] = response_1_types
    data["response_2_type"] = response_2_types
    # data["response_1_correct_aspects"] = response_1_correct_aspects
    # data["response_1_incorrect_aspects"] = response_1_incorrect_aspects
    # data["response_2_correct_aspects"] = response_2_correct_aspects
    # data["response_2_incorrect_aspects"] = response_2_incorrect_aspects
    data["response_1_aspects"] = response_1_selected_aspects
    data["response_1_selected_aspects_scores"] = response_1_selected_aspects_scores
    data["response_2_aspects"] = response_2_selected_aspects
    data["response_2_selected_aspects_scores"] = response_2_selected_aspects_scores
    data["response_1_sources"] = response_1_sources
    data["response_2_sources"] = response_2_sources
    data["response_1_explanations"] = response_1_explanations
    data["response_2_explanations"] = response_2_explanations

    data.to_csv("data/user_study/input_responses_w_explanations.csv", index=False)

if __name__ == "__main__":
    main()