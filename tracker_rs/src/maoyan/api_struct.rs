use serde::{Serialize, Deserialize};


#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MaoyanBoxStruct {
    pub status: bool,
    pub box_office: BoxOffice,
}

#[derive(Serialize, Deserialize)]
pub struct BoxOffice {
    pub data: Data,
    pub success: bool,
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Data {
    pub list: Vec<List>,
    pub national_box: Nationalbox,
    pub update_info: UpdateInfo,
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct List {
    pub box_desc: String,
    pub box_rate: String,
    pub movie_info: MovieInfo,
    pub seat_count_rate: String,
    pub show_count_rate: String,
    pub sum_box_desc: String,
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MovieInfo {
    pub movie_id: i32,
    pub movie_name: String,
    pub release_info: String,
}

#[derive(Serialize, Deserialize)]
pub struct Nationalbox {
    pub num: String,
    pub unit: String,
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UpdateInfo {
    pub date: String,
    pub time: String,
    pub update_gap_second: i32,
    pub update_timestamp: i64,
}