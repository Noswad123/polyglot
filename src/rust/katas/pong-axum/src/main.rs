use axum::{
    http::StatusCode,
    response::IntoResponse,
    routing::get,
    Router,
};
use std::{env, net::SocketAddr};

async fn ping() -> impl IntoResponse {
    (StatusCode::OK, "pong")
}

#[tokio::main]
async fn main() {
    let port: u16 = env::var("PORT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(8080);

    let app = Router::new().route("/ping", get(ping));

    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    println!("Listening on http://{addr}");

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
