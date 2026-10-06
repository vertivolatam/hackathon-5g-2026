#![no_std]
#![no_main]

use esp_backtrace as _;
use esp_hal::{
    i2c::master::{Config as I2cHwConfig, I2c},
    time::Rate,
};
use esp_println::println;

use embedded_hal_bus::i2c::RefCellDevice;

mod audio;
mod backlight;
mod board;
mod camera;
#[cfg(feature = "dsi")]
mod display_dsi;
mod display_mipidsi_spi;
mod eth;
mod touch;

use audio::Es8311;
use backlight::Backlight;
use touch::Gt911;

#[esp_hal::main]
fn main() -> ! {
    esp_alloc::heap_allocator!(size: 64 * 1024);

    let config = esp_hal::Config::default();
    let p = esp_hal::init(config);

    println!("esp32-p4-nano-fw boot: P4NRW32 + I2C SDA=GPIO7 SCL=GPIO8");

    // I2C0 master 400kHz, ownership exclusiva del HAL...
    let i2c_bus = I2c::new(
        p.I2C0,
        I2cHwConfig::default().with_frequency(Rate::from_khz(400)),
    )
    .expect("i2c0")
    .with_sda(p.GPIO7)
    .with_scl(p.GPIO8);
    // ...y compartida a N drivers sin `&mut` en cada método, vía RefCellDevice.
    // (patrón recomendado docs.rs embedded-hal 1.0: HAL expone exclusivo,
    //  el usuario parte con embedded-hal-bus).
    use core::cell::RefCell;
    let bus = RefCell::new(i2c_bus);

    // 1) Backlight 0x45 reg 0x96 al 80%.
    {
        let dev = RefCellDevice::new(&bus);
        let mut bl = Backlight::new(dev);
        match bl.set_brightness(200) {
            Ok(()) => println!("backlight ok (0x45:0x96=200)"),
            Err(_) => println!("backlight NACK: revisa flat MIPI-DSI / 5V"),
        }
    }

    // 2) Audio ES8311 0x18 sanity.
    {
        let dev = RefCellDevice::new(&bus);
        let mut codec = Es8311::new(dev);
        match codec.chip_id() {
            Ok(id) => println!("es8311 chip_id=0x{:02x}", id),
            Err(_) => println!("es8311 NACK en 0x18"),
        }
    }

    // 3) Touch GT911 polling (RST/INT NC).
    let mut gt = match Gt911::new(RefCellDevice::new(&bus)) {
        Ok(d) => {
            println!("gt911 ok addr=0x{:02x} (polling)", d.address());
            Some(d)
        }
        Err(_) => {
            println!("gt911 NACK 0x5D/0x14: display sin touch o cable suelto");
            None
        }
    };

    // 4) Cámara: solo probe SCCB (CSI requiere ESP-IDF esp_video).
    {
        let mut raw = bus.borrow_mut();
        match camera::probe_sccb(&mut *raw, camera::SCCB_CANDIDATES) {
            Some(a) => println!("camera SCCB ACK 0x{:02x}", a),
            None => println!("camera sin ACK (normal sin modulo CSI)"),
        }
    }

    println!("eth: {}", eth::rmii_summary());
    println!("mipidsi: {}", display_mipidsi_spi::note());
    #[cfg(feature = "dsi")]
    println!("dsi feature on: ver display_dsi.rs (MipiDsi+Dbi->Dpi, fbs en PSRAM)");

    let delay = esp_hal::delay::Delay::new();
    loop {
        if let Some(g) = gt.as_mut() {
            match g.read_first_point() {
                Ok(Some(pt)) => println!("touch x={} y={} s={}", pt.x, pt.y, pt.size),
                Ok(None) => {}
                Err(_) => println!("gt911 read err"),
            }
        }
        delay.delay_millis(100);
    }
}
