# Project Status & JavaScript Issues

This document lists identified problems in the JavaScript port of "Our Legacy" and provides a roadmap for fixes.

## Identified Problems

### 1. Tooling & Environment
- **ESLint Configuration Error**: The `eslint.config.js` fails because `@eslint/js` is not installed.
- **Missing Dependencies**: Several packages required for development (like `eslint`) are not in `package.json` or not installed in the environment.

### 2. Core Game Logic (main.js)
- **Settings Manager Initialization**: `settingsManager` is imported dynamically in the constructor, which might lead to race conditions where `this.settingsManager` is undefined when `LanguageManager` or `ModManager` tries to use it.
- **Global Variable Usage**: `COLORS_ENABLED` is handled with both `let` and `globalThis`, which is inconsistent and can lead to debugging headaches.
- **Blocking `delay` in `loadingIndicator`**: The `loadingIndicator` uses a loop with `game.delay(500)`, but it's not marked as `async`, yet it calls what looks like an asynchronous method (`game.delay`).
- **Data Loading Robustness**: Many `fetch` calls in `loadGameData` don't have individual error handling, meaning one failure might skip others or leave the game in a partially loaded state.

### 3. UI System (utilities_js/UI.js)
- **Empty `clearScreen`**: The `clearScreen` function is currently empty, relying on the "game instance" to handle it, but it's exported and likely expected to do something.
- **Menu Consistency**: `displayMainMenu` returns a string, while `displayWelcomeScreen` handles printing and interaction directly. This inconsistency makes the API harder to use.

### 4. Battle System (utilities_js/battle.js)
- **Potential Infinite Loop**: The battle loop `while (this.player.isAlive() && enemy.isAlive())` could hang if neither side can deal damage or if an error occurs inside the loop.
- **Missing Implementation**: `this.game.useItemInBattle()` is called but its implementation in `main.js` was truncated in the read, and it's a common source of bugs in ports.
- **Async/Sync Mismatch**: `companionsAct` and `enemyTurn` are called without `await`, but they might need to be asynchronous if they involve delays or animations.

### 5. Mod Manager
- **Dynamic Loading**: Mod loading is complex and relies on many file-system-like operations in a browser environment (`fetch`), which needs robust fallback mechanisms.

---

## Proposed Fixes

### T001: Fix Development Environment
- Update `package.json` with correct ESLint dependencies.
- Fix `eslint.config.js` to use available or standard configurations.
- Run `npm install`.

### T002: Refactor Game Initialization
- Change `settingsManager` import to be top-level or ensure the constructor waits for it.
- Consolidate global state management into a single `Config` object or the `Game` class.

### T003: Improve UI Consistency
- Standardize all UI functions to either return strings or handle their own printing via a passed-in `terminal` object.
- Implement `clearScreen` properly for the browser environment (e.g., clearing a specific DOM element).

### T004: Harden Battle System
- Add timeouts or turn limits to the battle loop.
- Ensure all turn-based actions are consistently `async/await`.
- Add comprehensive logging for combat events to aid debugging.

### T005: Robust Data Loading
- Wrap individual `fetch` calls in `loadGameData` with try-catch blocks.
- Implement a "Loading Progress" state to show the user exactly which files are being loaded.
