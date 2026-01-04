# C-Autograd-WASM: A Tiny Deep Learning Engine in C

![C](https://img.shields.io/badge/Language-C99-blue.svg)
![WASM](https://img.shields.io/badge/Platform-WebAssembly-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A lightweight, dependency-free **Automatic Differentiation (Autograd) Engine** written entirely in C. The trained model is ported to **WebAssembly (WASM)**, allowing it to run client-side in any browser—even offline—with zero latency.

## 🚀 Key Features

* **No External ML Libraries:** Built without PyTorch, TensorFlow, or BLAS. Pure C logic.
* **WebAssembly Port:** Runs at native speed in the browser using Emscripten.
* **Offline PWA:** Fully encapsulated as a Progressive Web App (PWA) capable of running without internet.
* **Tiny Footprint:** The entire deployed model and engine is just a few kilobytes.

## 📂 Deployment Files

These are the only files required to host the application:

```text
.
├── index.html         # The frontend UI (Canvas & Controls)
├── index.js           # Emscripten glue code (Connects JS to C)
├── index.wasm         # The compiled C engine & Model Weights
├── sw.js              # Service Worker (Enables offline support)
└── manifest.json      # PWA Metadata (Name, Icons, Display settings)