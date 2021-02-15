mod maoyan;
mod db;

#[tokio::main]
async fn main() {
    maoyan::work().await
}