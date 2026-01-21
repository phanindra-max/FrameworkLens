import streamlit as st
import pandas as pd

st.set_page_config(page_title="Risk and Evaluation Framework Survey", layout="wide")

SCORE_CHOICES = [
    "Not implemented",
    "Planned",
    "Partially implemented",
    "Mostly implemented",
    "Fully implemented",
    "Not applicable",
]

SCORE_MAP = {
    "Not implemented": 0,
    "Planned": 1,
    "Partially implemented": 2,
    "Mostly implemented": 3,
    "Fully implemented": 4,
}


def slug(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-")


FRAMEWORKS = {
    "NIST AI RMF": {
        "description": "Functions: Govern, Map, Measure, Manage",
        "sections": [
            {
                "name": "Govern",
                "questions": [
                    "Defined AI risk governance roles and responsibilities.",
                    "Approved AI risk policies and oversight cadence.",
                    "Documented risk appetite for AI systems.",
                ],
            },
            {
                "name": "Map",
                "questions": [
                    "Documented intended AI system purpose and context.",
                    "Identified stakeholders impacted by AI outcomes.",
                    "Tracked data sources and lineage for AI systems.",
                ],
            },
            {
                "name": "Measure",
                "questions": [
                    "Implemented bias and fairness evaluation procedures.",
                    "Conducted model performance monitoring and drift checks.",
                    "Validated data quality and representativeness.",
                ],
            },
            {
                "name": "Manage",
                "questions": [
                    "Implemented human oversight and escalation workflows.",
                    "Defined incident response for AI failures.",
                    "Maintained change management for AI models.",
                ],
            },
        ],
    },
    "COSO ERM": {
        "description": "Components aligned to strategy and performance",
        "sections": [
            {
                "name": "Governance and Culture",
                "questions": [
                    "Board or leadership oversight of enterprise risks.",
                    "Defined ethical values and accountability.",
                    "Aligned incentives with risk-aware behavior.",
                ],
            },
            {
                "name": "Strategy and Objective-Setting",
                "questions": [
                    "Risk appetite aligned to strategy.",
                    "Objectives consider risk and uncertainty.",
                    "Resource allocation reflects risk priorities.",
                ],
            },
            {
                "name": "Performance",
                "questions": [
                    "Identified and assessed key enterprise risks.",
                    "Prioritized risks using consistent criteria.",
                    "Implemented risk responses and controls.",
                ],
            },
            {
                "name": "Review and Revision",
                "questions": [
                    "Periodic review of risk posture and controls.",
                    "Adapted to internal and external changes.",
                ],
            },
            {
                "name": "Information, Communication, and Reporting",
                "questions": [
                    "Reliable risk data and reporting cadence.",
                    "Cross-functional communication of risk issues.",
                ],
            },
        ],
    },
    "GRC Tools and Practices": {
        "description": "Core GRC process capabilities",
        "sections": [
            {
                "name": "Risk Register",
                "questions": [
                    "Maintained centralized risk register.",
                    "Assigned risk owners and mitigation plans.",
                ],
            },
            {
                "name": "Control Library",
                "questions": [
                    "Documented controls mapped to risks.",
                    "Evidence collection and testing process.",
                ],
            },
            {
                "name": "Audit and Assurance",
                "questions": [
                    "Internal audit plan aligned to top risks.",
                    "Remediation tracking for audit findings.",
                ],
            },
            {
                "name": "Third-Party Risk",
                "questions": [
                    "Vendor due diligence and periodic reviews.",
                    "Contractual risk clauses for AI vendors.",
                ],
            },
            {
                "name": "Incident and Issue Management",
                "questions": [
                    "Centralized incident reporting and triage.",
                    "Root cause analysis and corrective action.",
                ],
            },
        ],
    },
}


def score_framework(framework_name: str, data: dict, responses: dict) -> dict:
    max_points = 0
    earned_points = 0
    section_scores = []

    for section in data["sections"]:
        section_max = 0
        section_earned = 0
        for idx, question in enumerate(section["questions"]):
            key = f"{slug(framework_name)}-{slug(section['name'])}-{idx}"
            selection = responses.get(key, SCORE_CHOICES[0])
            if selection == "Not applicable":
                continue
            section_max += 4
            section_earned += SCORE_MAP[selection]
        max_points += section_max
        earned_points += section_earned
        section_scores.append(
            {
                "Section": section["name"],
                "Score": section_earned,
                "Max": section_max,
                "Percent": (section_earned / section_max * 100) if section_max else 0,
            }
        )

    overall_percent = (earned_points / max_points * 100) if max_points else 0
    return {
        "overall_percent": overall_percent,
        "earned_points": earned_points,
        "max_points": max_points,
        "section_scores": section_scores,
    }


st.title("Risk and Evaluation Framework Survey")
st.caption("Assess NIST AI RMF, COSO ERM, and GRC practices with a structured questionnaire.")

st.sidebar.header("Survey Controls")
show_details = st.sidebar.checkbox("Show detailed scoring tables", value=True)
show_gaps = st.sidebar.checkbox("Show lowest scoring items", value=True)

responses = {}

tabs = st.tabs(list(FRAMEWORKS.keys()) + ["Summary"])

for tab, (framework_name, data) in zip(tabs, FRAMEWORKS.items()):
    with tab:
        st.subheader(framework_name)
        st.caption(data["description"])

        for section in data["sections"]:
            st.markdown(f"**{section['name']}**")
            for idx, question in enumerate(section["questions"]):
                key = f"{slug(framework_name)}-{slug(section['name'])}-{idx}"
                responses[key] = st.radio(
                    question,
                    SCORE_CHOICES,
                    horizontal=True,
                    key=key,
                )
            st.divider()

with tabs[-1]:
    st.subheader("Survey Results")

    results = {}
    for framework_name, data in FRAMEWORKS.items():
        results[framework_name] = score_framework(framework_name, data, responses)

    cols = st.columns(3)
    for idx, (framework_name, result) in enumerate(results.items()):
        with cols[idx]:
            st.metric(
                framework_name,
                f"{result['overall_percent']:.0f}%",
                f"{result['earned_points']}/{result['max_points']}",
            )
            st.progress(result["overall_percent"] / 100)

    overall_percent = (
        sum(r["overall_percent"] for r in results.values()) / len(results)
        if results
        else 0
    )
    st.markdown(f"**Overall readiness score:** {overall_percent:.0f}%")

    if show_details:
        st.divider()
        st.subheader("Section Scorecards")
        for framework_name, result in results.items():
            df = pd.DataFrame(result["section_scores"])
            st.markdown(f"**{framework_name}**")
            st.dataframe(df, width="stretch")

    if show_gaps:
        st.divider()
        st.subheader("Lowest Scoring Items")
        gap_items = []
        for framework_name, data in FRAMEWORKS.items():
            for section in data["sections"]:
                for idx, question in enumerate(section["questions"]):
                    key = f"{slug(framework_name)}-{slug(section['name'])}-{idx}"
                    selection = responses.get(key, SCORE_CHOICES[0])
                    if selection in ("Not implemented", "Planned", "Partially implemented"):
                        gap_items.append(
                            {
                                "Framework": framework_name,
                                "Section": section["name"],
                                "Question": question,
                                "Response": selection,
                            }
                        )

        if gap_items:
            st.dataframe(pd.DataFrame(gap_items), width="stretch")
        else:
            st.write("No gaps identified based on current responses.")
