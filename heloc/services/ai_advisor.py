from __future__ import annotations

import os
from typing import Any, Dict, Tuple

import pandas as pd


def _fmt_usd(value: float) -> str:
    return f"${value:,.2f}"


def _fmt_pct(value: float) -> str:
    return f"{value:.2%}"


def build_rule_based_explanation(summary: Dict[str, Any]) -> str:
    affordability = summary["affordability"]
    risk = summary["risk"]
    ltv = summary["ltv"]
    cltv = summary["cltv"]
    scenario = summary["scenario"]

    affordability_note = "affordable" if affordability <= 0.20 else "moderate" if affordability <= 0.35 else "stretched"
    leverage_note = "healthy" if cltv <= 0.80 else "elevated"

    return (
        f"Your payment-to-income ratio is about {affordability:.1%}, which looks {affordability_note}. "
        f"Risk score is {risk['score']:.1f}/100 ({risk['level']}). "
        f"LTV is {ltv:.1%} and CLTV is {cltv:.1%}, indicating {leverage_note} leverage. "
        f"In scenario testing, {scenario['best_name']} has the lowest projected total repayment, "
        f"about {_fmt_usd(abs(scenario['delta_vs_current']))} {scenario['direction']} than your current HELOC baseline. "
        "To reduce cost or risk, consider lowering borrowed amount, shortening term, making extra principal payments, "
        "or waiting for a better rate before drawing more funds."
    )


def _build_prompt(summary: Dict[str, Any]) -> str:
    risk = summary["risk"]
    scenario = summary["scenario"]
    return (
        "Write a concise plain-English explanation in 5 bullet points for a HELOC planning dashboard. "
        "Do not give financial advice; educational only. Do not mention personal identifying info. "
        "Cover affordability, risk score, LTV/CLTV, scenario comparison, and ways to reduce cost/risk.\n\n"
        f"Affordability ratio: {summary['affordability']:.3f}\n"
        f"Risk score: {risk['score']:.1f}\n"
        f"Risk level: {risk['level']}\n"
        f"LTV: {summary['ltv']:.4f}\n"
        f"CLTV: {summary['cltv']:.4f}\n"
        f"Best scenario: {scenario['best_name']}\n"
        f"Delta vs current repayment: {scenario['delta_vs_current']:.2f} ({scenario['direction']})\n"
    )


def get_ai_financial_explanation(summary: Dict[str, Any]) -> Tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "AI explanation is unavailable because OPENAI_API_KEY is not set. Showing a rule-based summary instead.",
            build_rule_based_explanation(summary),
        )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "You are a cautious educational finance explainer. Never provide financial advice.",
                },
                {"role": "user", "content": _build_prompt(summary)},
            ],
            max_output_tokens=220,
            temperature=0.3,
        )
        text = (resp.output_text or "").strip()
        if not text:
            raise ValueError("Empty AI response")
        return ("AI-generated educational explanation.", text)
    except Exception:
        return (
            "AI explanation is temporarily unavailable. Showing a rule-based summary instead.",
            build_rule_based_explanation(summary),
        )


def build_explanation_summary(*, monthly_payment: float, monthly_income: float, ltv: float, cltv: float, risk: Dict[str, Any], scenario_df: pd.DataFrame) -> Dict[str, Any]:
    affordability = (monthly_payment / monthly_income) if monthly_income > 0 else 0.0
    base = scenario_df[scenario_df["Scenario"] == "Current HELOC"].iloc[0]
    best = scenario_df.sort_values("Total Repayment").iloc[0]
    delta = float(best["Total Repayment"] - base["Total Repayment"])
    return {
        "affordability": affordability,
        "ltv": ltv,
        "cltv": cltv,
        "risk": risk,
        "scenario": {
            "best_name": str(best["Scenario"]),
            "delta_vs_current": delta,
            "direction": "lower" if delta < 0 else "higher",
        },
    }
