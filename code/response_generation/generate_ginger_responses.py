import argparse
import ast

import pandas as pd
from transformers import set_seed

from ginger.response_generation.config import OPENAI_API_KEY
from ginger.response_generation.pipeline.components.clustering import BERTopicClustering
from ginger.response_generation.pipeline.components.nugget_detection import GPTNuggetDetector
from ginger.response_generation.pipeline.components.ranker import DuoT5Reranker
from ginger.response_generation.pipeline.components.summarizer import (
    GPTSummarizer,
    rephrase_response,
)
from ginger.response_generation.utilities.ranking import Query, Ranking, ScoredDocument

from nltk import tokenize

set_seed(42)

def main(res_length_limit, baseline):
    data_sample = pd.read_csv("data/input_queries/input_queries.csv")

    queries = []
    queries_ids = []
    passages_used = []
    passages_used_ids = []
    information_nuggets = []
    retrieved_clusters = []
    ranked_clusters = []
    clusters_summaries = []
    clusters_based_responses = []
    passages_summary_zero_shot = []
    support_passages = []
    following_clusters = []
    responses = []
    sources_ids = []
    sources = []
    single_aspect_responses = []
    remaining_clusters = []
    additional_aspects = []

    ginger_version = "ginger"
    nugget_detector = GPTNuggetDetector(api_key=OPENAI_API_KEY)
    clusterer = BERTopicClustering()
    ranker = DuoT5Reranker()
    summarizer = GPTSummarizer(api_key=OPENAI_API_KEY)

    for _, row in data_sample.iterrows():
        data_so_far = pd.DataFrame()
        query = row["query"]
        queries.append(query)
        query_id = str(row["topic_id"]) + str(row["turn_id"])
        queries_ids.append(query_id)
        passages = ast.literal_eval(row["passages"])
        passages_used.append(passages)
        passage_ids = [1,2,3]
        passages_used_ids.append(passage_ids)

        information_nuggets_per_doc = {}
        query_information_nuggets = []
        for passage, passage_id in zip(passages, passage_ids):
            detected_nuggets = nugget_detector.detect_nuggets(query, passage)
            information_nuggets_per_doc[passage_id] = detected_nuggets
            query_information_nuggets.extend(detected_nuggets)
        
        information_nuggets.append(information_nuggets_per_doc)

        print("------------------")
        print("Generating response for query: " + query + " ID: " + query_id)
        if len(query_information_nuggets) <= 1:
            retrieved_clusters.append([])
            ranked_clusters.append([])
            clusters_summaries.append([])
            clusters_based_responses.append([])
            if baseline:
                passages_summary_zero_shot.append([])
        else:
            if len(query_information_nuggets) >= 4:
                clusters = clusterer.cluster(query_information_nuggets)
                information_nugget_clusters = []
                for cluster_id in list(set(clusters["Topic"])):
                    cluster_docs = list(
                        clusters[clusters["Topic"] == cluster_id]["Document"]
                    )
                    doc = ScoredDocument(
                        cluster_id, "; ".join(cluster_docs), len(cluster_docs)
                    )
                    information_nugget_clusters.append(doc)
            else:
                information_nugget_clusters = []
                for cluster_id in range(0, len(query_information_nuggets)):
                    doc = ScoredDocument(
                        cluster_id, query_information_nuggets[cluster_id]
                    )
                    information_nugget_clusters.append(doc)

            retrieved_clusters.append(
                [
                    (cluster.doc_id, cluster.content)
                    for cluster in information_nugget_clusters
                ]
            )

            information_nuggets_ranking = Ranking(
                query_id=query_id, scored_docs=information_nugget_clusters
            )
            clusters_ranking = ranker.rerank(
                Query(query_id, query),
                information_nuggets_ranking,
                len(clusters),
            )
            clusters_ranking_docs = clusters_ranking.documents()
            ranked_clusters.append(
                [
                    (cluster_id, cluster_content)
                    for cluster_id, cluster_content in zip(
                        clusters_ranking_docs[0], clusters_ranking_docs[1]
                    )
                ]
            )

            prompt_snippets = [
                {
                    "role": "system",
                    "content": "Summarize the provided information that answers the query into a single sentence (approximately 20 words). Generate one-sentence long summary that is short, concise and only contains the information that answers the query.",
                },
            ]

            support_passage = {}

            summaries = []
            length_limit_reached = False
            for cluster_id, cluster_content in zip(
                clusters_ranking_docs[0], clusters_ranking_docs[1]
            ):
                if not length_limit_reached:
                    cluster_summary = summarizer.summarize_passages(
                        query=query,
                        passages=cluster_content,
                        prompt=prompt_snippets,
                        max_length=1000,
                    )
                    summaries.append(cluster_summary)
        
                    response_till_now = " ".join(summaries)

                    if len(response_till_now.split()) > 400 or len(summaries) > res_length_limit:
                        summaries = summaries[:-1]
                        length_limit_reached = True
                    else:
                        support_passage[cluster_content] = []
                        for doc_id, nuggets in information_nuggets_per_doc.items():
                            if any(nugget in cluster_content for nugget in nuggets):
                                support_passage[cluster_content].append(doc_id)

            response = ""      
            for summary, sup_passages in zip(summaries, support_passage.values()):
                response += summary +  " " + str(sup_passages) + " "
            responses.append(response)

            source = []
            for s_ps in support_passage.values():
                source.extend(s_ps)
            source = list(set(source))
            sources_ids.append(source)
            sources.append(["[" + str(i) + "] " + passages[i-1] for i in source])
            
            if len(clusters_ranking_docs[1]) >= 4:
                following_clusters.append(clusters_ranking_docs[1][3])
            elif len(clusters_ranking_docs[1]) == 3:
                following_clusters.append("all clusters used")
            else:
                following_clusters.append("fewer than 3 clusters found")
            clusters_summaries.append(summaries)
            clusters_based_responses.append(" ".join(summaries[:res_length_limit]))
            support_passages.append(support_passage)

            prompt_top_cluster = [
                {
                    "role": "system",
                    "content": "Generate the answer to a query that is 3 sentences long (approximately 100 words in total) using the provided information. Use only the provided information. You can expand the provided information but do not add any additional information.",
                },
            ]
            single_aspect_response = summarizer.summarize_passages(
                query=query,
                passages=clusters_ranking_docs[1][0],
                prompt=prompt_top_cluster,
                max_length=1000,
            )
            single_aspect_responses.append(single_aspect_response)
            remaining_clusters.append(clusters_ranking_docs[1][:1])

            prompt_main_aspect_extraction = [
                {
                    "role": "system",
                    "content": "You are provided with some relevant information to answer the question. Extract from this relevant information the most important aspect to be discussed in an answer to this query. Provide this aspect in a keyword form.",
                },
            ]
            additional_aspect = summarizer.summarize_aspects(
                query=query,
                passages=" ".join(clusters_ranking_docs[1][:1]),
                prompt=prompt_main_aspect_extraction,
                max_length=1000,
            )
            additional_aspects.append(additional_aspect)
            
            if baseline:
                prompt_passages_zero_shot = [
                    {
                        "role": "system",
                        "content": "Answer the query in 3 sentences (approximately 100 words in total).",
                    },
                ]

                passages_summary_zero_shot.append(
                    summarizer.summarize_passages(
                        query=query,
                        passages="".join(passages),
                        prompt=prompt_passages_zero_shot,
                        max_length=1000,
                    )
                )
        
        data_so_far["query_id"] = queries_ids
        data_so_far["query"] = queries
        data_so_far["passage_id"] = passages_used_ids
        data_so_far["passage"] = passages_used
        data_so_far["information_nuggets"] = information_nuggets
        data_so_far["clusters"] = retrieved_clusters
        data_so_far["ranked_clusters"] = ranked_clusters
        data_so_far["clusters_summaries"] = clusters_summaries
        data_so_far["clusters_based_response"] = clusters_based_responses
        data_so_far["ginger_response"] = responses
        data_so_far["support_passages"] = support_passages
        data_so_far["source_ids"] = sources_ids
        data_so_far["source"] = sources
        data_so_far["following_clusters"] = following_clusters
        data_so_far["single_aspect_responses"] = single_aspect_responses
        data_so_far["remaining_clusters"] = remaining_clusters
        data_so_far["additional_aspects"] = additional_aspects
        if baseline:
            data_so_far["baseline_zero_shot"] = passages_summary_zero_shot
        
        top_n = 3
        data_so_far.to_csv("res_" + ginger_version + "_top_+ " + str(top_n) + "-" + str(res_length_limit) + "_sentences_max" + "-output.csv",index=False)

    rephrased_ginger_responses =  rephrase_response(
        data_so_far, "clusters_based_response", summarizer
    )
    data_so_far["rephrased_clusters_based_response"] = rephrased_ginger_responses
    rephrased_ginger_responses_sup = []
    for res, sup_pas in zip(rephrased_ginger_responses, support_passages):
        rep_res = ""
        for res_sent, s in zip(tokenize.sent_tokenize(res), sup_pas.values()):
            rep_res += res_sent + " " + str(s) + " "
        rephrased_ginger_responses_sup.append(rep_res)
    data_so_far["rephrased_ginger_responses"] = rephrased_ginger_responses_sup
    data_so_far.to_csv("data/generated_responses/ginger_responses.csv",index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate responses for TREC-RAG queries')
    parser.add_argument('--res_length_limit', type=int, help='Maximum length of the response in sentences. Use 100 if you want to limit the response to 400 words.')
    parser.add_argument('--baseline', action='store_true', help='Whether to generate baseline responses')

    args = parser.parse_args()

    main(res_length_limit=3, baseline=True)