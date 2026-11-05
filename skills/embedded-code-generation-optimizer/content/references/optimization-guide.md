# Embedded Code Optimization Guide

## 1. ARM Cortex-M Optimization Patterns

### 1.1 Bit Banding Operations

```c
// 传统方式 - 需要读取-修改-写入
if (GPIOA->ODR & GPIO_ODR_ODR5) {
    GPIOA->BSRR = GPIO_BSRR_BR_5;  // 清除
} else {
    GPIOA->BSRR = GPIO_BSRR_BS_5;  // 设置
}

// 优化方式 - 原子操作
uint32_t *gpio_odr = (uint32_t *)(0x42000000 + (GPIOA_BASE + 0x14 - 0x40000000) * 32 + 5 * 4);
*gpio_odr = value;  // 单条指令完成
```

### 1.2 DSP指令优化

```c
// 原始实现
int32_t filter(int32_t *data, int32_t *coeff, int len) {
    int32_t sum = 0;
    for (int i = 0; i < len; i++) {
        sum += data[i] * coeff[i];
    }
    return sum >> 15;
}

// ARM DSP优化
int32_t filter_optimized(int32_t *data, int32_t *coeff, int len) {
    int32_t sum = 0;
    __asm__ volatile (
        "mov r4, %[len]\n"
        "loop:\n"
        "ldr r2, [%[data]], #4\n"
        "ldr r3, [%[coeff]], #4\n"
        "smlal %[sum], sum_hi, r2, r3\n"
        "subs r4, #1\n"
        "bne loop\n"
        : [sum] "+r" (sum)
        : [data] "r" (data), [coeff] "r" (coeff), [len] "r" (len)
        : "r2", "r3", "r4", "cc"
    );
    return sum >> 15;
}
```

## 2. Power Optimization Patterns

### 2.1 Tickless Kernel Implementation

```c
// 低功耗tickless模式
void enter_tickless_idle(uint32_t ms) {
    // 计算下一个事件时间
    uint32_t next_event = get_next_event_tick();

    if (next_event > ms) {
        // 配置定时器唤醒
        configure_wakeup_timer(ms);

        // 进入深度睡眠
        SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
        PWR->CR |= PWR_CR_LPDS;  // 低功耗稳压器

        __WFI();

        // 恢复运行时校准
        calibrate_rtc_after_wakeup();
    }
}
```

### 2.2 外设时钟门控

```c
// 动态时钟控制
void enable_peripheral_clock(uint32_t periph_base) {
    if (periph_base == SPI1_BASE) {
        RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    } else if (periph_base == I2C1_BASE) {
        RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    }
}

void disable_peripheral_clock(uint32_t periph_base) {
    if (periph_base == SPI1_BASE) {
        RCC->APB2ENR &= ~RCC_APB2ENR_SPI1EN;
    } else if (periph_base == I2C1_BASE) {
        RCC->APB1ENR &= ~RCC_APB1ENR_I2C1EN;
    }
}
```

## 3. Memory Optimization Patterns

### 3.1 内存池分配器

```c
typedef struct memory_block {
    uint16_t size;
    uint8_t used;
    struct memory_block *next;
} memory_block_t;

static memory_block_t *memory_pool;
static uint8_t heap_memory[HEAP_SIZE];

void memory_pool_init(void) {
    memory_pool = (memory_block_t *)heap_memory;
    memory_pool->size = HEAP_SIZE - sizeof(memory_block_t);
    memory_pool->used = 0;
    memory_pool->next = NULL;
}

void *pool_alloc(uint16_t size) {
    memory_block_t *current = memory_pool;
    memory_block_t *prev = NULL;

    // 首次适应分配
    while (current != NULL) {
        if (!current->used && current->size >= size + sizeof(memory_block_t)) {
            // 分裂块
            memory_block_t *new_block = (memory_block_t *)
                ((uint8_t *)current + sizeof(memory_block_t) + size);
            new_block->size = current->size - size - sizeof(memory_block_t);
            new_block->used = 0;
            new_block->next = current->next;

            current->size = size;
            current->used = 1;
            current->next = new_block;

            return (uint8_t *)current + sizeof(memory_block_t);
        }
        prev = current;
        current = current->next;
    }
    return NULL;
}
```

### 3.2 CRC校验优化

```c
// 查表法CRC16优化
static const uint16_t crc_table[256] = {
    0x0000, 0x1021, 0x2042, 0x3063, /* ... */
};

uint16_t crc16_calc(uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    while (len--) {
        crc = (crc << 8) ^ crc_table[(crc >> 8) ^ *data++];
    }
    return crc;
}

// SIMD风格优化（STM32 G4）
uint16_t crc16_calc_hardware(CRC_HandleTypeDef *hcrc, uint8_t *data, uint32_t len) {
    HAL_CRC_Calculate(hcrc, data, len);
    return hcrc->Instance->DR;
}
```

## 4. Real-Time Optimization Patterns

### 4.1 环形缓冲区实现

```c
#include <stdint.h>
#include <string.h>

#define RB_INIT(name, size) \
    static uint8_t name##_buffer[size]; \
    static ring_buffer_t name = { \
        .buffer = name##_buffer, \
        .size = size, \
        .head = 0, \
        .tail = 0 \
    }

typedef struct {
    uint8_t *buffer;
    uint16_t size;
    volatile uint16_t head;
    volatile uint16_t tail;
} ring_buffer_t;

static inline uint16_t ring_buffer_write(ring_buffer_t *rb, uint8_t data) {
    uint16_t next_head = (rb->head + 1) % rb->size;
    if (next_head != rb->tail) {
        rb->buffer[rb->head] = data;
        __DMB();  // 数据内存屏障
        rb->head = next_head;
        return 1;
    }
    return 0;  // 缓冲区满
}

static inline uint16_t ring_buffer_read(ring_buffer_t *rb, uint8_t *data) {
    if (rb->tail != rb->head) {
        *data = rb->buffer[rb->tail];
        __DMB();
        rb->tail = (rb->tail + 1) % rb->size;
        return 1;
    }
    return 0;  // 缓冲区空
}
```

### 4.2 DMA双缓冲

```c
typedef struct {
    uint8_t *buffer_a;
    uint8_t *buffer_b;
    uint8_t *active_buffer;
    uint16_t buffer_size;
    void (*callback)(uint8_t *, uint16_t);
} double_buffer_t;

void dma_double_buffer_init(double_buffer_t *db, uint16_t size) {
    db->buffer_a = malloc(size);
    db->buffer_b = malloc(size);
    db->active_buffer = db->buffer_a;
    db->buffer_size = size;

    // 配置DMA
    hdma.Instance = DMA1_Channel1;
    hdma.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma.Init.MemInc = DMA_MINC_ENABLE;
    hdma.Init.Mode = DMA_CIRCULAR;
    HAL_DMA_Init(&hdma);

    // 启用双缓冲模式
    __HAL_DMA_ENABLE(&hdma);
}

void dma_transfer_complete_callback(DMA_HandleTypeDef *hdma) {
    double_buffer_t *db = (double_buffer_t *)hdma->Parent;

    // 切换缓冲区
    if (hdma->Instance->CR & DMA_SxCR_CT) {
        db->active_buffer = db->buffer_a;
    } else {
        db->active_buffer = db->buffer_b;
    }

    // 处理完成的数据
    if (db->callback) {
        db->callback(db->active_buffer, db->buffer_size);
    }
}
```

## 5. Flash/RAM Optimization

### 5.1 常量数据放置

```c
// 放在Flash指定区域
const uint8_t firmware_version[] __attribute__((section(".firmware_info"))) = "v1.2.3";

// 使用 __attribute__((const)) 通知编译器函数无副作用
static inline uint32_t get_chip_id(void) __attribute__((const));

static inline uint32_t get_chip_id(void) {
    return *(volatile uint32_t *)0xE0042000;
}

// XIP (eXecute-In-Place) 优化
__attribute__((section(".text")))
void critical_function(void) {
    // 确保函数在Flash执行，不复制到RAM
}
```

### 5.2 栈使用优化

```c
// 分析栈使用
uint32_t stack_analysis(void) {
    extern uint32_t _estack;
    extern uint32_t _sstack;

    uint32_t *p = (uint32_t *)&_estack;
    uint32_t *end = &_sstack;
    uint32_t max_used = 0;

    while (p > end) {
        if (*--p != 0xDEADBEEF) {
            max_used = (&_estack - p) * sizeof(uint32_t);
            break;
        }
    }
    return max_used;
}

// 设置栈填充值用于分析
void init_stack(void) {
    extern uint32_t _estack;
    extern uint32_t _sstack;

    uint32_t *p = (uint32_t *)&_estack;
    uint32_t *end = &_sstack;

    while (p > end) {
        *--p = 0xDEADBEEF;
    }
}
```

## 6. Compiler Optimization Directives

### 6.1 GCC优化

```c
// 函数属性
__attribute__((always_inline))
__attribute__((optimize("O3")))
__attribute__((naked))
__attribute__((section(".text.fastcode")))

// 变量属性
__attribute__((aligned(4)))
__attribute__((packed))
__attribute__((zero_init))

// 内存屏障
__asm__ volatile("" ::: "memory");

// 可能不需要的函数
__attribute__((weak))
```

### 6.2 IAR优化

```c
#pragma optimization = high
#pragma optimize = inline
#pragma location = ".text"

__ramfunc void fast_function(void) {
    // 在RAM中执行函数
}
```
