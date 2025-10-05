import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


plt.rcParams.update({'font.size': 20})

df = pd.read_csv("data/user_study/output_processed.csv", sep=";")
df = df.drop(columns=["queries", "reliable_response_ids","reliable_responses","unreliable_response_ids","unreliable_responses","trust_scores","justifications","aspect_scores"])
df["trust_preferences"] = [x.replace("Trust more", "Trust") for x in list(df["trust_preferences"])]

trust_order = [
    "Trust reliable response a lot more",
    "Trust reliable response slightly more",
    "Trust both responses about the same",
    "Trust unreliable response slightly more",
    "Trust unreliable response a lot more"
]

df["trust_preferences"] = pd.Categorical(df["trust_preferences"], categories=trust_order, ordered=True)

# Collapse TRUE/FALSE into nice labels
df["explanation_shown_lst"] = df["explanation_shown_lst"].astype(str).str.strip().str.upper().map({"TRUE": "Shown", "FALSE": "Not shown"})
df["explanation_type_lst"] = df["explanation_type_lst"].astype(str).map({"information_coverage": "Information Coverage", "grounding": "Grounding", "source_attribution": "Source attribution"})

counts = df.groupby(["explanation_type_lst", "explanation_shown_lst", "trust_preferences"]).size().reset_index(name="count")
# Normalize within each (type, shown) group
counts["proportion"] = counts.groupby(["explanation_type_lst", "explanation_shown_lst"])["count"].transform(lambda x: x / x.sum())
print(counts)

# Pivot for stacked bar
pivot_df = counts.pivot_table(index=["explanation_type_lst", "explanation_shown_lst"],
                              columns="trust_preferences",
                              values="proportion",
                              fill_value=0)

pivot_df = pivot_df.reset_index()
pivot_df["row_label"] = pivot_df["explanation_type_lst"] + " — " + pivot_df["explanation_shown_lst"]
ax = pivot_df.set_index("row_label").plot(kind="barh", stacked=True, figsize=(16,10), colormap="coolwarm")
print(pivot_df)
pivot_df.to_csv("stats_2.csv", sep=";")

plt.xlabel("Proportion", fontsize=20)
plt.title("Distribution of Trust Scores", fontsize=24)
plt.legend(title="Trust scores", ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=16, title_fontsize=18)

ax.set_yticks(range(len(pivot_df)))
ax.set_yticklabels(pivot_df["explanation_type_lst"], fontsize=20)
ax.set_ylabel("Explanation type", fontsize=20)

# Right y-axis: explanation shown labels
ax2 = ax.twinx()
ax2.set_ylim(ax.get_ylim())
ax2.set_yticks(range(len(pivot_df)))
ax2.set_yticklabels(pivot_df["explanation_shown_lst"], fontsize=20)
ax2.set_ylabel("Explanation presentation", fontsize=20)

plt.tight_layout()
plt.savefig('trust_scores_distribution.pdf')
plt.show()