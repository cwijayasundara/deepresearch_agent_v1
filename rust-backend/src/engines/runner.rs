use chrono::Utc;
use rig::providers::openai;
use tavily::Tavily;

use crate::parser;
use crate::types::enums::ResearchStatus;
use crate::types::report::EngineResult;

use super::engine::run_research;

pub async fn run_engine(
    client: &openai::Client,
    tavily: &Tavily,
    prompt: &str,
    search_topic: &str,
    model: &str,
) -> EngineResult {
    let started_at = Utc::now();
    let start = std::time::Instant::now();

    let result = run_research(client, tavily, prompt, search_topic, model).await;

    match result {
        Ok(raw_markdown) => {
            let completed_at = Utc::now();
            let duration = start.elapsed().as_secs_f64();

            tracing::info!("[3/4] Parsing structured data from markdown...");
            let tldr = parser::parse_tldr(&raw_markdown);
            let viral_events = parser::parse_viral_events(&raw_markdown);
            let deep_dives = parser::parse_deep_dives(&raw_markdown);
            let completeness_audit = parser::parse_completeness_audit(&raw_markdown);

            tracing::info!(
                "Engine completed in {:.1}s",
                duration
            );

            EngineResult {
                status: ResearchStatus::Completed,
                raw_markdown,
                tldr,
                viral_events,
                deep_dives,
                completeness_audit,
                started_at,
                completed_at,
                duration_seconds: duration,
                error_message: None,
            }
        }
        Err(err) => {
            let completed_at = Utc::now();
            let duration = start.elapsed().as_secs_f64();

            tracing::error!("Engine failed: {}", err);

            EngineResult {
                status: ResearchStatus::Failed,
                raw_markdown: String::new(),
                tldr: None,
                viral_events: Vec::new(),
                deep_dives: Vec::new(),
                completeness_audit: None,
                started_at,
                completed_at,
                duration_seconds: duration,
                error_message: Some(err),
            }
        }
    }
}
