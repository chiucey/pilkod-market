---
name: theos-reversing
description: iOS jailbreak reverse engineering skill. Used when users request iOS reverse analysis, Theos jailbreak development, Tweak creation, IPA decryption, dynamic analysis, static analysis, or iOS app reverse engineering using class-dump/Hopper/LLDB.
---

# Theos iOS Reverse Engineering Skill

## Skill Overview

This skill provides a complete iOS jailbreak reverse engineering workflow, covering the full chain from environment setup to dynamic/static analysis.

## Prerequisites

### Required Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| Theos | Jailbreak Tweak development framework | `git clone --recursive https://github.com/theos/theos.git ~/theos` |
| libhooker | Hook framework | Cydia/Sileo install |
| substrate | Early hook framework | Cydia install |
| class-dump | Extract OC class info | Compile and install |
| Hopper Disassembler | Disassembler tool | Download from official site |
| ldid | Code signing tool | `brew install ldid` |

### Environment Variables

```bash
# ~/.zshrc or ~/.bashrc
export THEOS=/opt/theos
export PATH=$THEOS/bin:$PATH
export THEOS_DEVICE_IP=your_ios_device_ip
export THEOS_DEVICE_PORT=22
```

## Core Workflow

### Workflow 1: IPA Decryption

**Goal**: Extract decrypted binary for analysis

```bash
# Method 1: frida-ios-dump
python3 dump.py com.app.identifier

# Method 2: CrackToolKit
./cracktool -d com.app.identifier -o output/

# Method 3: Manual frida
frida -U -f com.app.identifier --no-pause
# Load in Unicorn and dump
```

**Verify decryption success**:
```bash
# Check if Mach-O is encrypted
otool -l target_binary | grep -E "(LC_ENCRYPTION|CRYPT)"
# No encryption segment or CRYPT_ID=0 means success
```

### Workflow 2: Static Analysis

#### 2.1 Extract Class Info

```bash
# Use class-dump to extract Objective-C headers
class-dump -H encrypted_app.ipa -o headers/

# Extract Swift info (if contains Swift)
swift-demangle symbols_file
```

#### 2.2 Using Hopper

```bash
# Open binary file
hopperdisassembler /path/to/binary

# Common shortcuts
- / : Search strings/method names
- ; : Add comment
- Tab : Toggle pseudocode/assembly
- G : Go to address
```

#### 2.3 Key Analysis Points

| Analysis Target | Tool/Command | Description |
|----------------|--------------|-------------|
| Class structure | class-dump | Analyze ViewController, Model |
| Method cross-reference | Hopper | Locate key functions |
| String resources | strings/grep | Locate sensitive strings |
| Network requests | Analyze URL Scheme | Trace API calls |

### Workflow 3: Tweak Development

#### 3.1 Project Initialization

```bash
# Create project with Theos template
$THEOS/bin/nic.pl

# Select template:
# 1. iphone/tweak - Create Tweak plugin
# 2. iphone/application - Create standalone app
# 3. iphone/tool - Create command line tool
```

#### 3.2 Tweak Template

```objc
// Tweak.xm example
#import <UIKit/UIKit.h>

%hook AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    // Add hook logic here
    NSLog(@"Tweak loaded successfully!");
    return %orig;
}

%end
```

#### 3.3 Makefile Configuration

```makefile
THEOS_DEVICE_IP = 192.168.1.100
THEOS_DEVICE_PORT = 22
THEOS_PACKAGE_DIR = ./packages

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = MyFirstTweak
MyFirstTweak_FILES = Tweak.xm
MyFirstTweak_FRAMEWORKS = UIKit Foundation
MyFirstTweak_LDFLAGS = -Wl,-S,-x

include $(THEOS)/makefiles/tweak.mk

after-stage::
    $(ECHO) "Installing to /Library/MobileSubstrate/DynamicLibraries/"
```

#### 3.4 Build and Deploy

```bash
# Build locally
make package

# Deploy to jailbroken device remotely
make package install

# Install only
make install
```

### Workflow 4: Dynamic Analysis

#### 4.1 LLDB Debugging

```bash
# Attach to process
debugserver *:1234 -a <app_pid>

# Connect from computer
lldb
(gdb) process connect connect://device_ip:1234
```

#### 4.2 Frida Dynamic Hook

```javascript
// Basic hook example
var hookClass = ObjC.classes.ViewController;
if (hookClass) {
    hookClass['- viewDidLoad'].implementation = function() {
        console.log("[*] viewDidLoad called");
        return this.original_viewDidLoad();
    };
}

// Hook C function
var malloc = Module.findExportByName("libSystem.B.dylib", "malloc");
Interceptor.attach(Module.ensureNativeSymbol(malloc), {
    onEnter: function(args) {
        console.log("malloc called with size:", args[0].toInt32());
    }
});
```

#### 4.3 Log Output

```objc
// Objective-C log
NSLog(@"[*] Hook triggered: %@", someObject);

// C function log (via NSLog)
extern void NSLog(CFStringRef format, ...);
NSLog(CFSTR("[*] C function called"));
```

### Workflow 5: Common Scenarios

#### Scenario 1: Bypass SSL Pinning

```objc
%hook NSURLSession
+ (void)load {
    %orig;
    NSLog(@"[*] NSURLSession loaded");
}

// Implement SSL verification bypass
%end
```

#### Scenario 2: Unlock Premium Features

```objc
%hook VIPManager
- (BOOL)isPremiumUser {
    return YES; // Force return true
}
%end
```

#### Scenario 3: Remove Ads

```objc
%hook AdView
- (void)loadAd {
    // Silent fail, do not load ad
    return;
}
%end
```

## Advanced Tips

### 1. Locate Key Code

```bash
# Use MobSF for automated analysis
mobsf/mobsf.py -f target.ipa

# String search
strings target_binary | grep -i "password\|secret\|api"
```

### 2. Theos Multi-Module Development

```bash
# Support multiple Tweaks in same project
include $(THEOS)/makefiles/common.mk

TWEAK_NAME = Module1 Module2
Module1_FILES = Module1/Tweak.xm
Module2_FILES = Module2/Tweak.xm

include $(THEOS)/makefiles/tweak.mk
```

### 3. Debugging Tips

```bash
# Enable verbose log
MyTweak_CFLAGS = -DDEBUG=1

# Add in Tweak
#ifdef DEBUG
    NSLog(@"Debug info: %@", debugVar);
#endif
```

## Output Artifacts

| Artifact Type | Description | Output Path |
|---------------|-------------|-------------|
| Decrypted IPA | Decrypted app bundle | `./decrypted/` |
| Headers | class-dump extract | `./headers/` |
| Hook code | Tweak source | `./Tweak.xm` |
| Package | deb format | `./packages/` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build failed | Check THEOS env var `echo $THEOS` |
| Deploy failed | Verify device connection `ping $THEOS_DEVICE_IP` |
| Hook not effective | Verify Tweak is enabled `ls /Library/MobileSubstrate/DynamicLibraries/` |
| Link error | Check frameworks and ldsflags config |

## Notes

1. **Legality**: Only reverse engineer apps you have legal rights to use
2. **Backup**: Backup original IPA before operations
3. **Version compatibility**: Theos version must match iOS SDK version
4. **Device security**: Ensure jailbroken device security, avoid installing plugins from unknown sources