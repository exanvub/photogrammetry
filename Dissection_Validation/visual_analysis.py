"""
Visual Inspection VAS Analysis
==============================
Statistical analysis of Visual Analog Scale (VAS) scoring data from 6 researchers
evaluating 6 photogrammetry models across 7 quality topics.

Models:
    M1: CP-RS, M2: iPhone-RS, M3: DL-OC, M4: iPhone-OC, M5: DL-RS, M6: CP-OC

Topics:
    Detail, Most realistic, Muscle, Arteries, Nerves, Bone, Overall

Statistical analyses:
    - Descriptive statistics (median, IQR, mean, std)
    - Friedman test (non-parametric repeated measures)
    - Post-hoc pairwise Wilcoxon signed-rank tests (Bonferroni corrected)
    - Kendall's W (inter-rater concordance)
    - Rank analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
from itertools import combinations

MODEL_MAP = {
    "M1": "CP-RS",
    "M2": "iPhone-RS",
    "M3": "DL-OC",
    "M4": "iPhone-OC",
    "M5": "DL-RS",
    "M6": "CP-OC",
}

TOPICS = ["Detail", "Realistic", "Muscle", "Artries", "Nerves", "Bone", "Overall"]
TOPIC_DISPLAY = {
    "Detail": "Detail",
    "Realistic": "Most Realistic",
    "Muscle": "Muscle",
    "Artries": "Arteries",
    "Nerves": "Nerves",
    "Bone": "Bone",
    "Overall": "Overall",
}
MODELS = ["M1", "M2", "M3", "M4", "M5", "M6"]
RESEARCHERS = ["R1", "R2", "R3", "R4", "R5", "R6"]


def load_vas_data(excel_path: str) -> pd.DataFrame:
    """
    Load VAS data from Excel file and reshape into long format.

    Each topic block occupies 7 columns: [TopicLabel, M1, M2, M3, M4, M5, M6].
    Rows 1–6 are researchers R1–R6.

    Args:
        excel_path: Path to the Visual_Inspection_VAS.xlsx file

    Returns:
        Long-format DataFrame with columns [Researcher, Topic, Model, Score]
    """
    df_raw = pd.read_excel(excel_path, header=None)

    records: List[Dict] = []

    for topic_idx, topic_key in enumerate(TOPICS):
        col_start = topic_idx * 7  # topic label column
        score_cols = list(range(col_start + 1, col_start + 7))  # M1–M6

        for row_idx in range(1, 7):  # rows 1–6 are R1–R6
            researcher = str(df_raw.iloc[row_idx, col_start])
            for model_offset, model_key in enumerate(MODELS):
                score = float(df_raw.iloc[row_idx, score_cols[model_offset]])
                records.append({
                    "Researcher": researcher,
                    "Topic": TOPIC_DISPLAY[topic_key],
                    "Model": MODEL_MAP[model_key],
                    "Score": score,
                })

    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} VAS observations "
          f"({len(RESEARCHERS)} researchers × {len(TOPICS)} topics × {len(MODELS)} models)")
    return df

def compute_descriptive_stats(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Compute descriptive statistics per Topic × Model.

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save CSV

    Returns:
        Summary DataFrame
    """
    summary = (
        df.groupby(["Topic", "Model"])["Score"]
        .agg(
            n="count",
            mean="mean",
            std="std",
            median="median",
            q25=lambda x: np.percentile(x, 25),
            q75=lambda x: np.percentile(x, 75),
            min="min",
            max="max",
        )
        .reset_index()
    )

    # Round numeric columns
    for col in ["mean", "std", "median", "q25", "q75", "min", "max"]:
        summary[col] = summary[col].round(2)

    print("\n" + "=" * 80)
    print("DESCRIPTIVE STATISTICS (per Topic × Model)")
    print("=" * 80)
    print(summary.to_string(index=False))
    print("=" * 80)

    summary.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return summary


def compute_rank_analysis(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Derive ranks from VAS scores per Researcher × Topic (highest score = rank 1).
    Compute mean rank and median rank per Model × Topic.

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save CSV

    Returns:
        Rank summary DataFrame
    """
    df_ranked = df.copy()
    df_ranked["Rank"] = (
        df_ranked.groupby(["Researcher", "Topic"])["Score"]
        .rank(ascending=False, method="average")
    )

    rank_summary = (
        df_ranked.groupby(["Topic", "Model"])["Rank"]
        .agg(mean_rank="mean", median_rank="median")
        .reset_index()
        .sort_values(["Topic", "mean_rank"])
    )
    rank_summary["mean_rank"] = rank_summary["mean_rank"].round(2)
    rank_summary["median_rank"] = rank_summary["median_rank"].round(1)

    print("\n" + "=" * 80)
    print("RANK ANALYSIS (rank 1 = highest score)")
    print("=" * 80)
    print(rank_summary.to_string(index=False))
    print("=" * 80)

    rank_summary.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return rank_summary


# ── Friedman test ────────────────────────────────────────────────────────────

def run_friedman_tests(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Run Friedman test per topic to determine if at least one model differs.

    The Friedman test is a non-parametric alternative to repeated-measures ANOVA,
    appropriate for ordinal/bounded VAS data with a small number of raters.

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save CSV

    Returns:
        DataFrame with Friedman test results per topic
    """
    model_order = sorted(df["Model"].unique())
    results = []

    for topic in sorted(df["Topic"].unique()):
        topic_df = df[df["Topic"] == topic]

        # Build arrays per model (one value per researcher)
        arrays = []
        for model in model_order:
            scores = (
                topic_df[topic_df["Model"] == model]
                .sort_values("Researcher")["Score"]
                .values
            )
            arrays.append(scores)

        stat, p_value = stats.friedmanchisquare(*arrays)
        results.append({
            "Topic": topic,
            "Friedman_chi2": round(stat, 3),
            "p_value": round(p_value, 6),
            "Significant_0.05": p_value < 0.05,
            "n_raters": len(arrays[0]),
            "n_models": len(arrays),
        })

    results_df = pd.DataFrame(results)

    print("\n" + "=" * 80)
    print("FRIEDMAN TEST (per Topic)")
    print("=" * 80)
    print(results_df.to_string(index=False))
    print("=" * 80)

    results_df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return results_df

def run_posthoc_wilcoxon(df: pd.DataFrame, friedman_df: pd.DataFrame,
                         output_path: Path) -> pd.DataFrame:
    """
    Run pairwise Wilcoxon signed-rank tests for topics with significant
    Friedman results, with Bonferroni correction.

    Args:
        df: Long-format VAS DataFrame
        friedman_df: Friedman test results
        output_path: Path to save CSV

    Returns:
        DataFrame with pairwise comparison results
    """
    model_order = sorted(df["Model"].unique())
    pairs = list(combinations(model_order, 2))
    n_comparisons = len(pairs)  # 15

    results = []

    for _, row in friedman_df.iterrows():
        topic = row["Topic"]
        friedman_sig = row["Significant_0.05"]
        topic_df = df[df["Topic"] == topic]

        for model_a, model_b in pairs:
            scores_a = (
                topic_df[topic_df["Model"] == model_a]
                .sort_values("Researcher")["Score"]
                .values
            )
            scores_b = (
                topic_df[topic_df["Model"] == model_b]
                .sort_values("Researcher")["Score"]
                .values
            )

            diff = scores_a - scores_b

            # Wilcoxon requires at least 1 non-zero difference
            if np.all(diff == 0):
                stat, p_val = np.nan, 1.0
            else:
                try:
                    stat, p_val = stats.wilcoxon(scores_a, scores_b)
                except ValueError:
                    # Can happen if all differences are zero or n too small
                    stat, p_val = np.nan, 1.0

            p_corrected = min(p_val * n_comparisons, 1.0)

            results.append({
                "Topic": topic,
                "Model_A": model_a,
                "Model_B": model_b,
                "Median_A": round(np.median(scores_a), 2),
                "Median_B": round(np.median(scores_b), 2),
                "Wilcoxon_stat": round(stat, 3) if not np.isnan(stat) else np.nan,
                "p_value": round(p_val, 6),
                "p_corrected": round(p_corrected, 6),
                "Significant_0.05": p_corrected < 0.05,
                "Friedman_significant": friedman_sig,
            })

    results_df = pd.DataFrame(results)

    print("\n" + "=" * 80)
    print("POST-HOC PAIRWISE WILCOXON SIGNED-RANK TESTS (Bonferroni corrected)")
    print("=" * 80)
    sig_df = results_df[results_df["Significant_0.05"] & results_df["Friedman_significant"]]
    if len(sig_df) > 0:
        print(f"\nSignificant pairwise differences (p_corrected < 0.05):")
        print(sig_df.to_string(index=False))
    else:
        print("No significant pairwise differences after Bonferroni correction.")
    print("=" * 80)

    results_df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return results_df


def compute_kendalls_w(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Compute Kendall's coefficient of concordance (W) per topic.

    W measures inter-rater agreement on the ranking of models.
    W = 0: no agreement, W = 1: perfect agreement.

    Formula:
        W = 12 * S / (k^2 * n * (n^2 - 1))
    where:
        k = number of raters
        n = number of models
        S = sum of squared deviations of rank sums from their mean

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save CSV

    Returns:
        DataFrame with W values per topic
    """
    results = []

    for topic in sorted(df["Topic"].unique()):
        topic_df = df[df["Topic"] == topic]

        # Build rater × model matrix of ranks
        model_order = sorted(topic_df["Model"].unique())
        k = len(RESEARCHERS)  # number of raters
        n = len(model_order)  # number of models

        rank_matrix = np.zeros((k, n))

        for r_idx, researcher in enumerate(sorted(topic_df["Researcher"].unique())):
            scores = []
            for m_idx, model in enumerate(model_order):
                score = topic_df[
                    (topic_df["Researcher"] == researcher)
                    & (topic_df["Model"] == model)
                ]["Score"].values[0]
                scores.append(score)
            # Rank: highest score → rank 1
            rank_matrix[r_idx, :] = stats.rankdata([-s for s in scores])

        # Calculate W
        rank_sums = rank_matrix.sum(axis=0)  # sum of ranks per model
        mean_rank_sum = rank_sums.mean()
        S = np.sum((rank_sums - mean_rank_sum) ** 2)
        W = (12 * S) / (k ** 2 * n * (n ** 2 - 1))

        # Chi-square approximation for significance
        chi2 = k * (n - 1) * W
        dof = n - 1
        p_value = 1 - stats.chi2.cdf(chi2, dof)

        results.append({
            "Topic": topic,
            "Kendalls_W": round(W, 4),
            "Chi2": round(chi2, 3),
            "df": dof,
            "p_value": round(p_value, 6),
            "Significant_0.05": p_value < 0.05,
            "Interpretation": _interpret_w(W),
        })

    results_df = pd.DataFrame(results)

    print("\n" + "=" * 80)
    print("KENDALL'S W (Inter-rater Agreement per Topic)")
    print("=" * 80)
    print(results_df.to_string(index=False))
    print("=" * 80)

    results_df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return results_df


def _interpret_w(w: float) -> str:
    """Interpret Kendall's W value."""
    if w >= 0.9:
        return "Very strong"
    elif w >= 0.7:
        return "Strong"
    elif w >= 0.5:
        return "Moderate"
    elif w >= 0.3:
        return "Fair"
    else:
        return "Poor"


def create_boxplots(df: pd.DataFrame, output_folder: Path):
    """
    Create a box plot per topic showing VAS scores per model,
    with individual researcher data points overlaid.

    Args:
        df: Long-format VAS DataFrame
        output_folder: Folder to save plot PNGs
    """
    model_order = sorted(df["Model"].unique())
    topics = sorted(df["Topic"].unique())
    colors = sns.color_palette("colorblind", len(model_order))

    for topic in topics:
        topic_df = df[df["Topic"] == topic]

        fig, ax = plt.subplots(figsize=(10, 6))

        sns.boxplot(
            data=topic_df,
            x="Model",
            y="Score",
            hue="Model",
            order=model_order,
            hue_order=model_order,
            palette=colors,
            width=0.5,
            linewidth=1.5,
            legend=False,
            ax=ax,
        )
        sns.stripplot(
            data=topic_df,
            x="Model",
            y="Score",
            order=model_order,
            color="black",
            size=7,
            alpha=0.7,
            jitter=0.1,
            ax=ax,
        )

        ax.set_ylim(0, 10.5)
        ax.set_xlabel("Model", fontsize=13, fontweight="bold")
        ax.set_ylabel("VAS Score (cm)", fontsize=13, fontweight="bold")
        ax.set_title(f"VAS Scores – {topic}", fontsize=14, fontweight="bold")
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        fname = f"boxplot_{topic.replace(' ', '_').lower()}.png"
        fig.savefig(output_folder / fname, dpi=300, bbox_inches="tight")
        print(f"Saved {fname}")
        plt.close(fig)


def create_combined_boxplot(df: pd.DataFrame, output_path: Path):
    """
    Create a single figure with subplots for all 7 topics.

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save PNG
    """
    model_order = sorted(df["Model"].unique())
    topics = sorted(df["Topic"].unique())
    colors = sns.color_palette("colorblind", len(model_order))

    fig, axes = plt.subplots(2, 4, figsize=(22, 10), sharey=True)
    axes_flat = axes.flatten()

    for idx, topic in enumerate(topics):
        ax = axes_flat[idx]
        topic_df = df[df["Topic"] == topic]

        sns.boxplot(
            data=topic_df,
            x="Model",
            y="Score",
            hue="Model",
            order=model_order,
            hue_order=model_order,
            palette=colors,
            width=0.5,
            linewidth=1.2,
            legend=False,
            ax=ax,
        )
        sns.stripplot(
            data=topic_df,
            x="Model",
            y="Score",
            order=model_order,
            color="black",
            size=5,
            alpha=0.7,
            jitter=0.1,
            ax=ax,
        )

        ax.set_ylim(0, 10.5)
        ax.set_xlabel("")
        ax.set_ylabel("VAS Score (cm)" if idx % 4 == 0 else "")
        ax.set_title(topic, fontsize=12, fontweight="bold")
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", rotation=45)

    # Hide unused subplot (8th position)
    axes_flat[7].set_visible(False)

    fig.suptitle("VAS Scores by Topic and Model", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved combined boxplot to {output_path}")
    plt.close(fig)


def create_heatmap_median(df: pd.DataFrame, output_path: Path):
    """
    Create a heatmap of median VAS scores (Topics × Models).

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save PNG
    """
    pivot = (
        df.groupby(["Topic", "Model"])["Score"]
        .median()
        .unstack("Model")
    )
    # Sort models
    pivot = pivot[sorted(pivot.columns)]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="white",
        vmin=0,
        vmax=10,
        cbar_kws={"label": "Median VAS Score (cm)"},
        ax=ax,
    )
    ax.set_xlabel("Model", fontsize=13, fontweight="bold")
    ax.set_ylabel("Topic", fontsize=13, fontweight="bold")
    ax.set_title("Median VAS Scores", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved heatmap (median) to {output_path}")
    plt.close(fig)


def create_heatmap_ranks(df: pd.DataFrame, output_path: Path):
    """
    Create a heatmap of mean ranks (Topics × Models).
    Lower rank = better (rank 1 = highest VAS score).

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save PNG
    """
    df_ranked = df.copy()
    df_ranked["Rank"] = (
        df_ranked.groupby(["Researcher", "Topic"])["Score"]
        .rank(ascending=False, method="average")
    )

    pivot = (
        df_ranked.groupby(["Topic", "Model"])["Rank"]
        .mean()
        .unstack("Model")
    )
    pivot = pivot[sorted(pivot.columns)]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd_r",  # reversed: lower rank (better) = warmer color
        linewidths=0.5,
        linecolor="white",
        vmin=1,
        vmax=6,
        cbar_kws={"label": "Mean Rank (1 = best)"},
        ax=ax,
    )
    ax.set_xlabel("Model", fontsize=13, fontweight="bold")
    ax.set_ylabel("Topic", fontsize=13, fontweight="bold")
    ax.set_title("Mean Ranks across Researchers", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved heatmap (ranks) to {output_path}")
    plt.close(fig)


def create_radar_chart(df: pd.DataFrame, output_path: Path):
    """
    Create a radar chart showing the median score profile of each model
    across all topics.

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save PNG
    """
    model_order = sorted(df["Model"].unique())
    topics = sorted(df["Topic"].unique())
    colors = sns.color_palette("colorblind", len(model_order))

    # Compute median per model per topic
    pivot = (
        df.groupby(["Model", "Topic"])["Score"]
        .median()
        .unstack("Topic")
    )
    pivot = pivot[topics]  # ensure consistent order

    # Radar chart setup
    n_topics = len(topics)
    angles = np.linspace(0, 2 * np.pi, n_topics, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

    for idx, model in enumerate(model_order):
        values = pivot.loc[model].values.tolist()
        values += values[:1]  # close the polygon
        ax.plot(angles, values, "o-", linewidth=2, label=model, color=colors[idx])
        ax.fill(angles, values, alpha=0.08, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(topics, fontsize=11, fontweight="bold")
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=9)
    ax.set_title("Median VAS Score Profiles", fontsize=14, fontweight="bold", pad=25)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved radar chart to {output_path}")
    plt.close(fig)


def create_researcher_agreement_plot(df: pd.DataFrame, output_path: Path):
    """
    Create a heatmap showing each researcher's scores for each model,
    faceted by topic — useful for visually inspecting rater consistency.

    Args:
        df: Long-format VAS DataFrame
        output_path: Path to save PNG
    """
    topics = sorted(df["Topic"].unique())
    model_order = sorted(df["Model"].unique())

    fig, axes = plt.subplots(2, 4, figsize=(24, 10))
    axes_flat = axes.flatten()

    for idx, topic in enumerate(topics):
        ax = axes_flat[idx]
        topic_df = df[df["Topic"] == topic]

        pivot = topic_df.pivot(index="Researcher", columns="Model", values="Score")
        pivot = pivot[model_order]

        sns.heatmap(
            pivot,
            annot=True,
            fmt=".1f",
            cmap="YlOrRd",
            linewidths=0.5,
            linecolor="white",
            vmin=0,
            vmax=10,
            cbar=idx == len(topics) - 1,
            cbar_kws={"label": "VAS Score (cm)"} if idx == len(topics) - 1 else {},
            ax=ax,
        )
        ax.set_title(topic, fontsize=12, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("" if idx % 4 != 0 else "Researcher")

    axes_flat[7].set_visible(False)

    fig.suptitle("Individual Researcher Scores per Model", fontsize=16,
                 fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved researcher agreement plot to {output_path}")
    plt.close(fig)


def main():
    """Run the full VAS statistical analysis pipeline."""
    script_dir = Path(__file__).parent
    excel_path = script_dir / "DATA" / "Visual_Inspection_VAS.xlsx"
    output_folder = script_dir / "DATA" / "Visual_Inspection_VAS" / "analysis_results"
    output_folder.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("VISUAL INSPECTION VAS ANALYSIS")
    print("=" * 80)

    # ── 1. Load data ─────────────────────────────────────────────────────
    df = load_vas_data(str(excel_path))

    # ── 2. Descriptive statistics ────────────────────────────────────────
    desc_stats = compute_descriptive_stats(df, output_folder / "summary_statistics.csv")

    # ── 3. Rank analysis ─────────────────────────────────────────────────
    rank_summary = compute_rank_analysis(df, output_folder / "rank_summary.csv")

    # ── 4. Friedman test ─────────────────────────────────────────────────
    friedman_df = run_friedman_tests(df, output_folder / "friedman_results.csv")

    # ── 5. Post-hoc Wilcoxon ─────────────────────────────────────────────
    posthoc_df = run_posthoc_wilcoxon(df, friedman_df, output_folder / "posthoc_wilcoxon_results.csv")

    # ── 6. Kendall's W ───────────────────────────────────────────────────
    kendall_df = compute_kendalls_w(df, output_folder / "kendalls_w_results.csv")

    # ── 7. Visualizations ────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)

    create_boxplots(df, output_folder)
    create_combined_boxplot(df, output_folder / "boxplots_combined.png")
    create_heatmap_median(df, output_folder / "heatmap_median_scores.png")
    create_heatmap_ranks(df, output_folder / "heatmap_mean_ranks.png")
    create_radar_chart(df, output_folder / "radar_chart.png")
    create_researcher_agreement_plot(df, output_folder / "researcher_agreement.png")


if __name__ == "__main__":
    main()
