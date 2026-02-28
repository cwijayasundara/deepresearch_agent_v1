use tavily::Tavily;

/// Fire multiple Tavily searches in parallel with different query angles,
/// merge and deduplicate results into a combined context string.
pub async fn parallel_search(client: &Tavily, base_topic: &str) -> Result<String, String> {
    let queries = vec![
        format!("{base_topic} latest news today"),
        format!("{base_topic} breakthroughs announcements"),
        format!("{base_topic} funding partnerships"),
    ];

    tracing::info!("[2/4] Starting parallel web search ({} queries)...", queries.len());
    let search_start = std::time::Instant::now();

    // Run searches concurrently using tokio::join since Tavily doesn't impl Clone
    let (r1, r2, r3) = tokio::join!(
        client.search(&queries[0]),
        client.search(&queries[1]),
        client.search(&queries[2]),
    );

    let results = vec![r1, r2, r3];
    let mut combined = Vec::new();
    let mut seen_urls = std::collections::HashSet::new();

    for result in results {
        match result {
            Ok(response) => {
                for item in response.results {
                    if seen_urls.insert(item.url.clone()) {
                        combined.push(format!(
                            "Title: {}\nURL: {}\nContent: {}\n",
                            item.title, item.url, item.content
                        ));
                    }
                }
            }
            Err(e) => {
                tracing::warn!("Tavily search failed: {}", e);
            }
        }
    }

    let search_duration = search_start.elapsed().as_secs_f64();
    tracing::info!(
        "[2/4] Web search complete — {} results collected in {:.1}s",
        combined.len(),
        search_duration
    );

    if combined.is_empty() {
        return Err("All Tavily searches failed".into());
    }

    Ok(combined.join("\n---\n"))
}
