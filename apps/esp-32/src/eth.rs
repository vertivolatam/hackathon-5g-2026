//! Ethernet 100M: EMAC interno P4 + PHY IP101GRI (RMII).
//!
//! Mapa RMII en `board.rs` (REF_CLK GPIO50 50MHz PHY->P4, MDC GPIO31,
//! MDIO GPIO52, RST GPIO51, TX_EN 49, TXD 34/35, CRS_DV 28, RXD 29/30).
//! PoE: header dedicado, el FW solo cuida no colgar GPIOs RMII en boot
//! (GPIO35 es strapping).

/// Nota esp-hal: `esp_hal::ethernet` aún no expone EMAC RMII genérico en
/// todas las releases; el bring-up de referencia es ESP-IDF
/// (`esp_eth` + `esp_eth_phy_ip101`). Este módulo fija el contrato de pines
/// para que el port Rust lo consuma sin adivinar.
pub const PHY_ADDR_DEFAULT: u8 = 1;

pub fn rmii_summary() -> &'static str {
    "RMII IP101GRI: REF_CLK=50 TX_EN=49 TXD0=34 TXD1=35 CRS_DV=28 RXD0=29 RXD1=30 MDC=31 MDIO=52 RST=51"
}
