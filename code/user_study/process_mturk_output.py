import pandas as pd
import ast

def main():
    data = pd.read_csv("data/user_study/mturk_output.csv", sep=";", index=False)
    print(len(data))

    input_data = pd.read_csv("data/user_study/input_responses_w_explanations.csv")

    reliable_response_types = ["ginger_response", "ginger_response_support"]
    unreliable_response_types = ["single_aspect_response", "llm_zero_shot_response"]             	

    queries = []
    user_ids = []
    reliable_response_ids = []
    unreliable_response_ids = []
    reliable_responses = []
    unreliable_responses = []
    trust_scores = []
    picked_better_lst = []
    explanation_type_lst = []
    explanation_shown_lst = []
    justifications = []
    aspects_scores = []
    trust_preferences = []

    for sub_id, submission in data.iterrows():
        submission_queries = ast.literal_eval(submission["Input.question"])
        submission_responses = ast.literal_eval(submission["Input.answers"])
        submission_limitations = ast.literal_eval(submission["Input.limitations"])
        submission_aspects = ast.literal_eval(submission["Input.aspects"])
        user_id = submission["WorkerId"]
        
        for i in range(0, 12):
            query = submission_queries[i]
            query_responses = submission_responses[i]
            input_row = input_data[input_data["query"] == query]

            queries.append(query)
            user_ids.append(user_id) 
            
            if list(input_row["response_1_type"])[0] in reliable_response_types:
                reliable_response_id = "response_0"
                reliable_response = query_responses[0]
                unreliable_response_id = "response_1"
                unreliable_response = query_responses[1]
            else:
                reliable_response_id = "response_1"
                reliable_response = query_responses[1]
                unreliable_response_id = "response_0"
                unreliable_response = query_responses[0]
            
            reliable_response_ids.append(reliable_response_id)
            unreliable_response_ids.append(unreliable_response_id)
            reliable_responses.append(reliable_response)
            unreliable_responses.append(unreliable_response)

            trust_scores.append([1 if submission["Answer.query_" + str(i) + ".trust_" + str(j)] else 0 for j in range(0, 5)])
            picked_0 = True in [submission["Answer.query_" + str(i) + ".trust_0"], submission["Answer.query_" + str(i) + ".trust_1"]]
            picked_1 = True in [submission["Answer.query_" + str(i) + ".trust_3"], submission["Answer.query_" + str(i) + ".trust_4"]]
            picked_tie = submission["Answer.query_" + str(i) + ".trust_2"] == True

            trust_preference = None

            if reliable_response_id == "response_0" and picked_0 or reliable_response_id == "response_1" and picked_1:
                picked_better = True
                if True in [submission["Answer.query_" + str(i) + ".trust_0"], submission["Answer.query_" + str(i) + ".trust_4"]]:
                    trust_preference = "Trust more reliable response a lot more"
                elif True in [submission["Answer.query_" + str(i) + ".trust_1"], submission["Answer.query_" + str(i) + ".trust_3"]]:
                    trust_preference = "Trust more reliable response slightly more"
            elif picked_tie:
                picked_better = -1
                trust_preference = "Trust both responses about the same"
            else:
                picked_better = False
                if True in [submission["Answer.query_" + str(i) + ".trust_0"], submission["Answer.query_" + str(i) + ".trust_4"]]:
                    trust_preference = "Trust more unreliable response a lot more"
                elif True in [submission["Answer.query_" + str(i) + ".trust_1"], submission["Answer.query_" + str(i) + ".trust_3"]]:
                    trust_preference = "Trust more unreliable response slightly more"

            trust_preferences.append(trust_preference)

            explanation_shown = submission_limitations[i] != ["", ""]
    
            picked_better_lst.append(picked_better)
            explanation_type_lst.append(list(input_row["explanation_type"])[0])
            explanation_shown_lst.append(explanation_shown)
            justifications.append(submission["Answer.query_" + str(i) + "-justification"])

            if submission_aspects[i] == ["", ""]:
                aspects_scores.append(-1)
            else:
                res_scores = []
                for res_id in range(0, 2):
                    res_score = []
                    for aspect_id in range(0, 4):
                        if submission["Answer.query_" + str(i) + "-response_" + str(res_id) + "-aspects.aspect_" + str(aspect_id)] == True:
                            res_score.append(1)
                        else:
                            res_score.append(0)
                    res_scores.append(int(str(res_score) == input_row["response_" + str(res_id + 1) + "_selected_aspects_scores"]))
                aspects_scores.append(res_scores)

    study_results = pd.DataFrame({
        "queries": queries,
        "user_ids": user_ids,
        "reliable_response_ids": reliable_response_ids,
        "reliable_responses": reliable_responses,
        "unreliable_response_ids": unreliable_response_ids,
        "unreliable_responses": unreliable_responses,
        "trust_scores": trust_scores,
        "picked_better_lst": picked_better_lst,
        "trust_preferences": trust_preferences,
        "explanation_type_lst": explanation_type_lst,
        "explanation_shown_lst": explanation_shown_lst,
        "justifications": justifications,
        "aspect_scores": aspects_scores,
    })

    print(sum(picked_better_lst))
    print(sum(explanation_shown_lst))

    study_results.to_csv("data/user_study/output_processed.csv", sep=";", index=False)
    

if __name__ == "__main__":
    main()