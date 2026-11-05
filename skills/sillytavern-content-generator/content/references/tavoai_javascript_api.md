---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 58f1faf4fe61170b5281c5f44fbf0e2a
    PropagateID: 58f1faf4fe61170b5281c5f44fbf0e2a
    ReservedCode1: 3046022100fba9295da04837e23b961051da7234c7b263a81c06d20ce6ff08776f986f826b022100f3a5c74fb355c7876228f54ac2549b8097c2641377304715e873cabdae197850
    ReservedCode2: 3044022029244cb84977fddd1df7df4d41360a41a7815193f7eb2330e2898f875a3549e0022050cd088a7a62f5df3fa9b7f38b940d9f6a87474acd265ec68e3723480df127b3
---

# TavoAI JavaScript API Reference

Complete reference for TavoAI JavaScript scripting capabilities. Scripts run in the browser environment with access to TavoAI's internal APIs.

## API Overview

The `tavo` object provides the main API interface with the following sub-namespaces:

| Namespace | Purpose |
|-----------|---------|
| `tavo.get` | Read data from TavoAI |
| `tavo.set` | Write/modify data |
| `tavo.update` | Update specific fields |
| `tavo.unset` | Clear/remove data |
| `tavo.generate` | Control message generation |
| `tavo.input` | Handle user input |
| `tavo.utils` | Utility functions |

## tavo.get - Read Data

Read various types of data from the application.

### Character Data

```javascript
// Get full character card object
tavo.get.character()

// Get specific character fields
tavo.get.charDescription()   // Character description
tavo.get.charPersonality()   // Character personality
tavo.get.charScenario()      // Scenario setting
tavo.get.charName()          // Character name
```

### Chat Data

```javascript
// Get full chat history
tavo.get.chat()

// Get last message
tavo.get.chat(-1)

// Get message count
tavo.get.chat().length
```

### User Data

```javascript
tavo.get.userName()         // Username
tavo.get.userDescription()  // User persona description
tavo.get.persona()          // Full user persona object
```

### Lorebook/World Book

```javascript
tavo.get.lorebook()    // Get lorebook entries
tavo.get.world()       // Get world book content
```

### Regex and Memory

```javascript
tavo.get.regex()    // Get regex rules
tavo.get.memory()   // Get memory entries
```

### Preset Data

```javascript
tavo.get.preset()   // Get current preset
```

### Variables

```javascript
// Local variables (per-entry)
tavo.get.var('variableName')
tavo.get.variable('variableName')

// Global variables (persistent)
tavo.get.globalvar('variableName')
tavo.get.globalVariable('variableName')
```

## tavo.set - Write Data

Modify data in TavoAI.

### Character Data

```javascript
// Set full character object
tavo.set.character({
  name: "New Name",
  description: "New description"
})

// Set specific fields
tavo.set.charDescription("New description")
tavo.set.charPersonality("New personality")
tavo.set.charScenario("New scenario")
tavo.set.charName("New Name")
```

### Chat Data

```javascript
// Set entire chat history
tavo.set.chat([
  { role: "user", content: "Hello" },
  { role: "assistant", content: "Hi there!" }
])

// Note: Usually better to use tavo.update.addUserMessage()
```

### User Data

```javascript
tavo.set.persona({
  name: "New User Name",
  description: "New persona description"
})

tavo.set.userName("New User Name")
tavo.set.userDescription("New description")
```

### Variables

```javascript
// Local variable
tavo.set.var('variableName', 'value')
tavo.set.variable('variableName', 'value')

// Global variable
tavo.set.globalvar('variableName', 'value')
tavo.set.globalVariable('variableName', 'value')
```

## tavo.update - Update Data

Update specific fields with additional content.

### Character Updates

```javascript
// Append to character description
tavo.update.charDescription(" Additional description text.")

// Append to personality
tavo.update.charPersonality(" Additional personality traits.")

// Update scenario
tavo.update.charScenario(" New scenario setting.")
```

### Chat Updates

```javascript
// Add a user message to chat
tavo.update.addUserMessage("Message content")

// Add a character message
tavo.update.addAssistantMessage("Character response")
```

### Dynamic Updates

```javascript
// Conditional update example
const trust = tavo.get.globalvar('trust') || 0;
if (trust > 50) {
  tavo.update.charPersonality(
    tavo.get.charPersonality() +
    "\nShe has come to trust you."
  );
}
```

## tavo.unset - Clear Data

Remove or reset specific data.

```javascript
// Clear character description
tavo.unset.charDescription()

// Clear personality
tavo.unset.charPersonality()

// Clear scenario
tavo.unset.charScenario()

// Clear specific variable
tavo.unset.var('variableName')
tavo.unset.globalvar('variableName')
```

## tavo.generate - Generation Control

Control the message generation process.

### Cancel/Stop Generation

```javascript
// Cancel current generation
tavo.generate.cancel()

// Stop generation
tavo.generate.stop()
```

### Force Character Name

```javascript
// Force specific name in generation
tavo.generate.setForceName("Character Name")

// Disable force name
tavo.generate.setForceName("")
```

### Ignore Names

```javascript
// Ignore other character names in generation
tavo.generate.setIgnoreNames(true)

// Allow name generation
tavo.generate.setIgnoreNames(false)
```

## tavo.input - Input Handling

Work with the user input field.

### Read Input

```javascript
// Get current input field content
tavo.input.prompt()
```

### Write Input

```javascript
// Set input field content
tavo.input.setPrompt("New input text")

// Append to input
tavo.input.setPrompt(tavo.input.prompt() + " additional text")
```

### Macro Management

```javascript
// Add a macro to the input
tavo.input.addMacro("macroName", "macroContent")

// Example: Add a quick action
tavo.input.addMacro("action", "*takes a deep breath*")
```

### Message Manipulation

```javascript
// Set the last message content
tavo.input.setLastMessage("Modified message content")
```

## tavo.utils - Utility Functions

Helper functions for common operations.

### ID Retrieval

```javascript
// Get current character ID
tavo.utils.getCurrentCharId()

// Get current user ID
tavo.utils.getCurrentUserId()
```

### Dice Rolling

```javascript
// Roll dice with standard notation
tavo.utils.rollDice("3d6")    // Roll three six-sided dice
tavo.utils.rollDice("1d20")   // Roll a twenty-sided die
tavo.utils.rollDice("2d10")  // Roll two ten-sided dice
```

### Date/Time

```javascript
// Get current time
tavo.utils.getTime()    // Returns: "14:30"

// Get current date
tavo.utils.getDate()    // Returns: "2024-01-15"

// Get day of week
tavo.utils.getWeekday() // Returns: "Monday"

// Get idle duration since last message
tavo.utils.getIdleDuration() // Returns: "5m" or "2h"

// Get Unix timestamp
tavo.utils.getTimestamp()
```

## Script Examples

### Example 1: Relationship Tracker

```javascript
// Track relationship progression
const trust = tavo.get.globalvar('trust') || 0;
const affection = tavo.get.globalvar('affection') || 0;

// Increment based on positive interaction
tavo.set.globalvar('trust', trust + 5);
tavo.set.globalvar('affection', affection + 3);

// Update character personality based on trust level
if (trust > 75) {
  const current = tavo.get.charPersonality();
  if (!current.includes('trustworthy')) {
    tavo.update.charPersonality(
      " She has come to see you as a trustworthy ally."
    );
  }
}
```

### Example 2: Story Progress Manager

```javascript
// Get current chapter
let chapter = tavo.get.globalvar('chapter') || 1;

// Check for chapter transition
const chat = tavo.get.chat();
const lastMessage = chat[chat.length - 1]?.content || '';

if (lastMessage.includes('chapter_complete')) {
  chapter = chapter + 1;
  tavo.set.globalvar('chapter', chapter);

  // Update scenario for new chapter
  tavo.update.charScenario(
    `Chapter ${chapter} begins. ` +
    tavo.get.charScenario()
  );
}
```

### Example 3: Dynamic Greeting

```javascript
// Time-based greeting
const hour = new Date().getHours();
let greeting = "Hello";

if (hour < 12) {
  greeting = "Good morning";
} else if (hour < 18) {
  greeting = "Good afternoon";
} else {
  greeting = "Good evening";
}

// Set input with dynamic greeting
tavo.input.setPrompt(`${greeting}, how can I help you today?`);
```

### Example 4: Dice Game Integration

```javascript
// Roll for random encounter
const roll = tavo.utils.rollDice("1d100");

if (roll <= 20) {
  // 20% chance: Rare encounter
  tavo.input.setPrompt("A rare legendary creature appears!");
} else if (roll <= 50) {
  // 30% chance: Uncommon encounter
  tavo.input.setPrompt("An uncommon monster blocks your path.");
} else {
  // 50% chance: Common encounter
  tavo.input.setPrompt("You encounter some forest creatures.");
}
```

### Example 5: Character State Machine

```javascript
// Simple state machine for character behavior
const state = tavo.get.globalvar('characterState') || 'neutral';

const responses = {
  'neutral': 'I\'m watching you carefully.',
  'friendly': 'Welcome back, friend!',
  'hostile': 'You dare show your face here?!',
  'romantic': 'I\'ve missed you so much...'
};

tavo.generate.setForceName(responses[state] || responses['neutral']);
```

## Best Practices

1. **Always initialize variables**: Check for undefined before use
2. **Use global variables for persistence**: Local vars reset between entries
3. **Keep scripts efficient**: Avoid heavy operations in hot paths
4. **Handle errors gracefully**: Use try-catch for API calls
5. **Test incrementally**: Build scripts piece by piece
6. **Document your code**: Comment complex logic
7. **Avoid infinite loops**: Be careful with recursive calls
8. **Consider performance**: Heavy scripts can slow down generation

## Error Handling

```javascript
try {
  const value = tavo.get.globalvar('myVariable');
  if (value !== undefined) {
    // Safe to use
  }
} catch (e) {
  console.error('Error accessing variable:', e);
}
```
