from __future__ import annotations

from optimizer.graph_analytics.graph_bridge import GraphContext
from optimizer.graph_analytics.models import AnalyticFinding
from optimizer.graph_analytics.runners._common import (
    error_finding,
    highlight_nodes,
    nodes_of_type,
    ok_finding,
    panel_finding,
    shapley_approx,
    team_for_activity,
)


def run_h01(ctx: GraphContext) -> AnalyticFinding:
    teams = nodes_of_type(ctx, "Team")
    if not teams:
        return error_finding("H-01", "etiquetas de equipo insuficientes en el grafo")
    concentrations: dict[str, float] = {}
    for activity_id in ctx.activity_ids:
        team = team_for_activity(ctx, activity_id)
        if team is None:
            continue
        value = ctx.v_score(activity_id)
        if value <= 0:
            continue
        concentrations[team] = max(concentrations.get(team, 0.0), value)
    if not concentrations:
        return error_finding("H-01", "no hay actividades con equipo y valor asignado")
    top_team = max(concentrations, key=concentrations.get)
    return ok_finding(
        "H-01",
        scores=concentrations,
        highlight=highlight_nodes({top_team}),
        summary=f"Descubrimos concentración de conocimiento crítico en el equipo {top_team}.",
    )


def run_h02(ctx: GraphContext) -> AnalyticFinding:
    teams = nodes_of_type(ctx, "Team")
    if not teams:
        return error_finding("H-02", "etiquetas de equipo insuficientes en el grafo")
    target_team = teams[0]
    impacted: dict[str, float] = {}
    for activity_id in ctx.activity_ids:
        if team_for_activity(ctx, activity_id) != target_team:
            continue
        for metric_id in ctx.metric_ids:
            relevance = ctx.relevance(activity_id, metric_id)
            if relevance > 0:
                impacted[metric_id] = impacted.get(metric_id, 0.0) + relevance
    if not impacted:
        return error_finding("H-02", "el equipo simulado no sostiene métricas de valor")
    return ok_finding(
        "H-02",
        scores=impacted,
        highlight=highlight_nodes({target_team}),
        summary=f"Descubrimos impacto por pérdida del equipo {target_team}.",
    )


def run_h03(ctx: GraphContext) -> AnalyticFinding:
    teams = nodes_of_type(ctx, "Team")
    if not teams:
        return error_finding("H-03", "etiquetas de equipo insuficientes en el grafo")
    bridge_scores: dict[str, float] = {}
    for team_id in teams:
        count = sum(
            1
            for activity_id in ctx.activity_ids
            if team_for_activity(ctx, activity_id) == team_id
        )
        if count > 0:
            bridge_scores[team_id] = float(count)
    if not bridge_scores:
        return error_finding("H-03", "no hay equipos conectados a actividades")
    top = max(bridge_scores, key=bridge_scores.get)
    return ok_finding(
        "H-03",
        scores=bridge_scores,
        highlight=highlight_nodes({top}),
        summary=f"Descubrimos equipos puente entre flujos de valor (principal: {top}).",
    )


def run_h04(ctx: GraphContext) -> AnalyticFinding:
    capability_values = {
        activity_id: ctx.v_score(activity_id)
        for activity_id in activities_matching_hr(ctx)
    }
    scores = shapley_approx(capability_values)
    if not scores:
        return panel_finding(
            "H-04",
            detail="Valor Shapley aproximado sin datos de capacidades de RRHH.",
        )
    return panel_finding(
        "H-04",
        scores=scores,
        summary="Descubrimos la contribución marginal de capacidades de RRHH.",
    )


def activities_matching_hr(ctx: GraphContext) -> list[str]:
    from optimizer.graph_analytics.runners._common import activities_matching_area

    return activities_matching_area(ctx, "rrhh", "personas", "talento")
