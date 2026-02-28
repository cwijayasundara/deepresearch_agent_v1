use rig::completion::Prompt;
use rig::prelude::CompletionClient;
use rig::providers::openai;
use tavily::Tavily;

use crate::search::tavily_tool::parallel_search;

const TLDR_PREAMBLE: &str =
    "You are a Deep Research Analyst — providing comprehensive intelligence analysis. \
     Produce ONLY the ## TL;DR section with 3-5 bullet executive summary. \
     Do not produce any other sections.";

const EVENTS_PREAMBLE: &str =
    "You are a Deep Research Analyst — providing comprehensive intelligence analysis. \
     Produce ONLY the ## Global Viral Events section. \
     For each event use this format:\n\
     ### <Headline>\n\
     - **Category**: <category>\n\
     - **Impact Rating**: <1-10>\n\
     - **Confidence**: <high|medium|low>\n\
     - **Source**: <source URL or name>\n\
     - **Summary**: <2-3 sentence description of the event, its significance, and key details>\n\
     Do not produce any other sections.";

const DIVES_AUDIT_PREAMBLE: &str =
    "You are a Deep Research Analyst — providing comprehensive intelligence analysis. \
     Produce ONLY the ## Strategic Deep Dives and ## Completeness Audit sections. \
     For deep dives use:\n\
     ### <Title>\n\
     - **Priority**: HIGH|MEDIUM|LOW\n\
     - **Summary**: <paragraph>\n\
     - **Key Findings**\n\
     - <finding>\n\
     For completeness audit use:\n\
     - **Verified Signals**: <int>\n\
     - **Sources Checked**: <int>\n\
     - **Confidence Score**: <0.0-1.0>\n\
     - **Gaps**: <comma-separated list>\n\
     Do not produce any other sections.";

pub async fn run_research(
    client: &openai::Client,
    tavily: &Tavily,
    prompt: &str,
    search_topic: &str,
    model: &str,
) -> Result<String, String> {
    // Phase 1: Parallel search fan-out (short topic query, not the full prompt)
    let search_context = parallel_search(tavily, search_topic).await.unwrap_or_default();
    let full_prompt = format!("{prompt}\n\nSearch context:\n{search_context}");

    // Phase 2: 3 parallel LLM calls
    tracing::info!("[3/4] Starting parallel LLM analysis (3 sub-calls)...");
    let llm_start = std::time::Instant::now();

    let (tldr_res, events_res, dives_res) = tokio::join!(
        call_llm(client, model, TLDR_PREAMBLE, &full_prompt),
        call_llm(client, model, EVENTS_PREAMBLE, &full_prompt),
        call_llm(client, model, DIVES_AUDIT_PREAMBLE, &full_prompt),
    );

    let llm_duration = llm_start.elapsed().as_secs_f64();
    tracing::info!("[3/4] LLM analysis complete in {:.1}s", llm_duration);

    let tldr = tldr_res.map_err(|e| format!("TL;DR failed: {e}"))?;
    let events = events_res.map_err(|e| format!("Events failed: {e}"))?;
    let dives = dives_res.map_err(|e| format!("Dives failed: {e}"))?;

    Ok(format!("{tldr}\n\n{events}\n\n{dives}"))
}

async fn call_llm(
    client: &openai::Client,
    model: &str,
    preamble: &str,
    prompt: &str,
) -> Result<String, String> {
    let agent = client.agent(model).preamble(preamble).build();
    let result: Result<String, _> = agent.prompt(prompt).await;
    result.map_err(|e| e.to_string())
}
