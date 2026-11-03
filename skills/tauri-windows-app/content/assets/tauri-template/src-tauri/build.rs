fn main() {
    // 显式声明对前端产物的依赖。
    //
    // `tauri-build` 本身会对 `frontendDist` 目录发 `cargo:rerun-if-changed`，
    // 但当配置来源变化（例如用 `--config` 传入临时配置）时，cargo 的 build script
    // 指纹可能沿用上一次的结果，导致 **exe 里内嵌的是上一轮的旧前端资源**，
    // 表现为「改了界面但 exe 没变」，甚至白屏。
    //
    // 这里再显式声明一次，保证前端产物变化时 build script 一定重跑。
    let manifest_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap_or_else(|_| ".".to_string());
    println!("cargo:rerun-if-changed={}/../dist", manifest_dir);
    println!("cargo:rerun-if-changed={}/../dist/assets", manifest_dir);

    tauri_build::build()
}
