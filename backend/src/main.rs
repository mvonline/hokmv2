use actix_web::{web, App, HttpServer};

mod game;
mod ws;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    println!("Starting server at http://127.0.0.1:8080");

    HttpServer::new(|| {
        App::new()
            .route("/ws/", web::get().to(ws::index))
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}
