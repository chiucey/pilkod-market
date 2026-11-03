---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402205b4294620dd697230aeddfff9631d7d92f7f49eec623444c653b63bf7a6bc64e02203f5a44d324af86ba2bc28bd8cc72fcaefb0a795660308456a6e1ab5b5d459839
    ReservedCode2: 304402201bcfd9f478e903c3dd0387c5c07e436939ed74c0b059a678118e27bb167052e20220103c3df4d1a40fd02b5844765d8801b34b9eab0f96ed63193dc23538e67bd7ec
---

# ArkUI 组件参考手册

## 基础组件

### Text 文本

```typescript
Text('Hello HarmonyOS')
  .fontSize(20)
  .fontColor('#333333')
  .fontWeight(FontWeight.Medium)
  .textAlign(TextAlign.Center)
  .maxLines(2)
  .textOverflow({ overflow: TextOverflow.Ellipsis })
  .decoration({ type: TextDecorationType.Underline, color: '#666666' })
```

### Button 按钮

```typescript
// 普通按钮
Button('Click Me')
  .width(200)
  .height(50)
  .fontSize(16)
  .type(ButtonType.Normal)
  .stateEffect(true)
  .onClick(() => {
    console.info('Button clicked')
  })

// 胶囊按钮
Button('Capsule', { type: ButtonType.Capsule })
  .backgroundColor('#007DFF')

// 圆形按钮
Button('', { type: ButtonType.Circle })
  .width(50)
  .height(50)
```

### Image 图片

```typescript
// 本地资源
Image($r('app.media.logo'))
  .width(200)
  .height(200)
  .borderRadius(10)

// 网络图片
Image('https://example.com/image.png')
  .width('100%')
  .objectFit(ImageFit.Contain)

// 像素图
Image(pixelMap)
  .width(100)
  .height(100)
```

## 容器组件

### Column 垂直布局

```typescript
Column({ space: 20 }) {
  Text('Item 1')
  Text('Item 2')
  Text('Item 3')
}
.width('100%')
.height('100%')
.alignItems(HorizontalAlign.Center)
.justifyContent(FlexAlign.SpaceEvenly)
.backgroundColor('#F5F5F5')
```

### Row 水平布局

```typescript
Row({ space: 10 }) {
  Image($r('app.media.icon'))
    .width(24)
    .height(24)
  Text('Title')
    .fontSize(16)
}
.width('100%')
.height(50)
.padding({ left: 16, right: 16 })
.alignItems(VerticalAlign.Center)
```

### Flex 弹性布局

```typescript
Flex({
  direction: FlexDirection.Row,
  justifyContent: FlexAlign.SpaceBetween,
  alignItems: ItemAlign.Center
}) {
  Text('Left')
  Text('Right')
}
.width('100%')
```

### Stack 层叠布局

```typescript
Stack() {
  Image($r('app.media.background'))
    .width('100%')
    .height('100%')

  Text('Overlay Text')
    .fontSize(24)
    .fontColor(Color.White)

  Button('Action')
    .position({ x: 20, y: 20 })
}
.width('100%')
.height(300)
```

### List 列表

```typescript
List({ space: 10, initialIndex: 0 }) {
  ForEach(this.items, (item: string, index: number) => {
    ListItem() {
      Text(`${index + 1}. ${item}`)
        .width('100%')
        .height(60)
        .textAlign(TextAlign.Center)
    }
    .backgroundColor('#FFFFFF')
    .borderRadius(8)
  }, (item: string) => item)
}
.width('100%')
.height('100%')
.listDirection(Axis.Vertical)
```

### Grid 网格

```typescript
Grid() {
  ForEach(this.gridItems, (item: string) => {
    GridItem() {
      Text(item)
        .fontSize(20)
    }
    .width('100%')
    .height(100)
    .backgroundColor('#E0E0E0')
  })
}
.width('100%')
.height(300)
.columnsTemplate('1fr 1fr 1fr')
.rowsTemplate('1fr 1fr')
.columnsGap(10)
.rowsGap(10)
```

### Tabs 标签页

```typescript
Tabs({ barPosition: BarPosition.End }) {
  TabContent() {
    Text('Home Content')
  }
  .tabBar('Home')

  TabContent() {
    Text('Profile Content')
  }
  .tabBar('Profile')

  TabContent() {
    Text('Settings Content')
  }
  .tabBar('Settings')
}
.width('100%')
.height('100%')
.barHeight(60)
.animationDuration(300)
```

## 导航组件

### Navigation 导航

```typescript
Navigation() {
  // 内容区
  List() {
    ForEach(this.routes, (route: string) => {
      ListItem() {
        Text(route)
          .onClick(() => {
            router.pushUrl({ url: `pages/${route}/${route}` })
          })
      }
    })
  }
}
.title('Main Title')
.titleMode(NavigationTitleMode.Mini)
.toolbarConfiguration(this.toolbarItems)
.mode(NavigationMode.Stack)
```

### Router 路由

```typescript
import router from '@ohos.router'

// 跳转到新页面
router.pushUrl({
  url: 'pages/Detail/Detail',
  params: { id: 123 }
})

// 返回上一页
router.back()

// 替换当前页面
router.replaceUrl({
  url: 'pages/Home/Home'
})
```

## 表单组件

### TextInput 单行输入

```typescript
TextInput({ placeholder: 'Enter text...' })
  .width(300)
  .height(40)
  .type(InputType.Normal)
  .onChange((value: string) => {
    this.inputText = value
  })
```

### TextArea 多行输入

```typescript
TextArea({ placeholder: 'Enter description...' })
  .width('100%')
  .height(120)
  .maxLength(200)
  .showCount(true)
```

### Checkbox 复选框

```typescript
CheckboxGroup({ name: 'group1' })
  .onChange((checkboxGroup: CheckboxGroupResult) => {
    console.log(JSON.stringify(checkboxGroup))
  })

Checkbox({ name: 'option1', group: 'group1' })
  .onChange((isChecked: boolean) => {
    console.log(`Option 1: ${isChecked}`)
  })
```

### Radio 单选框

```typescript
Radio({ value: 'option1', group: 'radioGroup' })
  .onChange((isSelected: boolean) => {
    if (isSelected) {
      console.log('Option 1 selected')
    }
  })

Radio({ value: 'option2', group: 'radioGroup' })
  .onChange((isSelected: boolean) => {
    if (isSelected) {
      console.log('Option 2 selected')
    }
  })
```

## 反馈组件

### Dialog 对话框

```typescript
@CustomDialog
struct CustomDialogExample {
  controller: CustomDialogController

  build() {
    Column() {
      Text('Custom Dialog')
        .fontSize(20)
      Button('Close')
        .onClick(() => {
          this.controller.close()
        })
    }
    .padding(20)
  }
}

// 使用
this.dialogController = new CustomDialogController({
  builder: CustomDialogExample(),
  alignment: DialogAlignment.Center
})
this.dialogController.open()
```

### ActionSheet 动作面板

```typescript
promptAction.showActionSheet({
  title: 'Choose Action',
  message: 'Select an option',
  buttons: [
    { text: 'Option 1', color: '#666666' },
    { text: 'Option 2', color: '#666666' },
    { text: 'Cancel', color: '#999999' }
  ],
  confirm: {
    value: 'Confirm',
    action: () => {
      console.info('Confirmed')
    }
  }
})
```

### LoadingProgress 加载指示器

```typescript
LoadingProgress()
  .width(60)
  .height(60)
  .color('#007DFF')
```

## 高级组件

### Scroll 滚动容器

```typescript
Scroll() {
  Column() {
    ForEach(this.items, (item: string) => {
      Text(item)
        .width('100%')
        .height(100)
        .margin({ bottom: 10 })
    })
  }
}
.width('100%')
.height('100%')
.scrollBar(BarState.On)
.edgeEffect(EdgeEffect.Spring)
```

### Swiper 轮播

```typescript
Swiper() {
  ForEach(this.images, (img: string) => {
    Image(img)
      .width('100%')
      .height('100%')
  })
}
.width('100%')
.height(200)
.autoPlay(true)
.interval(3000)
.indicator(true)
.loop(true)
```

### RelativeContainer 相对容器

```typescript
RelativeContainer() {
  Text('Header')
    .id('header')
    .alignRules({
      top: { anchor: '__container__', align: VerticalAlign.Top },
      start: { anchor: '__container__', align: HorizontalAlign.Start },
      end: { anchor: '__container__', align: HorizontalAlign.End }
    })
    .height(50)

  Text('Content')
    .id('content')
    .alignRules({
      top: { anchor: 'header', align: BottomAlign.Start },
      bottom: { anchor: 'footer', align: TopAlign.End },
      start: { anchor: '__container__', align: HorizontalAlign.Start },
      end: { anchor: '__container__', align: HorizontalAlign.End }
    })

  Text('Footer')
    .id('footer')
    .alignRules({
      bottom: { anchor: '__container__', align: VerticalAlign.Bottom },
      start: { anchor: '__container__', align: HorizontalAlign.Start },
      end: { anchor: '__container__', align: HorizontalAlign.End }
    })
    .height(50)
}
.width('100%')
.height('100%')
```
