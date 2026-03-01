# TODO - Fix Parity Between main.js and main.py (1.1 & 1.2)

## Issues Found:

### 1.1 Alchemy/Crafting System (visitAlchemy)
- **Status**: IMPLEMENTED
- **Location**: main.js lines ~1730-1870
- **Parity Issues**:
  1. **Elixirs/Enchantments**: main.py uses "E" for both and asks sub-choice (E/N), main.js shows as separate options
  2. **Pagination**: main.py has "P" for previous page and "N" for next page, main.js doesn't handle P for previous
  3. **clear_screen()**: main.py calls it between loops, main.js doesn't
  4. **displayRecipesByCategory**: Shows recipes but doesn't allow viewing details (main.py does via enter)

### 1.2 Dungeons System (visitDungeons)
- **Status**: IMPLEMENTED - BUG FIXED
- **Location**: main.js lines ~1873-2200
- **Parity Issues**:
  1. **FIXED**: Syntax error in visitDungeons() - corrupted line "async visitD" removed
  2. **Pagination**: main.py uses "P"/"N" for pages, main.js uses a different approach
  3. **clear_screen()**: Called in main.py after entering dungeon, not in main.js

## Tasks:
- [x] Fix syntax error in visitDungeons() function
- [ ] Fix Alchemy: Add pagination (P for previous, N for next)
- [ ] Fix Alchemy: Handle E as both Elixirs/Enchantments with sub-choice
- [ ] Fix Alchemy: Add clear_screen() call
- [ ] Fix Dungeons: Add clear_screen() after entering dungeon
- [ ] Test both systems work correctly

## Priority:
1. Fix the syntax error in visitDungeons (CRITICAL - prevents function from running) - DONE
2. Fix Alchemy pagination (P for previous, N for next) 
3. Fix Alchemy E choice handling
4. Add clear_screen() calls where needed
5. Test
