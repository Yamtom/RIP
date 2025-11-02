# Alternative Ruthenian Immersion Pack (RIP)

The **Alternative Ruthenian Immersion Pack** is a fan-made mod for *Europa Universalis IV* that explores alternate historical developments for Ruthenia. It adds new nations, missions, disasters, decisions, and other flavour content to enrich gameplay across Eastern Europe and the Carpathians.

## Installation
1. Download or clone this repository.
2. Copy the entire mod folder and the `descriptor.mod` file into your EU4 mods directory, typically located at `Documents/Paradox Interactive/Europa Universalis IV/mod`.
3. Ensure the descriptor file sits next to the mod folder. If necessary, rename `descriptor.mod` to `Alternative Ruthenian Immersion Pack.mod`.
4. Launch the game and enable **Alternative Ruthenian Immersion Pack** from the launcher.

## Compatibility
- **Supported EU4 version:** 1.37.5
- The included `descriptor.mod` file specifies no external dependencies.

## Recent Highlights
- Added the *Opryshky Uprising* disaster chain for Uzhhorod, inspired by 17th–18th century Máramaros mountain brotherhoods, with bespoke events and modifiers.

## Development Notes

### Running Tests

To ensure event IDs remain unique, run:

```powershell
python tests/test_event_ids.py
```
