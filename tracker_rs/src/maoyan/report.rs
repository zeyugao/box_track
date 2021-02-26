use std::collections::HashMap;
use serde_json::Value;
use regex::Regex;
use super::api_struct::MaoyanBoxStruct;
use std::str::FromStr;

fn parse_percent(percent: &str) -> &str {
    let end = if percent.ends_with("%") { percent.len() - 1 } else { percent.len() };
    let start = if percent.starts_with("<") { 1 } else { 0 };
    &percent[start..end]
}

fn unit_to_num(unit: &str) -> f64 {
    match unit {
        "亿" => 1_0000_0000.0,
        "万" => 1_0000.0,
        _ => 1.0
    }
}

fn parse_box_sum(raw_box_sum: &str) -> f64 {
    let re = Regex::new(r"([0-9.]+)([亿|万]?)").unwrap();
    let res = re.captures(raw_box_sum).unwrap();
    let num: f64 = res.get(2).unwrap().as_str().parse().unwrap();

    num * unit_to_num(res.get(3).unwrap().as_str())
}

pub async fn report(data: MaoyanBoxStruct) -> Result<(), &'static str> {
    if !data.status {
        return Err("status is false");
    }
    let data = data.box_office;
    if !data.success {
        return Err("success is false");
    }
    let data = data.data;

    let time = data.update_info.update_timestamp; // ms
    let national_box = f64::from_str(&data.national_box.num).unwrap() * unit_to_num(&data.national_box.unit);

    Ok(())
}