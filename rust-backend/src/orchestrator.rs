use chrono::Utc;

use crate::engines::runner::run_engine;
use crate::errors::AppError;
use crate::prompts::build_research_prompt;
use crate::types::report::ResearchReport;
use crate::AppState;

pub async fn run_daily_research(
    date: &str,
    state: &AppState,
) -> Result<ResearchReport, AppError> {
    let total_start = std::time::Instant::now();
    let report_id = format!("rpt-{date}");

    tracing::info!("[1/4] Building research prompt for {}", date);
    let prompt = build_research_prompt(date);
    let search_topic = format!("AI industry developments {date}");

    let result = run_engine(
        &state.openai_client,
        &state.tavily_client,
        &prompt,
        &search_topic,
        &state.settings.openai_model,
    )
    .await;

    tracing::info!("[4/4] Saving report {} to database", report_id);
    let now = Utc::now();
    let report = ResearchReport {
        report_id,
        run_date: now,
        result: Some(result),
        created_at: now,
    };

    state.repo.save_report(&report).await?;

    let total_duration = total_start.elapsed().as_secs_f64();
    tracing::info!(
        "Research complete: {} in {:.1}s total",
        report.report_id,
        total_duration
    );
    Ok(report)
}
