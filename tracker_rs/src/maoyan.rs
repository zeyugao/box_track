mod fetch;
mod report;

pub async fn work() {
    let data = fetch::fetch_data().await.expect("Fail");
    report::report(data).await;
}