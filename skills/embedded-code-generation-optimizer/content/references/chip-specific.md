# Chip-Specific Optimization Reference

## 1. STM32系列 (ST Microelectronics)

### 1.1 STM32F1/F4/H7优化

```c
// STM32F4 DSP优化 - 使用ARM DSP指令
#include "arm_math.h"

arm_pid_instance_f32 pid;
float32_t input, output;

void pid_init(void) {
    pid.Kp = 1.0f;
    pid.Ki = 0.1f;
    pid.Kd = 0.05f;
    arm_pid_init_f32(&pid, 1);
}

float32_t pid_compute(float32_t target, float32_t measured) {
    return arm_pid_f32(&pid, target - measured);
}

// STM32H7 D-Cache配置
void stm32h7_cache_enable(void) {
    SCB_EnableICache();
    SCB_EnableDCache();
}

void stm32h7_cache_invalidate(void) {
    SCB_InvalidateDCache();
}

// STM32F4 FMC/FSMC优化
void fmc_optimized_init(void) {
    FMC_Bank1->BTCR[0] = FMC_Bank1_R_BTR_MODEx |
                          FMC_Bank1_R_BTR_ADDSETx |
                          FMC_Bank1_R_BTR_DATASTx;
}
```

### 1.2 STM32WB/L4+ 低功耗

```c
// STM32WB BLE低功耗
void ble_low_power_init(void) {
    // 配置BLE栈为低功耗模式
    SHCI_C2_BLE_Init();
    BLE_STACK_Config();

    // 配置RF功率
    aci_hal_set_tx_power_level(0, 4);  // 0dBm
}

void stm32wb_stop2_enter(void) {
    HAL_PWREx_EnterSTOP2Mode(PWR_STOPENTRY_WFI);
}

// STM32L4+超低功耗
void stm32l4ulp_config(void) {
    // 启用超低功耗模式
    HAL_PWREx_EnableLowPowerMode();

    // 配置LPTIM用于唤醒
    hlptim1.Instance = LPTIM1;
    HAL_LPTIM_TimeOut_Start_IT(&hlptim1, 0, 65535);
}
```

## 2. GD32系列 (兆易创新)

### 2.1 GD32F103/F407优化

```c
// GD32外设时钟门控
void gd32_periph_clock_gate(uint32_t periph, FunctionalState state) {
    if (state == ENABLE) {
        RCU->APB1EN |= periph;
    } else {
        RCU->APB1EN &= ~periph;
    }
}

// GD32 flash预取缓冲
void gd32_flash_prefetch_enable(void) {
    FMC->WS |= FMC_WS_WSCNT(0);  // 0个等待周期
    FMC->CTLR |= FMC_CTLR_PB1;
}

// GD32 EXTI边沿配置
void gd32_exti_init(uint8_t line, uint8_t mode, uint8_t triger) {
    rcu_periph_clock_enable(RCU_CFGCMP);
    exti_init((exti_line_enum)(EXTI_0 + line), mode, triger);
}
```

### 2.2 GD32E230系列

```c
// GD32E230定时器配置
void gd32e230_timer_config(void) {
    timer_parameter_struct timer_initpara;
    rcu_periph_clock_enable(RCU_TIMER0);

    timer_struct_para_init(&timer_initpara);
    timer_initpara.prescaler = 47;      // 48MHz / 48 = 1MHz
    timer_initpara.alignedmode = TIMER_COUNTER_EDGE;
    timer_initpara.counterdirection = TIMER_COUNTER_UP;
    timer_initpara.period = 999;         // 1ms中断
    timer_initpara.clockdivision = TIMER_CKDIV_DIV1;
    timer_init(TIMER0, &timer_initpara);

    nvic_irq_enable(TIMER0_IRQn, 0, 0);
    timer_enable(TIMER0);
}
```

## 3. ESP32系列 (乐鑫)

### 3.1 ESP-IDF组件配置优化

```
# sdkconfig.defaults
CONFIG_ESPTOOLPY_FLASHSIZE="4MB"
CONFIG_ESPTOOLPY_FLASHFREQ="80m"
CONFIG_PARTITION_TABLE_TWO_OTA=y
CONFIG_ESPTOOLPY_COMPRESS_SPARSE_KERNELS=y

# WiFi省电
CONFIG_WIFI_PS_NONE=y  # 禁用WiFi省电以提高性能
# 或
CONFIG_WIFI_PS_MIN_MODEM=y  # 最小WiFi功耗

# FreeRTOS优化
CONFIG_FREERTOS_HZ=1000
CONFIG_FREERTOS_UNICORE=y  # 单核运行减少开销
CONFIG_FREERTOS_IDLE_TASK_STACKSIZE=2048
```

### 3.2 ESP32-S3优化

```c
// ESP32-S3双核优化
void esp32s3_dual_core_init(void) {
    xTaskCreatePinnedToCore(
        core_task,           // 任务函数
        "core_task",         // 任务名
        4096,                // 栈大小
        NULL,                // 参数
        10,                  // 优先级
        &core_task_handle,   // 句柄
        1                    // 核心ID (0或1)
    );
}

// ESP32-S3矢量指令
// 编译选项: -mvectorize-with-ffma-esp32

// ESP32-S3 RISC-V协处理器使用
void esp32s3_gdma_init(void) {
    gdma_handle_t gdma_handle;
    gdma_channel_alloc_config_t alloc_config = {
        .sram_reserve = false,
    };
    ESP_ERROR_CHECK(gdma_new_channel(&alloc_config, &gdma_handle));
}
```

### 3.3 ESP32-C3/C6 (RISC-V)

```c
// ESP32-C3 RISC-V优化
// 使用RISC-V特定优化选项
// -march=rv32imc -mabi=ilp32

// 中断配置
void esp32c3_intr_alloc(void) {
    intr_handle_t intr_handle;
    esp_intr_alloc(ETS_FROM_CPU_INTR0, 0, isr_handler, NULL, &intr_handle);
}

// RTC内存 - 用于深度睡眠数据保持
RTC_DATA_ATTR uint32_t sleep_count = 0;
RTC_DATA_ATTR uint8_t sensor_data[64];

void esp32c3_deep_sleep(void) {
    sleep_count++;
    esp_deep_sleep_start();
}
```

## 4. Nordic nRF系列

### 4.1 nRF52/nRF53优化

```c
// nRF52低功耗配置
void nrf52_power_config(void) {
    NRF_POWER->TASKS_LOWPWR = 1;
    NRF_POWER->EVENTS_SLEEPENTER = 0;
    NRF_POWER->EVENTS_SLEEPEXIT = 0;
}

// nRF52 EasyDMA优化
void nrf52_easydma_init(NRF_SPIM_Type *spim, uint8_t *tx_buf, uint8_t *rx_buf, uint16_t len) {
    spim->TXD.PTR = (uint32_t)tx_buf;
    spim->TXD.MAXCNT = len;
    spim->RXD.PTR = (uint32_t)rx_buf;
    spim->RXD.MAXCNT = len;

    spim->TASKS_START = 1;
}

// nRF53双核配置
void nrf53_network_core_init(void) {
    // 启动网络核心
    NRF_SPU->EXTERNALPOWER[0] = 0;
    NRF_RESET->NETWORK = 0;
    while(NRF_RESET->NETWORK == 0);
}
```

## 5. TI MSP430/TMS320系列

### 5.1 MSP430优化

```c
// MSP430低功耗模式
#pragma PERSISTENT
volatile uint16_t timer_count;

void msp430_lpm_init(void) {
    BCSCTL1 = CALBC1_1MHZ;
    DCOCTL = CALDCO_1MHZ;

    TACTL = TASSEL_2 + MC_1 + ID_0;  // SMCLK, up mode
    TACCR0 = 1000 - 1;               // 1ms @ 1MHz

    _BIS_SR(GIE + LPM0_bits);        // 进入低功耗模式
}

// MSP430 intrinsic优化
#pragma inline=forced
uint16_t msp430_fast_mult(uint16_t a, uint16_t b) {
    return __mpy(a, b);  // 使用硬件乘法器
}
```

### 5.2 TMS320F28377D优化

```c
// TMS320F28377D CLA (Control Law Accelerator)
#pragma DATA_SECTION(cla_task1, "ClaDataRam0");
float cla_task1_input[16];
float cla_task1_output[16];

// CLA任务配置
void cla_init(void) {
    Cla1Regs.MVECT1 = (uint16_t)(&Cla1Task1);
    Cla1Regs.MVECT2 = (uint16_t)(&Cla1Task2);

    Cla1Regs.MCTL.bit.HARLRESET = 1;
    Cla1Regs.MIER.all = 0x0001;

    Cla1ForceTask1();
}

// TMS320 DSP优化
#pragma DATA_ALIGN(buffer, 8);
float buffer[256];

void dsp_filter(void) {
    arm_fir_instance_f32 fir;
    arm_fir_init_f32(&fir, 64, coeffs, state, 256);
    arm_fir_f32(&fir, input, output, 256);
}
```

## 6. Renesas RA/RX系列

### 6.1 RA系列优化

```c
// Renesas RA低功耗
void ra_low_power_init(void) {
    R_System_Control_RAM->OPCCR_b.OPCM = 3;  // 低功耗模式
    R_BSP_LockCpu();
}

// RA FSP DMA配置
void ra_dma_init(dma_instance_t *dma) {
    R_DMAC_Open(&dma, &dma_cfg);
    R_DMAC_CfgAddr(&dma, (uint32_t)src, (uint32_t)dst, len);
    R_DMAC_Start(&dma);
}
```

### 6.2 RX系列优化

```c
// RX62N指令缓存
void rx62n_cache_enable(void) {
    ICU.DMISRCR.BIT.DMIST = 1;
    FLASH.ICCR.BYTE = 0x05;
}

// RX使用MACF/MULU指令优化乘除
#pragma inline_asm MulDiv32
static uint32_t MulDiv32(uint32_t a, uint32_t b, uint32_t c) {
    MULU a,b
    DIV0U
    DIVHU c
    DIVU c
    MVC Mach
}
```

## 7. Realtek Ameba系列

```c
// Realtek Ameba-D低功耗
void ameba_power_config(void) {
    // 配置为深度睡眠
    *(volatile uint32_t *)(0x40006000) = 0x1C;
    __asm__("wfi");
}

// Ameba WiFi低功耗
void ameba_wifi_ps_config(void) {
    wifi_ps_type_t mode = WIFI_PS_MIN_MODEM;
    rtw_set_ps_mode(mode);
}

// Ameba内存优化
void *ameba_malloc(size_t size) {
    if (size < 4096) {
        return rtw_malloc(size);
    }
    return pvPortMalloc(size);
}
```

## 8. 跨平台优化建议

### 8.1 统一时钟配置模板

```c
typedef struct {
    uint32_t sysclk;
    uint32_t hclk;
    uint32_t pclk1;
    uint32_t pclk2;
} clock_config_t;

const clock_config_t clock_configs[] = {
    #ifdef STM32F4
        {168000000, 168000000, 84000000, 168000000},
    #elif defined(ESP32)
        {240000000, 240000000, 240000000, 240000000},
    #elif defined(GD32F4)
        {168000000, 168000000, 84000000, 168000000},
    #endif
};
```

### 8.2 外设驱动抽象

```c
typedef struct uart_ops {
    void (*init)(uint32_t baudrate);
    void (*send)(uint8_t data);
    int  (*recv)(void);
    void (*irq_handler)(void);
} uart_ops_t;

#ifdef STM32F4
    static const uart_ops_t stm32_uart_ops = {
        .init = stm32_uart_init,
        .send = stm32_uart_send,
        .recv = stm32_uart_recv,
        .irq_handler = stm32_uart_irq,
    };
#elif defined(ESP32)
    static const uart_ops_t esp32_uart_ops = {
        .init = esp32_uart_init,
        .send = esp32_uart_send,
        .recv = esp32_uart_recv,
        .irq_handler = esp32_uart_irq,
    };
#endif
```
