import os
import pandas as pd
import plotly.express as px
import dash
from dash import Input, Output, dcc, html

# 1. Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Fan Experience Explorer"

# 2. Expose the underlying Flask server for Render/Gunicorn
server = app.server

THEME_COLUMNS = [
    "Parking and transportation", "Entry and wayfinding", "Food and beverage",
    "Queues and wait times", "Restrooms", "Staff and service",
    "Affordability and value", "Fan atmosphere and connection"
]
SENTIMENT_COLORS = {"Positive": "#C39E6D", "Neutral": "#777777", "Negative": "#E31837"}

def load_data():
    try:
        # Use your local path, but fall back to "data" if running on Render
        local_path = "/Users/franksilva/Documents/fan-experience-app"
        base_dir = local_path if os.path.exists(local_path) else "data"
        
        analysis = pd.read_csv(os.path.join(base_dir, "fan_experience_analysis.csv"))
        kpis = pd.read_csv(os.path.join(base_dir, "fan_experience_kpis.csv"))
        feedback_with_sentiment = pd.read_csv(os.path.join(base_dir, "fan_feedback_with_sentiment.csv"))
        sentiment_by_segment = pd.read_csv(os.path.join(base_dir, "sentiment_by_seating_segment.csv"))
        theme_sentiment = pd.read_csv(os.path.join(base_dir, "theme_sentiment_summary.csv"))
        theme_seating_sentiment = pd.read_csv(os.path.join(base_dir, "theme_seating_sentiment_summary.csv"))
        return analysis, kpis, feedback_with_sentiment, sentiment_by_segment, theme_sentiment, theme_seating_sentiment, None
    except Exception as exc:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), f"Data could not be loaded. Error: {str(exc)}"


analysis_df, kpis_df, feedback_sentiment_df, sentiment_segment_df, theme_sentiment_df, theme_seating_sentiment_df, load_error = load_data()
segments = sorted(analysis_df["seating_segment"].dropna().unique()) if "seating_segment" in analysis_df else []
segment_order = (analysis_df["seating_segment"].fillna("Unspecified").value_counts().index.tolist() if "seating_segment" in analysis_df else [])
theme_patterns = sorted(theme_sentiment_df["theme_pattern"].dropna().unique()) if "theme_pattern" in theme_sentiment_df else []

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Fan Experience Explorer", style={"marginBottom": "4px", "color": "#C39E6D", "letterSpacing": "1px"}),
            html.P("Explore fan feedback, experience themes, and spending patterns.", style={"marginTop": "0", "color": "#FFFFFF"}),
        ]),
        html.Img(src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Los_Angeles_Football_Club.svg/960px-Los_Angeles_Football_Club.svg.png", alt="Los Angeles Football Club logo", style={"height": "88px", "width": "auto", "objectFit": "contain"}),
    ], style={"padding": "18px 32px", "backgroundColor": "#000000", "borderBottom": "4px solid #C39E6D", "display": "flex", "alignItems": "center", "justifyContent": "space-between", "gap": "24px"}),
    html.Div(id="load-error", children=(html.Div([html.B("Data could not be loaded: "), load_error], style={"color": "#E31837", "padding": "12px", "background": "#fff1f1"}) if load_error else None)),
    dcc.Tabs([
        dcc.Tab(label="Overview", children=html.Div([
            html.Div([
                html.Div([html.Label("Seating segment", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="segment-filter", options=[{"label": "All segments", "value": "All"}] + [{"label": x, "value": x} for x in segments], value="All", clearable=False)], style={"minWidth": "240px", "flex": "1"}),
                html.Div([html.Label("LAFC membership", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="overview-member-filter", options=[{"label": "All fan responses", "value": "All"}, {"label": "LAFC members", "value": "YES"}, {"label": "Non-members", "value": "NO"}], value="All", clearable=False)], style={"minWidth": "240px", "flex": "1"}),
            ], style={"display": "flex", "flexWrap": "wrap", "gap": "16px", "padding": "18px", "marginBottom": "20px", "background": "#FAFAFA", "border": "1px solid #E0D3C3", "borderLeft": "4px solid #C39E6D", "borderRadius": "4px"}),
            html.Div(id="kpi-cards", style={"display": "grid", "gridTemplateColumns": "repeat(4, minmax(0, 1fr))", "gap": "16px", "width": "100%"}),
            html.Div([dcc.Graph(id="theme-chart", style={"flex": "1", "minWidth": "400px"}), dcc.Graph(id="spend-distribution-chart", style={"flex": "1", "minWidth": "400px"})], style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginTop": "18px"}),
            html.Div([
                html.Label("Seating segment", style={"fontWeight": "bold", "fontSize": "13px", "marginRight": "12px"}),
                dcc.RadioItems(
                    id="spend-sentiment-segment-toggle",
                    options=[{"label": "All segments", "value": "All"}] + [{"label": x, "value": x} for x in segments],
                    value="All",
                    inline=True,
                    labelStyle={"display": "inline-block", "marginRight": "14px", "cursor": "pointer"},
                ),
            ], style={"marginTop": "24px", "padding": "12px", "background": "#FAFAFA", "borderLeft": "4px solid #C39E6D"}),
            dcc.Graph(id="spend-by-sentiment-chart", style={"marginTop": "8px"}),
        ], style={"padding": "24px 32px"})),
        dcc.Tab(label="Segment Comparison", children=html.Div([
            html.H2("Segment Comparison", style={"color": "#000000"}),
            html.P("Compare fan feedback rates, reported spending, and the count and percentage breakdown of positive, neutral, and negative survey sentiment by seating segment.", style={"color": "#555"}),
            html.Div([html.Label("LAFC membership", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="comparison-member-filter", options=[{"label": "All fan responses", "value": "All"}, {"label": "LAFC members", "value": "YES"}, {"label": "Non-members", "value": "NO"}], value="All", clearable=False)], style={"maxWidth": "360px", "margin": "16px 0"}),
            dcc.Graph(id="sentiment-comparison-chart"), dcc.Graph(id="sentiment-percentage-chart"), dcc.Graph(id="segment-comparison-chart"),
        ], style={"padding": "24px 32px"})),
        dcc.Tab(label="Theme Patterns", children=html.Div([
            html.H2("Theme Pattern Sentiment", style={"color": "#000000"}),
            html.P("Identify the themes with the most frequent and highest-percentage positive, neutral, and negative responses, then compare each theme across seating locations.", style={"color": "#555"}),
            html.Div([
                html.Div([html.Label("LAFC membership", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="theme-member-filter", options=[{"label": "All fan responses", "value": "All"}, {"label": "LAFC members", "value": "YES"}, {"label": "Non-members", "value": "NO"}], value="All", clearable=False)], style={"minWidth": "240px", "flex": "1"}),
                html.Div([html.Label("Theme pattern", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="theme-pattern-filter", options=[{"label": "All theme patterns", "value": "All"}] + [{"label": theme, "value": theme} for theme in theme_patterns], value="All", clearable=False)], style={"minWidth": "240px", "flex": "1"}),
            ], style={"display": "flex", "flexWrap": "wrap", "gap": "16px", "marginTop": "12px"}),
            dcc.Graph(id="theme-sentiment-count-chart"), dcc.Graph(id="theme-sentiment-percentage-chart"), dcc.Graph(id="theme-seating-sentiment-chart"),
        ], style={"padding": "24px 32px"})),
        dcc.Tab(label="Feedback Explorer", children=html.Div([
            html.H2("Feedback Explorer", style={"color": "#000000"}),
            html.P("Filter recent fan comments by seating segment, theme, and sentiment.", style={"color": "#555"}),
            html.Div([
                html.Div([html.Label("Seating segment", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="feedback-segment-filter", options=[{"label": "All seating segments", "value": "All"}] + [{"label": x, "value": x} for x in segments], value="All", clearable=False)], style={"minWidth": "200px", "flex": "1"}),
                html.Div([html.Label("Feedback theme", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="feedback-theme-filter", options=[{"label": "All themes", "value": "All"}] + [{"label": theme, "value": theme} for theme in THEME_COLUMNS] + [{"label": "Other / unclassified", "value": "Other / unclassified"}], value="All", clearable=False)], style={"minWidth": "200px", "flex": "1"}),
                html.Div([html.Label("Sentiment", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="feedback-sentiment-filter", options=[{"label": "All sentiments", "value": "All"}, {"label": "Positive", "value": "positive"}, {"label": "Neutral", "value": "neutral"}, {"label": "Negative", "value": "negative"}], value="All", clearable=False)], style={"minWidth": "180px", "flex": "1"}),
                html.Div([html.Label("LAFC membership", style={"fontWeight": "bold", "fontSize": "13px"}), dcc.Dropdown(id="feedback-member-filter", options=[{"label": "All fan responses", "value": "All"}, {"label": "LAFC members", "value": "YES"}, {"label": "Non-members", "value": "NO"}], value="All", clearable=False)], style={"minWidth": "180px", "flex": "1"}),
            ], style={"display": "flex", "flexWrap": "wrap", "gap": "16px", "padding": "18px", "margin": "16px 0 24px", "background": "#FAFAFA", "border": "1px solid #E0D3C3", "borderLeft": "4px solid #C39E6D", "borderRadius": "4px"}),

            html.Div(id="explorer-feedback-list"),
        ], style={"padding": "24px 32px"})),
    ], style={"fontFamily": "Neutraface, 'Arial Narrow', Arial, sans-serif"}),
])


def card(label, value, note):
    return html.Div([html.Div(label, style={"fontSize": "13px", "color": "#555"}), html.Div(value, style={"fontSize": "28px", "fontWeight": "bold", "margin": "6px 0", "color": "#000000"}), html.Div(note, style={"fontSize": "12px", "color": "#555"})], style={"background": "#fff", "border": "1px solid #C39E6D", "padding": "16px", "minWidth": "0", "width": "100%", "boxSizing": "border-box", "boxShadow": "0 1px 2px #ddd"})


def chart_style(figure, bottom=70):
    figure.update_layout(margin=dict(l=10, r=10, t=50, b=bottom), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font={"family": "Neutraface, Arial, sans-serif", "color": "#000000"})
    return figure


@app.callback(
    Output("kpi-cards", "children"), Output("theme-chart", "figure"), Output("spend-distribution-chart", "figure"), Output("spend-by-sentiment-chart", "figure"), Output("explorer-feedback-list", "children"), Output("sentiment-comparison-chart", "figure"), Output("sentiment-percentage-chart", "figure"), Output("segment-comparison-chart", "figure"), Output("theme-sentiment-count-chart", "figure"), Output("theme-sentiment-percentage-chart", "figure"), Output("theme-seating-sentiment-chart", "figure"),
    Input("segment-filter", "value"), Input("overview-member-filter", "value"), Input("spend-sentiment-segment-toggle", "value"), Input("feedback-segment-filter", "value"), Input("feedback-theme-filter", "value"), Input("feedback-sentiment-filter", "value"), Input("feedback-member-filter", "value"), Input("comparison-member-filter", "value"), Input("theme-member-filter", "value"), Input("theme-pattern-filter", "value")
)
def update_dashboard(segment, overview_member, spend_sentiment_segment, explorer_segment, explorer_theme, explorer_sentiment, explorer_member, comparison_member, theme_member, selected_pattern):
    empty = px.bar(title="No data available")
    if analysis_df.empty:
        return [], empty, empty, empty, [], empty, empty, empty, empty, empty, empty

    data = analysis_df.copy()
    if segment != "All": data = data[data["seating_segment"] == segment]
    if overview_member != "All" and "member_segment" in data: data = data[data["member_segment"].fillna("").astype(str).str.upper() == overview_member]
    feedback_count = int(data["has_feedback"].fillna(False).astype(bool).sum())
    valid_spend = pd.to_numeric(data["total_spend"], errors="coerce").dropna()
    response_count = len(data)
    cards = [card("Responses", f"{response_count:,}", "survey responses"), card("Feedback rate", f"{feedback_count / response_count:.1%}" if response_count else "0.0%", f"{feedback_count:,} comments"), card("Average spend", f"${valid_spend.mean():,.0f}" if not valid_spend.empty else "—", f"{len(valid_spend):,} reported values"), card("Median spend", f"${valid_spend.median():,.0f}" if not valid_spend.empty else "—", "reported values only")]

    theme_counts = data["primary_theme"].fillna("Other / unclassified").value_counts().reset_index()
    theme_counts.columns = ["Theme", "Feedback"]
    theme_fig = px.bar(theme_counts.sort_values("Feedback"), x="Feedback", y="Theme", orientation="h", title="Feedback themes", color_discrete_sequence=["#C39E6D"])
    chart_style(theme_fig, 10)
    theme_fig.update_traces(hovertemplate="%{y}: %{x}<extra></extra>")

    if overview_member == "All" and not sentiment_segment_df.empty:
        spend_source = sentiment_segment_df.copy()
        if segment != "All":
            spend_source = spend_source[spend_source["seating_segment"].fillna("Unspecified") == segment]
        spend_source["total_spend_avg"] = pd.to_numeric(spend_source["total_spend_avg"], errors="coerce")
        spend_source["count"] = pd.to_numeric(spend_source["count"], errors="coerce")
        spend_source = spend_source.dropna(subset=["total_spend_avg", "count"])
        spend_source["weighted_spend"] = spend_source["total_spend_avg"] * spend_source["count"]
        overview_member_spend = spend_source.groupby("seating_segment", dropna=False).agg(weighted_spend=("weighted_spend", "sum"), response_count=("count", "sum")).reset_index()
        overview_member_spend["total_spend_num"] = overview_member_spend["weighted_spend"] / overview_member_spend["response_count"]
    else:
        overview_member_spend = data.copy()
        overview_member_spend["total_spend_num"] = pd.to_numeric(overview_member_spend["total_spend"], errors="coerce")
        overview_member_spend = overview_member_spend.groupby("seating_segment", dropna=False)["total_spend_num"].mean().reset_index()
    overview_member_spend["seating_segment"] = overview_member_spend["seating_segment"].fillna("Unspecified")
    overview_spend_order = [x for x in segment_order if x in overview_member_spend["seating_segment"].tolist()]
    spend_fig = px.bar(overview_member_spend, x="seating_segment", y="total_spend_num", title="Average total spend by seating segment", labels={"seating_segment": "Seating segment", "total_spend_num": "Average total spend ($)"}, color_discrete_sequence=["#C39E6D"], category_orders={"seating_segment": overview_spend_order})
    chart_style(spend_fig, 10)

    spend_by_sentiment = sentiment_segment_df.copy()
    if spend_sentiment_segment != "All":
        spend_by_sentiment = spend_by_sentiment[spend_by_sentiment["seating_segment"].fillna("Unspecified") == spend_sentiment_segment]
    spend_by_sentiment["total_spend_avg"] = pd.to_numeric(spend_by_sentiment["total_spend_avg"], errors="coerce")
    spend_by_sentiment = spend_by_sentiment.dropna(subset=["sentiment", "total_spend_avg"])
    spend_by_sentiment["sentiment"] = spend_by_sentiment["sentiment"].astype(str).str.title()
    spend_by_sentiment = spend_by_sentiment.groupby("sentiment", as_index=False)["total_spend_avg"].mean()
    spend_by_sentiment["sentiment"] = pd.Categorical(spend_by_sentiment["sentiment"], categories=["Positive", "Neutral", "Negative"], ordered=True)
    spend_by_sentiment = spend_by_sentiment.sort_values("sentiment")
    chart_title = "Average total spend by sentiment" if spend_sentiment_segment == "All" else f"Average total spend by sentiment — {spend_sentiment_segment}"
    spend_by_sentiment_fig = px.bar(spend_by_sentiment, x="sentiment", y="total_spend_avg", color="sentiment", title=chart_title, labels={"sentiment": "Sentiment", "total_spend_avg": "Average total spend ($)"}, color_discrete_map=SENTIMENT_COLORS)
    chart_style(spend_by_sentiment_fig, 10)
    spend_by_sentiment_fig.update_layout(showlegend=False)

    explorer_comments = feedback_sentiment_df[feedback_sentiment_df["has_feedback"].fillna(False).astype(bool)].dropna(subset=["feedback"]) if not feedback_sentiment_df.empty else pd.DataFrame()
    if not explorer_comments.empty and explorer_segment != "All": explorer_comments = explorer_comments[explorer_comments["seating_segment"].fillna("Unspecified") == explorer_segment]
    if not explorer_comments.empty and explorer_theme != "All": explorer_comments = explorer_comments[explorer_comments["primary_theme"].fillna("Other / unclassified") == explorer_theme]
    if not explorer_comments.empty and explorer_sentiment != "All": explorer_comments = explorer_comments[explorer_comments["sentiment"].fillna("unclassified") == explorer_sentiment]
    if not explorer_comments.empty and explorer_member != "All" and "member_segment" in explorer_comments: explorer_comments = explorer_comments[explorer_comments["member_segment"].fillna("").astype(str).str.upper() == explorer_member]
    explorer_feedback = [html.Div([html.Span(f"{row['seating_segment'] if pd.notna(row['seating_segment']) else 'Unspecified'} · {row['primary_theme']} · {str(row['sentiment']).title() if pd.notna(row['sentiment']) else 'Unclassified'}", style={"fontWeight": "bold", "color": "#E31837"}), html.Div(row["feedback"], style={"marginTop": "4px"})], style={"borderLeft": "4px solid #C39E6D", "padding": "12px", "marginBottom": "10px", "background": "#FAFAFA"}) for _, row in explorer_comments.head(25).iterrows()]
    if not explorer_feedback: explorer_feedback = [html.Div("No fan feedback matches these filters.", style={"color": "#555"})]

    sentiment_data = feedback_sentiment_df.copy()
    if not sentiment_data.empty:
        sentiment_data = sentiment_data[sentiment_data["has_feedback"].fillna(False).astype(bool)]
        sentiment_data = sentiment_data[sentiment_data["sentiment"].isin(["positive", "neutral", "negative"])]
        if comparison_member != "All" and "member_segment" in sentiment_data:
            sentiment_data = sentiment_data[sentiment_data["member_segment"].fillna("").astype(str).str.upper() == comparison_member]
        sentiment_data = sentiment_data.groupby(["seating_segment", "sentiment"], dropna=False).size().reset_index(name="count")
        sentiment_data["seating_segment"] = sentiment_data["seating_segment"].fillna("Unspecified")
        sentiment_data["sentiment"] = sentiment_data["sentiment"].str.title()
    chart_segments = sentiment_data["seating_segment"].unique().tolist() if not sentiment_data.empty else []
    chart_segment_order = [x for x in segment_order if x in chart_segments] + [x for x in chart_segments if x not in segment_order]
    sentiment_fig = px.bar(sentiment_data, x="seating_segment", y="count", color="sentiment", barmode="group", title="Survey sentiment frequency by seating segment", labels={"seating_segment": "Seating segment", "count": "Responses", "sentiment": "Sentiment"}, color_discrete_map=SENTIMENT_COLORS, category_orders={"seating_segment": chart_segment_order})
    chart_style(sentiment_fig)
    
    sentiment_percentages = sentiment_data.copy()
    if not sentiment_percentages.empty: sentiment_percentages["percentage"] = sentiment_percentages["count"] / sentiment_percentages.groupby("seating_segment")["count"].transform("sum")
    sentiment_percentage_fig = px.bar(sentiment_percentages, x="seating_segment", y="percentage", color="sentiment", barmode="stack", title="Survey sentiment mix by seating segment", labels={"seating_segment": "Seating segment", "percentage": "Share of classified responses", "sentiment": "Sentiment"}, color_discrete_map=SENTIMENT_COLORS, category_orders={"seating_segment": chart_segment_order})
    chart_style(sentiment_percentage_fig)
    sentiment_percentage_fig.update_yaxes(tickformat=".0%", range=[0, 1])

    comparison = analysis_df.copy()
    if comparison_member != "All" and "member_segment" in comparison:
        comparison = comparison[comparison["member_segment"].fillna("").astype(str).str.upper() == comparison_member]
    comparison["has_feedback_num"] = comparison["has_feedback"].fillna(False).astype(bool).astype(int)
    comparison["total_spend_num"] = pd.to_numeric(comparison["total_spend"], errors="coerce")
    segment_summary = comparison.groupby("seating_segment", dropna=False).agg(feedback_rate=("has_feedback_num", "mean"), average_spend=("total_spend_num", "mean")).reset_index()
    segment_summary["seating_segment"] = segment_summary["seating_segment"].fillna("Unspecified")
    segment_summary["seating_segment"] = pd.Categorical(segment_summary["seating_segment"], categories=segment_order, ordered=True)
    segment_summary = segment_summary.sort_values("seating_segment")
    comparison_fig = px.bar(segment_summary, x="seating_segment", y="feedback_rate", color="average_spend", color_continuous_scale=["#EAF5E5", "#78B159", "#1B5E20"], title="Feedback rate by seating segment", labels={"seating_segment": "Seating segment", "feedback_rate": "Feedback rate", "average_spend": "Average spend ($)"}, category_orders={"seating_segment": segment_order})
    chart_style(comparison_fig)
    comparison_fig.update_yaxes(tickformat=".0%")

    theme_data = feedback_sentiment_df.copy()
    if not theme_data.empty:
        theme_data = theme_data[theme_data["has_feedback"].fillna(False).astype(bool)]
        theme_data = theme_data[theme_data["sentiment"].isin(["positive", "neutral", "negative"])]
        if theme_member != "All" and "member_segment" in theme_data:
            theme_data = theme_data[theme_data["member_segment"].fillna("").astype(str).str.upper() == theme_member]
        theme_data["theme_pattern"] = theme_data["primary_theme"].fillna("Other / unclassified")
        if selected_pattern != "All": theme_data = theme_data[theme_data["theme_pattern"] == selected_pattern]
        theme_data = theme_data.groupby(["theme_pattern", "sentiment"], as_index=False).size().rename(columns={"size": "response_count"})
        theme_data["sentiment"] = theme_data["sentiment"].str.title()
        theme_data["sentiment_percentage"] = 100 * theme_data["response_count"] / theme_data.groupby("theme_pattern")["response_count"].transform("sum")
    theme_count_fig = px.bar(theme_data, x="theme_pattern", y="response_count", color="sentiment", barmode="group", title="Classified response frequency by theme pattern", labels={"theme_pattern": "Theme pattern", "response_count": "Responses", "sentiment": "Sentiment"}, color_discrete_map=SENTIMENT_COLORS)
    chart_style(theme_count_fig, 110)
    theme_count_fig.update_layout(xaxis_tickangle=-35)
    theme_percentage_fig = px.bar(theme_data, x="theme_pattern", y="sentiment_percentage", color="sentiment", barmode="stack", title="Sentiment mix within each theme pattern", labels={"theme_pattern": "Theme pattern", "sentiment_percentage": "Share of classified responses", "sentiment": "Sentiment"}, color_discrete_map=SENTIMENT_COLORS)
    chart_style(theme_percentage_fig, 110)
    theme_percentage_fig.update_layout(xaxis_tickangle=-35)
    theme_percentage_fig.update_yaxes(ticksuffix="%", range=[0, 100])

    seating_data = feedback_sentiment_df.copy()
    if not seating_data.empty:
        seating_data = seating_data[seating_data["has_feedback"].fillna(False).astype(bool)]
        seating_data = seating_data[seating_data["sentiment"].isin(["positive", "neutral", "negative"])]
        if theme_member != "All" and "member_segment" in seating_data:
            seating_data = seating_data[seating_data["member_segment"].fillna("").astype(str).str.upper() == theme_member]
        seating_data["theme_pattern"] = seating_data["primary_theme"].fillna("Other / unclassified")
        if selected_pattern != "All": seating_data = seating_data[seating_data["theme_pattern"] == selected_pattern]
        seating_data = seating_data.groupby(["seating_segment", "sentiment"], as_index=False).size().rename(columns={"size": "response_count"})
        seating_data["seating_segment"] = seating_data["seating_segment"].fillna("Unspecified")
        seating_data["sentiment"] = seating_data["sentiment"].str.title()
        seating_data["sentiment_percentage"] = 100 * seating_data["response_count"] / seating_data.groupby("seating_segment")["response_count"].transform("sum")
    heatmap_title = "Sentiment share by seating segment and theme pattern" if selected_pattern == "All" else f"Sentiment share by seating segment: {selected_pattern}"
    heatmap_fig = px.density_heatmap(seating_data, x="sentiment", y="seating_segment", z="sentiment_percentage", text_auto=".1f", color_continuous_scale=["#FFFFFF", "#F4EADF", "#C39E6D", "#6F4E2C"], title=heatmap_title, labels={"sentiment": "Sentiment", "seating_segment": "Seating segment", "sentiment_percentage": "Share of classified responses (%)"})
    chart_style(heatmap_fig)
    heatmap_fig.update_layout(coloraxis_colorbar_title="Share (%)")

    return cards, theme_fig, spend_fig, spend_by_sentiment_fig, explorer_feedback, sentiment_fig, sentiment_percentage_fig, comparison_fig, theme_count_fig, theme_percentage_fig, heatmap_fig


# 3. Main execution block needed for local development & Render
if __name__ == '__main__':
    # Render assigns dynamic ports via the PORT env variable
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host='0.0.0.0', port=port, debug=False)