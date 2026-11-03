# Theos Reverse Engineering Reference

## Tool Installation Guide

### macOS Environment Setup

```bash
# 1. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install basic tools
brew install wget curl ldid

# 3. Install Theos
git clone --recursive https://github.com/theos/theos.git /opt/theos

# 4. Configure environment variables
echo 'export THEOS=/opt/theos' >> ~/.zshrc
echo 'export PATH=$THEOS/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

### class-dump Installation

```bash
# Download class-dump
wget http://stevenygard.com/downloads/class-dump-x86_64.tar.gz

# Extract and install
tar -xzf class-dump-x86_64.tar.gz
sudo mv class-dump /usr/local/bin/
sudo chmod 755 /usr/local/bin/class-dump
```

### Theos Dependencies

```bash
# God tool suite
git clone https://github.com/pcjbird/theos.git /opt/theos

# Configure SSH passwordless login
ssh-keygen -t rsa
ssh-copy-id root@device_ip

# Test connection
ssh root@device_ip "echo test"
```

## Tweak Development Templates

### Basic Tweak Template (Tweak.xm)

```objc
#import <UIKit/UIKit.h>
#import <SpringBoard/SpringBoard.h>

// Log macro definition
#define TweakLog(fmt, ...) NSLog(@"[MyTweak] " fmt, ##__VA_ARGS__)

// Hook single method
%hook SpringBoard

- (void)applicationDidFinishLaunching:(id)application {
    TweakLog(@"Application launched");
    %orig;
}

%end

// Hook C function
extern "C" {
    void (*original_malloc)(size_t size);
    void my_malloc(size_t size) {
        TweakLog(@"malloc: %zu bytes", size);
        return original_malloc(size);
    }
}

// Initialization
%ctor {
    TweakLog(@"Tweak initialized");
    MSHookFunction((void *)0x1234, (void *)my_malloc, (void **)&original_malloc);
}
```

### Complete Makefile Example

```makefile
THEOS_DEVICE_IP = 192.168.1.100
THEOS_DEVICE_PORT = 22
THEOS_PACKAGE_DIR = $(THEOS)/../packages

ARCHS = arm64 arm64e
TARGET = iphone:clang:14.0:14.0

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = MyTweak
MyTweak_FILES = Tweak.xm
MyTweak_CFLAGS = -fobjc-arc
MyTweak_FRAMEWORKS = UIKit Foundation
MyTweak_PRIVATE_FRAMEWORKS = SpringBoard

# Depend on other Tweaks
MyTweak_DEPENDENCIES = mobile substrate

include $(THEOS)/makefiles/tweak.mk

after-stage::
	$(ECHO) "Installing to device..."
	@scp -P $(THEOS_DEVICE_PORT) $(THEOS_PACKAGE_DIR)/$(TWEAK_NAME).deb root@$(THEOS_DEVICE_IP):/tmp/
	@ssh -p $(THEOS_DEVICE_PORT) root@$(THEOS_DEVICE_IP) "dpkg -i /tmp/$(TWEAK_NAME).deb && killall -9 SpringBoard"
```

### control File Template

```
Package: com.mytweak.app
Name: MyTweak
Version: 1.0.0
Architecture: iphoneos-arm
Description: A powerful tweak for testing
Author: Developer <dev@example.com>
Maintainer: Developer <dev@example.com>
Section: Tweaks
Depends: mobilesubstrate (>= 0.9.5000)
```

## Common Hook Patterns

### UIViewController Hook

```objc
%hook UIViewController

- (void)viewDidLoad {
    TweakLog(@"%@ viewDidLoad", NSStringFromClass([self class]));
    %orig;
}

- (void)viewWillAppear:(BOOL)animated {
    TweakLog(@"%@ appearing", NSStringFromClass([self class]));
    %orig;
}

%end
```

### NSURLSession Hook

```objc
%hook NSURLSession

+ (id)sharedSession {
    TweakLog(@"sharedSession called");
    return %orig;
}

- (void)dataTaskWithURL:(NSURL *)url completionHandler:(void (^)(NSData *data, NSURLResponse *response, NSError *error))completionHandler {
    TweakLog(@"Request URL: %@", url.absoluteString);
    %orig;
}

%end
```

### Objective-C Runtime Method Swizzling

```objc
// Use Method Swizzling
#import <objc/runtime.h>

%hook SomeClass

+ (void)load {
    %orig;

    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        Class class = object_getClass((id)self);

        SEL originalSelector = @selector(originalMethod);
        SEL swizzledSelector = @selector(swizzledMethod);

        Method originalMethod = class_getInstanceMethod(class, originalSelector);
        Method swizzledMethod = class_getInstanceMethod(class, swizzledSelector);

        // Add swizzled method to original class
        BOOL didAddMethod = class_addMethod(class,
            swizzledSelector,
            method_getImplementation(swizzledMethod),
            method_getTypeEncoding(swizzledMethod));

        if (didAddMethod) {
            class_replaceMethod(class,
                originalSelector,
                method_getImplementation(swizzledMethod),
                method_getTypeEncoding(swizzledMethod));
        } else {
            method_exchangeImplementations(originalMethod, swizzledMethod);
        }
    });
}

- (void)swizzledMethod {
    TweakLog(@"Swizzled method called");
    [self swizzledMethod]; // Call original implementation
}

%end
```

## Frida Script Templates

### Basic Object-C Hook

```javascript
// hook_objc.js
'use strict';

// Hook specific class
var targetClass = "ViewController";
var targetMethod = "viewDidLoad";

var hook = ObjC.classes[targetClass];
if (hook) {
    var method = hook['-' + targetMethod];
    if (method) {
        method.implementation = function() {
            console.log('[*] viewDidLoad called');
            return this[targetMethod]();
        };
    }
} else {
    console.log('[-] Class not found: ' + targetMethod);
}
```

### Complete Network Monitor Script

```javascript
// network_monitor.js
'use strict';

console.log('[*] Network Monitor loaded');

// Hook NSURLConnection
var NSURLConnection = ObjC.classes.NSURLConnection;

// Hook CFNetwork
var CFNetwork = Process.enumerateModules().find(function(m) {
    return m.name.indexOf('CFNetwork') !== -1;
});

if (CFNetwork) {
    var sendRequest = CFNetwork.getExportByName('CFURLConnectionSendRequest');
    Interceptor.attach(sendRequest, {
        onEnter: function(args) {
            var request = args[2];
            console.log('[*] Request sent');
        }
    });
}

// Monitor all Objective-C class network request methods
['NSURLConnection', 'NSURLSession', 'NSMutableURLRequest'].forEach(function(className) {
    var klass = ObjC.classes[className];
    if (!klass) return;

    Object.keys(klass).forEach(function(key) {
        if (key.toLowerCase().indexOf('request') !== -1 ||
            key.toLowerCase().indexOf('data') !== -1) {
            try {
                var method = klass[key];
                method.implementation = function() {
                    console.log('[*] ' + className + ' ' + key);
                    return this[key].apply(this, arguments);
                };
            } catch (e) {}
        }
    });
});
```

## Reverse Analysis Tips

### class-dump Advanced Usage

```bash
# Export all class definitions
class-dump -H -o ./headers AppBinary

# Export protocols only
class-dump -H --only-protocols AppBinary

# Export instance variables
class-dump -H -I AppBinary

# Swift mixed app
swift-demangle symbols_file > demangled_output
```

### Hopper Script Automation

```bash
#!/bin/bash
# Analysis script

BINARY=$1
OUTPUT_DIR="./analysis"

mkdir -p $OUTPUT_DIR

# Export pseudocode
hopper -x --batch --output-format=psuedocode $BINARY > $OUTPUT_DIR/pseudocode.txt

# Export strings
strings $BINARY > $OUTPUT_DIR/strings.txt

# Extract specific patterns
grep -i "password\|secret\|key\|token" $OUTPUT_DIR/strings.txt > $OUTPUT_DIR/sensitive.txt
```

### IDA Pro Script (IDC)

```c
// Find all functions referencing specific string
#include <idc.idc>

static FindStringReferences()
{
    auto ea, func, strings;

    strings = Strings();
    while (strings.next()) {
        if (strstr(strings.get(), "password") != -1) {
            ea = strings.ea();
            auto xrefs = XrefsTo(ea);
            while (xrefs.next()) {
                func = GetFunctionName(xrefs.frm);
                Message("String '%s' referenced in %s\n", strings.get(), func);
            }
        }
    }
}
```

## Debug Commands Quick Reference

### LLDB Common Commands

```lldb
# Attach to process
process attach --name "AppName" --type iOS

# Set breakpoint
breakpoint set --name "-[ViewController viewDidLoad]"
breakpoint set -a 0x12345678

# View registers
register read

# Single step execution
thread step-instruction

# Print object
po $arg1
po [ViewController sharedInstance]
po [self view]

# View memory
x/100x 0x12345678
memory read --size 1 --format x 0x12345678

# View threads
thread list
thread backtrace

# Continue execution
continue
```

### iOS Device Commands

```bash
# View installed Tweaks
ls -la /Library/MobileSubstrate/DynamicLibraries/

# View logs
tail -f /var/log/syslog

# Restart SpringBoard
killall -9 SpringBoard

# View processes
ps aux | grep -i appname

# Use Cycript attach
cycript -p SpringBoard
cycript -p PID

# Frida connection
frida -U -f com.app.identifier
frida-ps -U
```

## Common Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `error: Theos/makefiles not found` | THEOS env var not set | `export THEOS=/opt/theos` |
| `make: *** No rule to make target 'package'` | Makefile path error | Check include path |
| `ld: library not found` | Missing framework | Add FRAMEWORKS in Makefile |
| `Hook failed to take effect` | Tweak not activated | Check /Library/MobileSubstrate/DynamicLibraries/ |
| `Device connection failed` | SSH config issue | Check THEOS_DEVICE_IP/PORT |
| `Symbol conflict` | Multiple Tweak conflict | Set dependency or adjust load order |

## Reference Links

- [Theos Official Documentation](https://theos.dev/docs)
- [iOS Reverse Engineering Getting Started](https://iphonedev.wiki/index.php/Cydia_Substrate)
- [libhooker Documentation](https://github.com/AsphaltKit/Logos/wiki)
- [Frida Official Documentation](https://frida.re/docs/javascript-api/)
- [Hopper Disassembler](https://www.hopperapp.com/)