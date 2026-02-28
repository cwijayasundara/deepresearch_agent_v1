use std::sync::Arc;

use axum::extract::{Path, State};
use axum::Json;
use chrono::Utc;
use serde_json::{json, Value};

use crate::auth::middleware::AuthUser;
use crate::errors::AppError;
use crate::orchestrator::run_daily_research;
use crate::types::report::ResearchReport;
use crate::types::requests::{ReportListResponse, ResearchRequest};
use crate::AppState;

pub async fn list_reports(
    State(state): State<Arc<AppState>>,
    _user: AuthUser,
) -> Result<Json<ReportListResponse>, AppError> {
    let reports = state.repo.list_reports(20).await?;
    let total = reports.len();
    Ok(Json(ReportListResponse { reports, total }))
}

pub async fn get_report(
    State(state): State<Arc<AppState>>,
    _user: AuthUser,
    Path(report_id): Path<String>,
) -> Result<Json<ResearchReport>, AppError> {
    let report = state
        .repo
        .get_report(&report_id)
        .await?
        .ok_or_else(|| AppError::NotFound("Report not found".into()))?;
    Ok(Json(report))
}

pub async fn trigger_research(
    State(state): State<Arc<AppState>>,
    _user: AuthUser,
    Json(request): Json<ResearchRequest>,
) -> Result<Json<Value>, AppError> {
    let date = request
        .date
        .unwrap_or_else(|| Utc::now().format("%Y-%m-%d").to_string());

    tracing::info!("Research trigger requested for date={}", date);
    let report = run_daily_research(&date, &state).await?;
    tracing::info!("Research complete report_id={}", report.report_id);

    Ok(Json(
        json!({"report_id": report.report_id, "status": "triggered"}),
    ))
}
