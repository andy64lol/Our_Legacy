/**
 * UI Module for Our Legacy (Browser Version)
 * Terminal-style UI functions
 * Ported from utilities/UI.py
 */

import { Colors } from './settings.js';

/**
 * Clear the terminal screen
 */
export function clearScreen() {
  // Browser version - the game instance should handle clearing
}

/**
 * Create a visual progress bar
 * @param {number} current - Current value
 * @param {number} maximum - Maximum value
 * @param {number} width - Width of the bar
 * @param {string} color - Color code
 * @returns {string} Formatted progress bar
 */
export function createProgressBar(current, maximum, width = 20, color = Colors.GREEN) {
  if (maximum <= 0) {
    return "[" + " ".repeat(width) + "]";
  }
  const filledWidth = Math.floor((current / maximum) * width);
  const filled = "█".repeat(filledWidth);
  const empty = "░".repeat(width - filledWidth);
  const percentage = (current / maximum) * 100;
  return `[${Colors.wrap(filled, color)}${empty}] ${percentage.toFixed(1)}%`;
}

/**
 * Create a visual separator line
 * @param {string} char - Character to use
 * @param {number} length - Length of separator
 * @returns {string} Separator string
 */
export function createSeparator(char = "=", length = 60) {
  return char.repeat(length);
}

/**
 * Create a decorative section header
 * @param {string} title - Section title
 * @param {string} char - Character to use
 * @param {number} width - Width of header
 * @returns {string} Formatted header
 */
export function createSectionHeader(title, char = "=", width = 60) {
  const padding = Math.floor((width - title.length - 2) / 2);
  const headerText = `${char.repeat(padding)} ${title} ${char.repeat(padding)}`;
  return Colors.wrap(headerText, `${Colors.CYAN}${Colors.BOLD}`);
}

/**
 * Display welcome screen
 * @param {Object} lang - Language manager
 * @param {Object} gameInstance - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<string>} User choice
 */
export async function displayWelcomeScreen(lang, gameInstance, askFunc) {
  const game = gameInstance;
  
  while (true) {
    if (game && typeof game.clear === 'function') {
      game.clear();
    }
    game.print(`${Colors.CYAN}${Colors.BOLD}`);
    game.print("=".repeat(60));
    game.print(`             ${lang.get('game_title_display') || 'Our Legacy'}`);
    game.print(`       ${lang.get('game_subtitle_display') || 'A Text-Based Fantasy RPG'}`);
    game.print("=".repeat(60));
    game.print(`${Colors.END}`);
    game.print(lang.get("welcome_message") || "Welcome to Our Legacy!");
    game.print("Choose your path wisely, for every decision shapes your destiny.\n");
    game.print(`${Colors.BOLD}${Colors.CYAN}=== ${lang.get('main_menu') || 'Main Menu'} ===${Colors.END}`);
    game.print(`${Colors.CYAN}1.${Colors.END} ${lang.get('new_game') || 'New Game'}`);
    game.print(`${Colors.CYAN}2.${Colors.END} ${lang.get('load_game') || 'Load Game'}`);
    game.print(`${Colors.CYAN}3.${Colors.END} ${lang.get('settings') || 'Settings'}`);
    game.print(`${Colors.CYAN}4.${Colors.END} ${lang.get('mods') || 'Mods'}`);
    game.print(`${Colors.CYAN}5.${Colors.END} ${lang.get('quit') || 'Quit'}\n`);

    const choice = await askFunc(`${Colors.CYAN}Choose an option (1-5): ${Colors.END}`);
    
    if (choice === "1") {
      return "new_game";
    }
    if (choice === "2") {
      return "load_game";
    }
    if (choice === "3") {
      if (gameInstance && gameInstance.settingsWelcome) {
        await gameInstance.settingsWelcome();
      }
    }
    if (choice === "4") {
      if (gameInstance && gameInstance.modsWelcome) {
        await gameInstance.modsWelcome();
      }
    }
    if (choice === "5") {
      game.print(lang.get("thank_exit") || "Thank you for playing!");
      if (game && typeof game.clear === 'function') {
        game.clear();
      }
      return "quit";
    }
  }
}

/**
 * Display the main game menu
 * @param {Object} lang - Language manager
 * @param {Object} player - Player object
 * @param {string} areaName - Current area name
 * @param {string} menuMax - Maximum menu option number
 * @returns {string} Formatted menu string
 */
export function displayMainMenu(lang, player, areaName, menuMax = "20") {
  let output = "";
  output += `\n${Colors.BOLD}=== ${lang.get('main_menu') || 'Main Menu'} ===${Colors.END}`;
  output += `\n${lang.get("current_location", { area: areaName }) || `Current Location: ${areaName}`}`;

  // Time and weather
  const displayHour = Math.floor(player.hour);
  const displayMinute = Math.floor((player.hour - displayHour) * 60);
  const timeStr = lang.get("current_time", { hour: `${displayHour.toString().padStart(2, '0')}:${displayMinute.toString().padStart(2, '0')}` }) || `Time: ${displayHour.toString().padStart(2, '0')}:${displayMinute.toString().padStart(2, '0')}`;
  const dayStr = lang.get("current_day", { day: player.day.toString() }) || `Day ${player.day}`;
  const weatherDesc = player.getWeatherDescription ? player.getWeatherDescription(lang) : player.currentWeather;
  
  output += `\n${Colors.YELLOW}${timeStr} | ${dayStr}${Colors.END}`;
  output += `\n${Colors.CYAN}${weatherDesc}${Colors.END}`;

  output += `\n${Colors.CYAN}1.${Colors.END} ${lang.get('explore') || 'Explore'}`;
  output += `\n${Colors.CYAN}2.${Colors.END} ${lang.get('view_character') || 'View Character'}`;
  output += `\n${Colors.CYAN}3.${Colors.END} ${lang.get('travel') || 'Travel'}`;
  output += `\n${Colors.CYAN}4.${Colors.END} ${lang.get('inventory') || 'Inventory'}`;
  output += `\n${Colors.CYAN}5.${Colors.END} ${lang.get('missions') || 'Missions'}`;
  output += `\n${Colors.CYAN}6.${Colors.END} ${lang.get('fight_boss') || 'Fight Boss'}`;
  output += `\n${Colors.CYAN}7.${Colors.END} ${lang.get('tavern') || 'Tavern'}`;
  output += `\n${Colors.CYAN}8.${Colors.END} ${lang.get('shop') || 'Shop'}`;
  output += `\n${Colors.CYAN}9.${Colors.END} ${lang.get('alchemy') || 'Alchemy'}`;
  output += `\n${Colors.CYAN}10.${Colors.END} ${lang.get('elite_market') || 'Elite Market'}`;
  output += `\n${Colors.CYAN}11.${Colors.END} ${lang.get('rest') || 'Rest'}`;
  output += `\n${Colors.CYAN}12.${Colors.END} ${lang.get('companions') || 'Companions'}`;
  output += `\n${Colors.CYAN}13.${Colors.END} ${lang.get('dungeons') || 'Dungeons'}`;
  output += `\n${Colors.CYAN}14.${Colors.END} ${lang.get('challenges') || 'Challenges'}`;

  if (player.currentArea === "your_land") {
    output += `\n${Colors.CYAN}15.${Colors.END} ${lang.get('pet_shop', 'Pet Shop')}`;
  }
  output += `\n${Colors.CYAN}16.${Colors.END} ${lang.get('settings', 'Settings')}`;

  if (player.currentArea === "your_land") {
    output += `\n${Colors.YELLOW}17.${Colors.END} ${lang.get('furnish_home', 'Furnish Home')}`;
    output += `\n${Colors.YELLOW}18.${Colors.END} ${lang.get('build_structures', 'Build Structures')}`;
    output += `\n${Colors.YELLOW}19.${Colors.END} ${lang.get('farm', 'Farm')}`;
    output += `\n${Colors.YELLOW}20.${Colors.END} ${lang.get('training', 'Training')}`;
    output += `\n${Colors.CYAN}21.${Colors.END} ${lang.get('save_game') || 'Save Game'}`;
    output += `\n${Colors.CYAN}22.${Colors.END} ${lang.get('load_game') || 'Load Game'}`;
    output += `\n${Colors.CYAN}23.${Colors.END} ${lang.get('claim_rewards') || 'Claim Rewards'}`;
    output += `\n${Colors.CYAN}24.${Colors.END} ${lang.get('quit') || 'Quit'}`;
  } else {
    output += `\n${Colors.CYAN}17.${Colors.END} ${lang.get('save_game') || 'Save Game'}`;
    output += `\n${Colors.CYAN}18.${Colors.END} ${lang.get('load_game') || 'Load Game'}`;
    output += `\n${Colors.CYAN}19.${Colors.END} ${lang.get('claim_rewards') || 'Claim Rewards'}`;
    output += `\n${Colors.CYAN}20.${Colors.END} ${lang.get('quit') || 'Quit'}`;
  }

  return output;
}

export default {
  clearScreen,
  createProgressBar,
  createSeparator,
  createSectionHeader,
  displayWelcomeScreen,
  displayMainMenu
};
