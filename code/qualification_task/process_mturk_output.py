import pandas as pd

def main():
    data = pd.read_csv("data/qualification_task/output.csv")
    print(len(data))

    ground_truth_scores = [
        [1,0,0,1],
        [0,0,1,1],
        [1,1,1,0],
        [0,0,0,1],
        [0,1,0,1]
    ]

    workers_scores = []
    points = []
    approves = []

    for _, row in data.iterrows():
        worker_scores = []
        point = 0
        approve = ""
        for res_id in range(0, 5):
            res_scores = []
            for aspect_id in range(0, 4):
                if row["Answer.response_" + str(res_id) + "_aspects.aspect_" + str(aspect_id)] == True:
                    res_scores.append(1)
                else:
                    res_scores.append(0)
            if res_scores == ground_truth_scores[res_id]:
                point += 1
            worker_scores.append(res_scores)
        if point >= 4:
            approve = "x" 
    
        workers_scores.append(worker_scores)
        points.append(point)
        approves.append(approve)

    data["Approve"] = approves
    data["worker_scores"] = workers_scores
    data["points"] = points

    print(points)
    print(approves)

    data.to_csv("data/qualification_task/output_processed.csv", sep=";", index=False)
    

if __name__ == "__main__":
    main()