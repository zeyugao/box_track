use reqwest;
use reqwest::header::HeaderMap;
use std::collections::HashMap;

use serde_json::Value;

pub async fn fetch_data() -> Result<HashMap<String, Value>, Box<dyn std::error::Error>> {
    let url = "https://piaofang.maoyan.com/getBoxList?date=1&isSplit=true";
    let mut headers = HeaderMap::new();
    headers.insert("Host", "piaofang.maoyan.com".parse().unwrap());
    headers.insert("Connection", "keep-alive".parse().unwrap());
    headers.insert("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36".parse().unwrap());
    headers.insert("Accept", "*/*".parse().unwrap());
    headers.insert("Sec-Fetch-Site", "same-origin".parse().unwrap());
    headers.insert("Sec-Fetch-Mode", "cors".parse().unwrap());
    headers.insert("Sec-Fetch-Dest", "empty".parse().unwrap());
    headers.insert("Referer", "https://piaofang.maoyan.com/box-office?ver=normal".parse().unwrap());
    headers.insert("Accept-Encoding", "gzip, deflate, br".parse().unwrap());
    headers.insert("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8".parse().unwrap());
    headers.insert("Cookie", "__mta=51338902.1613271347925.1613304470840.1613307308223.8".parse().unwrap());

    let client = reqwest::Client::new();
    let resp = client.get(url).headers(headers).send().await?;
    let body = resp.json::<HashMap<String, Value>>().await?;
    Ok(body)
}
