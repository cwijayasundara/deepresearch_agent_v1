use axum::extract::FromRequestParts;
use axum::http::request::Parts;
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use serde_json::json;
use std::sync::Arc;

use crate::auth::service::{verify_token, Claims};

#[allow(dead_code)]
pub struct AuthUser(pub Claims);

impl FromRequestParts<Arc<crate::AppState>> for AuthUser {
    type Rejection = Response;

    async fn from_request_parts(
        parts: &mut Parts,
        state: &Arc<crate::AppState>,
    ) -> Result<Self, Self::Rejection> {
        let auth_header = parts
            .headers
            .get("authorization")
            .and_then(|v| v.to_str().ok());

        let header_value = auth_header.ok_or_else(|| {
            (
                StatusCode::UNAUTHORIZED,
                axum::Json(json!({"detail": "Missing authorization"})),
            )
                .into_response()
        })?;

        let token = header_value
            .strip_prefix("Bearer ")
            .ok_or_else(|| {
                (
                    StatusCode::UNAUTHORIZED,
                    axum::Json(json!({"detail": "Invalid auth scheme"})),
                )
                    .into_response()
            })?;

        let claims = verify_token(token, &state.settings).map_err(|_| {
            (
                StatusCode::UNAUTHORIZED,
                axum::Json(json!({"detail": "Invalid token"})),
            )
                .into_response()
        })?;

        Ok(AuthUser(claims))
    }
}
