# Linux嵌入式开发参考指南

## Buildroot构建配置

### .config模板

```makefile
#==========================================
# Buildroot 配置文件
#==========================================

# 目标架构
BR2_arm=y
BR2_cortex_a7=y
BR2_ARM_INSTRUCTIONS_THUMB2=y

# 工具链配置
BR2_TOOLCHAIN_BUILDROOT_VENDOR="embedded"
BR2_GCC_ENABLE_LTO=y
BR2_GCC_ENABLE_OPENMP=y

# 系统配置
BR2_SYSTEM_DHCP="eth0"
BR2_ROOTFS_OVERLAY="$(BR2_EXTERNAL)/board/$(BOARD)/rootfs-overlay"
BR2_ROOTFS_POST_BUILD_SCRIPT="$(BR2_EXTERNAL)/board/$(BOARD)/post-build.sh"
BR2_ROOTFS_POST_IMAGE_SCRIPT="$(BR2_EXTERNAL)/board/$(BOARD)/post-image.sh"

# Busybox配置
BR2_PACKAGE_BUSYBOX_CONFIG="$(BR2_EXTERNAL)/package/busybox/busybox.config"

# 内核配置
BR2_LINUX_KERNEL=y
BR2_LINUX_KERNEL_CUSTOM_TARBALL_LOCATION="file://$(TOPDIR)/../linux.tar.gz"
BR2_LINUX_KERNEL_DEFCONFIG="imx6ull"
BR2_LINUX_KERNEL_CONFIG_FRAGMENT_FILES="$(BR2_EXTERNAL)/board/$(BOARD)/kernel.config"

# Bootloader
BR2_TARGET_UBOOT=y
BR2_TARGET_UBOOT_CUSTOM_TARBALL="file://$(TOPDIR)/../u-boot.tar.gz"
BR2_TARGET_UBOOT_DEFCONFIG="imx6ull_14x14_evk"

# 网络相关
BR2_PACKAGE_IPTABLES=y
BR2_PACKAGE_OPENSSH=y
BR2_PACKAGE_WPA_SUPPLICANT=y

# 无线驱动
BR2_PACKAGE_LINUX_FIRMWARE=y
BR2_PACKAGE_LINUX_FIRMWARE_IMX=y
BR2_PACKAGE_RTL8723DS=y

# 调试工具
BR2_PACKAGE_GDB=y
BR2_PACKAGE_STRACE=y
BR2_PACKAGE_LTRACE=y
```

### 设备树覆盖配置

```dts
/dts-v1/;

/ {
    model = "Embedded Board";
    compatible = "vendor,imx6ull-board";

    /* 扩展默认配置 */
    chosen {
        stdout-path = &uart1;
    };

    /* RF模块设备树覆盖 */
    rf_module {
        compatible = "vendor,rf-module";
        status = "okay";

        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_rf>;

        spi-max-frequency = <10000000>;
        irq-gpios = <&gpio4 19 GPIO_ACTIVE_HIGH>;

        /* RF校准数据 */
        calibration-data = /memreserve/ 0x80000000 0x1000;
    };
};

&ecspi1 {
    status = "okay";
    pinctrl-0 = <&pinctrl_ecspi1>;

    flash@0 {
        compatible = "jedec,spi-nor";
        reg = <0>;
        spi-max-frequency = <40000000>;
        partitions {
            compatible = "fixed-partitions";
            #address-cells = <1>;
            #size-cells = <1>;
        };
    };
};

&uart1 {
    status = "okay";
};

&pinctrl_ecspi1 {
    fsl,pins = <
        MX6ULL_PAD_BOARD_MODE0__ECSPI1_MISO    0x10b0
        MX6ULL_PAD_BOARD_MODE1__ECSPI1_MOSI    0x10b0
        MX6ULL_PAD_BOARD_MODE2__ECSPI1_SCLK    0x10b0
        MX6ULL_PAD_BOARD_MODE3__GPIO4_IO03     0x10b0  /* CS */
    >;
};

&pinctrl_rf {
    fsl,pins = <
        MX6ULL_PAD_BOARD_RF_IRQ__GPIO4_IO19    0x17059
        MX6ULL_PAD_BOARD_RF_RST__GPIO4_IO20    0x17059
    >;
};
```

## Linux驱动开发

### 字符设备驱动框架

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/io.h>
#include <linux/uaccess.h>
#include <linux/of.h>
#include <linux/platform_device.h>

#define DEVICE_NAME     "rf_ctrl"
#define CLASS_NAME      "rf_ctrl_class"

static dev_t dev_num;
static struct cdev rf_cdev;
static struct class *rf_class;
static struct device *rf_device;

/* 硬件寄存器 */
struct rf_hw {
    void __iomem *base;
    uint32_t ctrl_reg;
    uint32_t status_reg;
    uint32_t tx_data;
    uint32_t rx_data;
} hw;

static int rf_open(struct inode *inode, struct file *filp) {
    pr_info("%s: opened\n", DEVICE_NAME);
    return 0;
}

static int rf_release(struct inode *inode, struct file *filp) {
    pr_info("%s: closed\n", DEVICE_NAME);
    return 0;
}

static ssize_t rf_read(struct file *filp, char __user *buf,
                       size_t count, loff_t *f_pos) {
    uint32_t data;

    if (count < sizeof(data))
        return -EINVAL;

    /* 从硬件读取 */
    data = ioread32(hw.base + hw.rx_data);

    if (copy_to_user(buf, &data, sizeof(data)))
        return -EFAULT;

    return sizeof(data);
}

static ssize_t rf_write(struct file *filp, const char __user *buf,
                        size_t count, loff_t *f_pos) {
    uint32_t data;

    if (count < sizeof(data))
        return -EINVAL;

    if (copy_from_user(&data, buf, sizeof(data)))
        return -EFAULT;

    /* 写入硬件 */
    iowrite32(data, hw.base + hw.tx_data);

    return sizeof(data);
}

static long rf_ioctl(struct file *filp, unsigned int cmd,
                     unsigned long arg) {
    int ret = 0;

    switch (cmd) {
    case RF_SET_FREQ:
        pr_info("Set frequency: %lu Hz\n", arg);
        iowrite32(arg, hw.base + hw.ctrl_reg);
        break;
    case RF_SET_GAIN:
        pr_info("Set gain: %lu dB\n", arg);
        break;
    case RF_START_TX:
        iowrite32(1, hw.base + hw.ctrl_reg);
        break;
    case RF_START_RX:
        iowrite32(2, hw.base + hw.ctrl_reg);
        break;
    default:
        ret = -EINVAL;
    }

    return ret;
}

static const struct file_operations rf_fops = {
    .owner          = THIS_MODULE,
    .open           = rf_open,
    .release        = rf_release,
    .read           = rf_read,
    .write          = rf_write,
    .unlocked_ioctl = rf_ioctl,
};

static int rf_probe(struct platform_device *pdev) {
    struct resource *res;

    pr_info("%s: probing\n", DEVICE_NAME);

    /* 获取内存资源 */
    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    hw.base = devm_ioremap_resource(&pdev->dev, res);
    if (IS_ERR(hw.base))
        return PTR_ERR(hw.base);

    /* 分配设备号 */
    alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);

    /* 初始化字符设备 */
    cdev_init(&rf_cdev, &rf_fops);
    rf_cdev.owner = THIS_MODULE;

    /* 添加设备 */
    cdev_add(&rf_cdev, dev_num, 1);

    /* 创建设备类 */
    rf_class = class_create(THIS_MODULE, CLASS_NAME);
    rf_device = device_create(rf_class, NULL, dev_num, NULL, DEVICE_NAME);

    pr_info("%s: device created, major=%d\n", DEVICE_NAME, MAJOR(dev_num));
    return 0;
}

static int rf_remove(struct platform_device *pdev) {
    device_destroy(rf_class, dev_num);
    class_destroy(rf_class);
    cdev_del(&rf_cdev);
    unregister_chrdev_region(dev_num, 1);

    pr_info("%s: removed\n", DEVICE_NAME);
    return 0;
}

static const struct of_device_id rf_of_match[] = {
    { .compatible = "vendor,rf-controller" },
    { }
};
MODULE_DEVICE_TABLE(of, rf_of_match);

static struct platform_driver rf_driver = {
    .probe  = rf_probe,
    .remove = rf_remove,
    .driver = {
        .name = DEVICE_NAME,
        .of_match_table = rf_of_match,
    }
};
module_platform_driver(rf_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Embedded Expert");
MODULE_DESCRIPTION("RF Controller Driver");
```

## 系统启动优化

### init脚本优化

```shell
#!/bin/sh
# 最小化启动脚本

mount -t proc none /proc
mount -t sysfs none /sys
mount -t tmpfs -o size=1M,mode=0755 tmpfs /run

# 创建设备节点
mdev -s

# 预热CPU调度器
for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo "performance" > $i 2>/dev/null
done

# 调整内核参数
echo 512 > /proc/sys/vm/min_free_kbytes
echo 0 > /proc/sys/kernel/randomize_va_space

# 启动应用
exec /usr/bin/myapp -d
```

## 性能调优

### 实时性配置

```shell
# 配置PREEMPT_RT
echo 1000 > /sys/kernel/debug/sched_wakeup_granularity_ns
echo 0 > /proc/sys/kernel/nmi_watchdog

# CPU隔离
echo 2-3 > /sys/devices/system/cpu/cpu2/core_ctl/isolate
echo 2-3 > /sys/devices/system/cpu/cpu3/core_ctl/isolate

# 中断亲和性
echo 2 > /proc/irq/$(cat /proc/interrupts | grep eth0 | awk '{print $1}' | tr -d ':')/smp_affinity
```
