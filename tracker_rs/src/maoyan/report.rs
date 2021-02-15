use std::collections::HashMap;
use serde_json::Value;
use regex::Regex;

fn parse_percent(percent: &str) -> &str {
    let end = if percent.ends_with("%") { percent.len() - 1 } else { percent.len() };
    let start = if percent.starts_with("<") { 1 } else { 0 };
    &percent[start..end]
}

fn unit_to_num(unit: &str) -> i64 {
    match unit {
        "亿" => 1_0000_0000,
        "万" => 1_0000,
        _ => 1
    }
}

fn parse_box_sum(raw_box_sum: &str) -> i64 {
    let re = Regex::new(r"([0-9.]+)([亿|万]?)").unwrap();
    let res = re.captures(raw_box_sum).unwrap();
    let num: i64 = res.get(2).unwrap().as_str().parse().unwrap();

    num * unit_to_num(res.get(3).unwrap().as_str())
}

pub async fn report(data: HashMap<String, Value>) -> Result<(), &'static str> {
    let status = data.get("status");
    match status {
        Some(Value::Bool(true)) => {}
        _ => { return Err("status err"); }
    }

    let data = data.get("boxOffice").unwrap();

    let success = data.get("success");
    match success {
        Some(Value::Bool(true)) => {}
        _ => { return Err("success err"); }
    }

    let data = data.get("data").unwrap();
    let update_time = data.get("updateInfo").unwrap().get("updateTimestamp").unwrap();
    let national_box_num = data.get("nationalBox").unwrap().get("num").unwrap();
    let national_box_unit = data.get("nationalBox").unwrap().get("unit").unwrap();
    if let (
        Value::Number(update_time),
        Value::Number(nation_box_sum),
        Value::String(national_box_unit)
    ) = (
        update_time,
        national_box_num,
        national_box_unit
    ) {
        let nation_box = national_box_num * unit_to_num(national_box_unit);

        if let Value::Array(list) = data.get("list").unwrap() {
            let box_office = data.get("boxDesc").unwrap();
            let box_rate = data.get("boxRate").unwrap();
            let seat_count_rate = data.get("seatCountRate").unwrap();
            let show_count_rate = data.get("showCountRate").unwrap();
            let sum_box_desc = data.get("sumBoxDesc").unwrap();
            let movie_name = data.get("movie_name").unwrap().get("movieName").unwrap();

            if let (
                Value::String(box_office_str),
                Value::String(box_rate_str),
                Value::String(seat_count_rate_str),
                Value::String(show_count_rate_str),
                Value::String(sum_box_desc_str),
                Value::String(movie_name_str)
            ) = (
                box_office,
                box_rate,
                seat_count_rate,
                show_count_rate,
                sum_box_desc,
                movie_name
            ) {
                let box_office: f32 = box_office_str.parse().unwrap();
                let box_rate: f32 = parse_percent(box_rate_str).parse().unwrap();
                let seat_count_rate: f32 = parse_percent(seat_count_rate_str).parse().unwrap();
                let show_count_rate: f32 = parse_percent(show_count_rate_str).parse().unwrap();
                let parse_box_sum: i64 = parse_box_sum(sum_box_desc_str);
            }
        }
    }


    Ok(())
}