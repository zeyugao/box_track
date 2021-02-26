mod fetch;
mod report;
mod api_struct;

pub async fn work() {
    let data = fetch::fetch_data().await.expect("Fail");
    report::report(data).await;
}